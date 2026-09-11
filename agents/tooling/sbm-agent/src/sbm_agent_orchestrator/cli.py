from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .core import Orchestrator, OrchestratorConfig, UnixPrincipalProvider
from .errors import OrchestratorError
from .routing import AgentIdentity, HMACResponseAttestor, ManualChatAgentExecutionAdapter, PackageIdentityVerifier
from .util import atomic_write_json, normalize_brief, read_json, sha256_object, sortable_id, utc_now


def agents_root_from_package():
    return Path(__file__).resolve().parents[4]


class DurableCreateToken:
    def __init__(self, orchestrator, principal):
        self.orchestrator = orchestrator; self.principal = principal
        self.root = orchestrator.store.safe("client-requests", principal.replace(":", "_"))
        self.root.mkdir(parents=True, exist_ok=True)

    def obtain(self, brief):
        semantic_hash = sha256_object({"semantic_brief": normalize_brief(brief or "")})
        for path in self.root.glob("*.json"):
            record = read_json(path)
            if record.get("status") == "PENDING" and record.get("semantic_request_sha256") == semantic_hash:
                return record, path
        token = sortable_id("create_request_")
        record = {"create_request_token": token, "principal": self.principal, "semantic_request_sha256": semantic_hash, "status": "PENDING", "created_at": utc_now()}
        path = self.root / f"{token}.json"; atomic_write_json(path, record)
        return record, path


def parser():
    root = argparse.ArgumentParser(prog="sbm-agent")
    commands = root.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create"); create.add_argument("semantic_brief", nargs="?"); create.add_argument("--intent-brief"); create.add_argument("--intake-adapter")
    intake = commands.add_parser("intake"); intake.add_argument("execution_id"); intake.add_argument("semantic_response")
    imported = commands.add_parser("import-response"); imported.add_argument("execution_id"); imported.add_argument("response_file")
    approve = commands.add_parser("approve"); approve.add_argument("execution_id")
    status = commands.add_parser("status"); status.add_argument("execution_id", nargs="?")
    resume = commands.add_parser("resume"); resume.add_argument("execution_id")
    return root


def build_orchestrator(agents_root=None):
    config = OrchestratorConfig(Path(agents_root or agents_root_from_package()))
    provider = UnixPrincipalProvider(config.agents_root / "tooling/sbm-agent/config/authenticated-principals.json", config.agents_root)
    routing = read_json(config.agents_root / "tooling/sbm-agent/config/agent-routing.json")
    verifier = PackageIdentityVerifier(config.agents_root)
    key_value = os.environ.get("SBM_AGENT_RESPONSE_ATTESTATION_KEY", "")
    try: attestor = HMACResponseAttestor(bytes.fromhex(key_value)) if key_value else None
    except ValueError as exc: raise OrchestratorError("ATTESTATION_KEY_INVALID", "SBM_AGENT_RESPONSE_ATTESTATION_KEY must be hexadecimal") from exc
    def adapter(name):
        value = routing[name]; identity = AgentIdentity(value["agent_id"], value["agent_version"], value["path"], value["sha256"], tuple(value.get("capabilities", []))); return ManualChatAgentExecutionAdapter(verifier, identity, name, attestor)
    gepetto, darwin, noe = adapter("Gepetto"), adapter("Darwin"), adapter("Noe")
    return Orchestrator(config, principal_provider=provider, gepetto_adapter=gepetto, architecture_adapter=darwin, darwin_review_adapter=darwin, noe_review_adapter=noe, auto_route_agents=True)


def load_intent_brief(value):
    if not value: raise OrchestratorError("INTENT_BRIEF_INPUT_INVALID", "--intent-brief requires a JSON file path or JSON object")
    path = Path(value)
    try:
        payload = path.read_text(encoding="utf-8") if path.is_file() else value
        parsed = json.loads(payload)
    except (OSError, json.JSONDecodeError) as exc:
        raise OrchestratorError("INTENT_BRIEF_INPUT_INVALID", "--intent-brief must be a readable JSON file or valid JSON object") from exc
    if not isinstance(parsed, dict): raise OrchestratorError("INTENT_BRIEF_INPUT_INVALID", "--intent-brief must contain a JSON object")
    return parsed


def main(argv=None, orchestrator=None):
    args = parser().parse_args(argv)
    orch = orchestrator or build_orchestrator()
    try:
        if args.command == "create":
            principal = orch.principal_provider.current()
            if args.intent_brief and args.semantic_brief: raise OrchestratorError("CREATE_CONTRACT_INVALID", "semantic_brief and --intent-brief are mutually exclusive")
            if bool(args.intent_brief) != bool(args.intake_adapter): raise OrchestratorError("CREATE_CONTRACT_INVALID", "--intent-brief and --intake-adapter must be supplied together")
            if args.intent_brief:
                intent = load_intent_brief(args.intent_brief)
                durable = DurableCreateToken(orch, principal.principal_id)
                record, path = durable.obtain(json.dumps({"intent_brief": intent, "intake_adapter": args.intake_adapter}, sort_keys=True))
                state = orch.create_from_intent_brief(intent, intake_mode=args.intake_adapter, principal=principal.principal_id, idempotency_key=record["create_request_token"])
                record.update({"status": "ACKNOWLEDGED", "execution_id": state["execution_id"], "acknowledged_at": utc_now()}); atomic_write_json(path, record)
                print(json.dumps({"execution_id": state["execution_id"], "state": state["state"], "pending_gate": state.get("pending_gate")}, indent=2)); return 0
            durable = DurableCreateToken(orch, principal.principal_id)
            record, path = durable.obtain(args.semantic_brief)
            state = orch.create(args.semantic_brief, principal=principal.principal_id, idempotency_key=record["create_request_token"])
            record.update({"status": "ACKNOWLEDGED", "execution_id": state["execution_id"], "acknowledged_at": utc_now()}); atomic_write_json(path, record)
            print(json.dumps({"execution_id": state["execution_id"], "state": state["state"], "question": state.get("pending_question")}, indent=2)); return 0
        if args.command == "intake":
            state = orch.submit_intent(args.execution_id, args.semantic_response)
            print(json.dumps({"execution_id": state["execution_id"], "state": state["state"], "question": state.get("pending_question")}, indent=2)); return 0
        if args.command == "import-response":
            envelope = json.loads(Path(args.response_file).read_text(encoding="utf-8")); state = orch.import_agent_response(args.execution_id, envelope)
            print(json.dumps({"execution_id": state["execution_id"], "state": state["state"], "pending_gate": state.get("pending_gate")}, indent=2)); return 0
        if args.command == "approve":
            print(json.dumps(orch.approval_view(args.execution_id), indent=2, sort_keys=True))
            state = orch.approve(args.execution_id); print(json.dumps({"execution_id": state["execution_id"], "state": state["state"]}, indent=2)); return 0
        if args.command == "status":
            print(json.dumps(orch.status(args.execution_id), indent=2, sort_keys=True)); return 0
        if args.command == "resume":
            state = orch.resume(args.execution_id); print(json.dumps({"execution_id": state["execution_id"], "state": state["state"]}, indent=2)); return 0
    except OrchestratorError as exc:
        print(str(exc), file=sys.stderr); return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
