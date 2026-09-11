from __future__ import annotations

from pathlib import Path

from .errors import OrchestratorError
from .util import read_json, sha256_file, sha256_object, utc_now


class CreationProfileResolver:
    def __init__(self, agents_root, profile_root):
        self.agents_root = Path(agents_root)
        self.profile_root = Path(profile_root)

    def resolve(self):
        activation = read_json(self.profile_root / "activation.json")
        if not activation:
            raise OrchestratorError("NO_ACTIVE_PROFILE", "Creation profile activation is missing")
        active = activation.get("active_profiles", [])
        if len(active) != 1:
            raise OrchestratorError("ACTIVE_PROFILE_CONFLICT", "Exactly one active creation profile is required", details={"count": len(active)})
        entry = active[0]
        if entry["profile_id"] in set(activation.get("revoked_profiles", [])) or entry.get("revoked"):
            raise OrchestratorError("PROFILE_REVOKED", "Active creation profile is revoked")
        path = self.profile_root / entry["path"]
        if not path.is_file():
            raise OrchestratorError("PROFILE_MISSING", "Active creation profile is missing")
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            raise OrchestratorError("PROFILE_HASH_MISMATCH", "Creation profile hash mismatch", details={"expected": entry["sha256"], "actual": actual})
        profile = read_json(path)
        if profile.get("profile_id") != entry["profile_id"] or profile.get("status") != "PUBLISHED":
            raise OrchestratorError("PROFILE_INVALID", "Creation profile identity/status mismatch")
        self.verify_bindings(profile)
        return profile, actual

    def verify_bindings(self, profile):
        bindings = profile["bindings"]
        physical = {name: bindings[name] for name in ("standard", "governance", "generator", "template", "factory")}
        physical.update({f"schema:{name}": binding for name, binding in bindings["schemas"].items()})
        for name, binding in physical.items():
            path = self.agents_root / binding["path"]
            if not path.is_file():
                raise OrchestratorError("BINDING_MISSING", f"{name} artifact is missing")
            actual = sha256_file(path)
            if actual != binding["sha256"]:
                raise OrchestratorError("BINDING_HASH_MISMATCH", f"{name} binding hash mismatch", details={"expected": binding["sha256"], "actual": actual})


class CreationContextResolver:
    VERSION = "1.0.0"

    def __init__(self, store, profiles):
        self.store = store
        self.profiles = profiles

    def _canonical_document(self, name, default):
        path = self.store.state / name
        value = read_json(path)
        if value is None:
            raise OrchestratorError("CANONICAL_STATE_MISSING", f"Canonical {name} is missing; explicit recovery is required")
        return value, sha256_object(value)

    def resolve(self, execution_id):
        profile, profile_hash = self.profiles.resolve()
        registry, registry_hash = self._canonical_document(
            "final-agent-registry.json", {"revision": 0, "agents": []}
        )
        ledger, ledger_hash = self._canonical_document(
            "identity-reservations.json", {"revision": 0, "next_sequence": 1, "reservations": []}
        )
        snapshot = {
            "execution_id": execution_id,
            "creation_profile": {"profile_id": profile["profile_id"], "sha256": profile_hash},
            "registry": {"revision": registry["revision"], "sha256": registry_hash},
            "reservation_ledger": {"revision": ledger["revision"], "sha256": ledger_hash},
            "registry_document": registry,
            "reservation_ledger_document": ledger,
            "standard": profile["bindings"]["standard"],
            "governance": profile["bindings"]["governance"],
            "generator": profile["bindings"]["generator"],
            "template": profile["bindings"]["template"],
            "factory": profile["bindings"]["factory"],
            "schemas": profile["bindings"]["schemas"],
            "field_source_policy": profile["field_source_policy"],
            "resolver_version": self.VERSION,
            "timestamp": utc_now(),
        }
        snapshot["snapshot_sha256"] = sha256_object(snapshot)
        fingerprint = self.fingerprint(profile_hash, registry, registry_hash, ledger, ledger_hash)
        return profile, snapshot, fingerprint

    @staticmethod
    def fingerprint(profile_hash, registry, registry_hash, ledger, ledger_hash, relevant_agent_ids=None, agents_root=None):
        relevant_agent_ids = set(relevant_agent_ids or [])
        relevant = []
        for agent in registry.get("agents", []):
            if agent.get("agent_id") not in relevant_agent_ids:
                continue
            bound = dict(agent)
            metadata_path = agent.get("metadata_path")
            if metadata_path and agents_root:
                path = Path(agents_root) / metadata_path
                bound["resolved_metadata_sha256"] = sha256_file(path) if path.is_file() else "MISSING"
            relevant.append(bound)
        data = {
            "creation_profile_sha256": profile_hash,
            "registry_revision": registry.get("revision", 0),
            "registry_sha256": registry_hash,
            "reservation_ledger_revision": ledger.get("revision", 0),
            "reservation_ledger_sha256": ledger_hash,
            "relevant_final_agents_sha256": sha256_object(relevant),
        }
        data["fingerprint_sha256"] = sha256_object(data)
        return data

    @staticmethod
    def intake_view(profile, snapshot, unresolved=None, relevant_agents=None):
        return {
            "unresolved_human_semantic_requirements": unresolved or [],
            "naming_rules": profile["naming_rules"],
            "material_constraints": profile["canonical_defaults"]["material_constraints"],
            "relevant_relationships": profile["canonical_defaults"]["relationships"],
            "relevant_agents": relevant_agents or [],
            "field_source_policy": profile["field_source_policy"],
            "defaults": profile["canonical_defaults"],
            "human_authority": "sbm-admin",
            "provenance": {
                "creation_profile_sha256": snapshot["creation_profile"]["sha256"],
                "snapshot_sha256": snapshot["snapshot_sha256"],
                "resolver_version": snapshot["resolver_version"],
            },
        }


def classify_freshness(old, new, *, reservation_conflict=False):
    if reservation_conflict:
        return "RESERVATION_CONFLICT"
    if old["creation_profile_sha256"] != new["creation_profile_sha256"]:
        return "CONTRACT_DELTA"
    if old["relevant_final_agents_sha256"] != new["relevant_final_agents_sha256"]:
        return "ECOSYSTEM_RELEVANT_DELTA"
    if old["registry_sha256"] != new["registry_sha256"]:
        return "ECOSYSTEM_IRRELEVANT_DELTA"
    if old["reservation_ledger_sha256"] != new["reservation_ledger_sha256"]:
        return "ECOSYSTEM_IRRELEVANT_DELTA"
    return "NO_RELEVANT_DELTA"
