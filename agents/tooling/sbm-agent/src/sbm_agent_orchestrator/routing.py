from __future__ import annotations

import copy
import hashlib
import hmac
import json
import secrets
import zipfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from .errors import OrchestratorError
from .util import atomic_write_json, canonical_json, sha256_file, sha256_object, sortable_id, utc_now


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    agent_version: str
    package_path: str
    package_sha256: str
    capabilities: tuple[str, ...] = ()


class PackageIdentityVerifier:
    """Verifies the physical package and its SHA-bound routed capability binding."""
    def __init__(self, agents_root): self.agents_root = Path(agents_root).resolve()

    def verify(self, identity, capability=None):
        path = (self.agents_root / identity.package_path).resolve()
        try: path.relative_to(self.agents_root)
        except ValueError as exc: raise OrchestratorError("AGENT_PACKAGE_PATH_INVALID", "Agent package escapes agents root") from exc
        if not path.is_file() or sha256_file(path) != identity.package_sha256:
            raise OrchestratorError("AGENT_PACKAGE_SHA_MISMATCH", f"Package SHA mismatch for {identity.agent_id}")
        actual_id, actual_version = self._physical_identity(path)
        if actual_id.casefold() != identity.agent_id.casefold() or str(actual_version) != str(identity.agent_version):
            raise OrchestratorError("AGENT_PACKAGE_IDENTITY_MISMATCH", "Agent ID/version does not match package contents")
        capabilities = tuple(identity.capabilities)
        if capability and capability not in capabilities:
            raise OrchestratorError("AGENT_CAPABILITY_UNSUPPORTED", f"{identity.agent_id} package binding does not support {capability}")
        return {"agent_id": actual_id, "agent_version": str(actual_version), "package_path": identity.package_path, "package_sha256": identity.package_sha256, "capabilities": list(capabilities)}

    @staticmethod
    def _physical_identity(path):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist(); manifest = next((n for n in names if n.endswith("/manifest.json")), None)
            if manifest:
                value = json.loads(archive.read(manifest)); return value["id"], value["version"]
            definition = next((n for n in names if n.endswith("/AGENT_DEFINITION.yaml")), None)
            if definition:
                value = yaml.safe_load(archive.read(definition)); return value["agent_id"], value["agent_version"]
        raise OrchestratorError("AGENT_PACKAGE_IDENTITY_MISSING", "Agent package has no canonical identity document")


class HMACResponseAttestor:
    """Trusted external provenance; public response metadata is never authentication."""
    METHOD = "HMAC-SHA256/v1"
    def __init__(self, key):
        if not isinstance(key, (bytes, bytearray)) or len(key) < 32: raise OrchestratorError("ATTESTATION_KEY_INVALID", "Trusted response attestation key must contain at least 32 bytes")
        self._key = bytes(key); self._issued = set(); self._consumed = set()
    def issue(self):
        nonce = secrets.token_hex(32); self._issued.add(nonce); return nonce
    def sign(self, envelope, nonce):
        unsigned = copy.deepcopy(envelope); unsigned.pop("provenance", None)
        return hmac.new(self._key, canonical_json({"nonce": nonce, "envelope": unsigned}), hashlib.sha256).hexdigest()
    def provenance(self, envelope, nonce): return {"method": self.METHOD, "nonce": nonce, "signature": self.sign(envelope, nonce)}
    def verify_once(self, envelope, expected_nonce):
        provenance = envelope.get("provenance")
        if not isinstance(provenance, dict): raise OrchestratorError("AGENT_RESPONSE_PROVENANCE_MISSING", "External response requires trusted provenance")
        nonce = provenance.get("nonce")
        if provenance.get("method") != self.METHOD or (expected_nonce is not None and nonce != expected_nonce): raise OrchestratorError("AGENT_RESPONSE_PROVENANCE_INVALID", "External response provenance is not trusted")
        if nonce in self._consumed: raise OrchestratorError("AGENT_RESPONSE_REPLAY", "External response provenance was already consumed")
        if not hmac.compare_digest(str(provenance.get("signature", "")), self.sign(envelope, nonce)): raise OrchestratorError("AGENT_RESPONSE_PROVENANCE_INVALID", "External response provenance signature is invalid")
        self._consumed.add(nonce)


@dataclass(frozen=True)
class RoutedAgentResponse:
    principal_id: str
    provider: str
    authenticated: bool
    payload: dict


class AgentExecutionAdapter:
    def request_intake(self, request, execution_dir): raise NotImplementedError
    def request_architecture(self, request, execution_dir): raise NotImplementedError
    def request_review(self, request, execution_dir): raise NotImplementedError
    def import_response(self, envelope, expected_request_sha256): raise NotImplementedError


class ManualChatAgentExecutionAdapter(AgentExecutionAdapter):
    """Fail-closed MANUAL_CHAT adapter with capability and detached provenance checks."""
    CONTRACTS = {"INTAKE": ("GEPETTO_INTAKE_REQUEST/v1", "STRUCTURED_INTENT_UPDATE/v1"), "ARCHITECTURE": ("DARWIN_ARCHITECTURE_REQUEST/v1", "SPEC_DECISIONS/v1"), "REVIEW": ("AGENT_REVIEW_REQUEST/v1", "AGENT_REVIEW_RESPONSE/v1")}
    def __init__(self, verifier, identity, principal_id=None, attestor=None):
        self.verifier = verifier; self.identity = identity; self.principal_id = principal_id or identity.agent_id; self.attestor = attestor; self._pending_nonces = {}
    def _request(self, kind, request, execution_dir):
        request_contract, response_contract = self.CONTRACTS[kind]
        if request.get("contract") != request_contract: raise OrchestratorError("AGENT_REQUEST_CONTRACT_MISMATCH", f"Expected {request_contract}")
        verified = self.verifier.verify(self.identity, request_contract)
        if response_contract not in verified["capabilities"]: raise OrchestratorError("AGENT_CAPABILITY_UNSUPPORTED", f"{self.identity.agent_id} does not support {response_contract}")
        if self.attestor is None: raise OrchestratorError("AGENT_PROVENANCE_NOT_CONFIGURED", "MANUAL_CHAT requires a trusted response attestor")
        request_sha = sha256_object(request); nonce = self.attestor.issue(); self._pending_nonces[request_sha] = nonce
        package = {"contract": "MANUAL_CHAT_AGENT_REQUEST/v2", "request_id": sortable_id("agent_request_"), "request_kind": kind, "expected_agent": verified, "request_contract": request_contract, "response_contract": response_contract, "request": request, "request_sha256": request_sha, "attestation": {"method": self.attestor.METHOD, "nonce": nonce}, "created_at": utc_now(), "state": "WAITING_EXTERNAL_RESPONSE"}
        path = Path(execution_dir) / "routing" / f"{package['request_id']}.json"; atomic_write_json(path, package)
        return {"waiting": True, "request_path": str(path), "request_sha256": request_sha, "request_kind": kind}
    def request_intake(self, request, execution_dir): return self._request("INTAKE", request, execution_dir)
    def request_architecture(self, request, execution_dir): return self._request("ARCHITECTURE", request, execution_dir)
    def request_review(self, request, execution_dir): return self._request("REVIEW", request, execution_dir)
    def import_response(self, envelope, expected_request_sha256):
        kind = envelope.get("response_kind")
        if kind not in self.CONTRACTS: raise OrchestratorError("AGENT_RESPONSE_SCHEMA_INVALID", "External agent response kind is invalid")
        request_contract, response_contract = self.CONTRACTS[kind]; verified = self.verifier.verify(self.identity, request_contract)
        if response_contract not in verified["capabilities"]: raise OrchestratorError("AGENT_CAPABILITY_UNSUPPORTED", f"{self.identity.agent_id} does not support {response_contract}")
        if envelope.get("agent_id", "").casefold() != verified["agent_id"].casefold() or str(envelope.get("agent_version")) != verified["agent_version"]: raise OrchestratorError("WRONG_AGENT_IDENTITY", "External response agent identity mismatch")
        if envelope.get("package_sha256") != verified["package_sha256"]: raise OrchestratorError("WRONG_AGENT_PACKAGE_SHA", "External response package SHA mismatch")
        if envelope.get("request_sha256") != expected_request_sha256: raise OrchestratorError("WRONG_AGENT_REQUEST_SHA", "External response request SHA mismatch")
        if envelope.get("response_contract") != response_contract: raise OrchestratorError("AGENT_RESPONSE_CONTRACT_MISMATCH", f"Expected {response_contract}")
        payload = envelope.get("response")
        valid = (kind == "INTAKE" and isinstance(payload, dict) and payload.get("contract") == response_contract and isinstance(payload.get("fields"), dict)) or (kind == "ARCHITECTURE" and isinstance(payload, dict) and payload.get("contract") == response_contract and payload.get("status") in {"RESOLVED", "HUMAN_DECISION_REQUIRED"}) or (kind == "REVIEW" and isinstance(payload, dict) and payload.get("contract") == response_contract and payload.get("verdict") in {"PASS", "FAIL"} and isinstance(payload.get("subject_hashes"), dict))
        if not valid: raise OrchestratorError("AGENT_RESPONSE_SCHEMA_INVALID", "External agent response schema is invalid")
        if self.attestor is None: raise OrchestratorError("AGENT_PROVENANCE_NOT_CONFIGURED", "MANUAL_CHAT requires a trusted response attestor")
        self.attestor.verify_once(envelope, self._pending_nonces.get(expected_request_sha256))
        return RoutedAgentResponse(self.principal_id, f"manual-chat-attested:{verified['package_sha256']}", True, payload)
