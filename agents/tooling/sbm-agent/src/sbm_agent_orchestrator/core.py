from __future__ import annotations

import getpass
import base64
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .adapters import ContainerGeneratorAdapter, FactoryAdapter, IndependentQARunner, proposal_input
from .contracts import ApprovalWriter, DarwinSubmissionContract, ExternalIntentBriefContract, IntentAccumulator, ReviewSubmissionContract, SpecCompiler, read_yaml
from .errors import OrchestratorError
from .identity import IdentityAllocator
from .profiles import CreationContextResolver, CreationProfileResolver, classify_freshness
from .promotion import PromotionManager
from .routing import ManualChatAgentExecutionAdapter, RoutedAgentResponse
from .storage import RuntimeStore
from .util import atomic_write_json, normalize_brief, read_json, sha256_file, sha256_object, sortable_id, utc_now

STATES = {"SYNCING_CONTEXT", "WAITING_FOR_CONTEXT", "CAPTURING_INTENT", "PREBUILD", "STALE_CREATION_CONTEXT", "WAITING_BUILD_APPROVAL", "BUILDING", "FINAL_REVIEW", "WAITING_PROMOTION_APPROVAL", "PROMOTING", "PROMOTED", "BLOCKED", "CANCELLED"}
INITIAL_QUESTION = "¿Qué agente quieres crear? Dime cómo quieres llamarlo y, en tus palabras, qué quieres que haga o qué resultado quieres que consiga. Si hay algún límite, relación o estilo que para ti sea especialmente importante, inclúyelo."

@dataclass(frozen=True)
class AuthenticatedPrincipal:
    principal_id: str
    provider: str
    authenticated: bool = True
    session_reference: str = "unspecified"
    authenticated_at: str = ""

class PrincipalProvider:
    def current(self): raise NotImplementedError

class StaticPrincipalProvider(PrincipalProvider):
    def __init__(self, principal_id): self.principal_id = principal_id
    def current(self): return AuthenticatedPrincipal(self.principal_id, "trusted-static-provider", True, f"static-session:{self.principal_id}", utc_now())

class UnixPrincipalProvider(PrincipalProvider):
    def __init__(self, mapping_path, authority_root=None): self.mapping_path = Path(mapping_path); self.authority_root = Path(authority_root or mapping_path).resolve()
    def current(self):
        mapping = read_json(self.mapping_path, {"unix_users": {}}); username = getpass.getuser()
        principal = mapping.get("unix_users", {}).get(username)
        if principal is None and mapping.get("repository_owner_is_sbm_admin") and self.authority_root.stat().st_uid == __import__("os").getuid(): principal = "sbm-admin"
        return AuthenticatedPrincipal(principal or f"local:{username}", f"unix-account-mapping:{sha256_object(mapping)}", True, f"unix-session:uid:{__import__('os').getuid()}", utc_now())

@dataclass
class OrchestratorConfig:
    agents_root: Path
    runtime_root: Path | None = None
    profile_root: Path | None = None
    final_root: Path | None = None
    def __post_init__(self):
        self.agents_root = Path(self.agents_root).resolve()
        self.runtime_root = Path(self.runtime_root or self.agents_root / "runtime/sbm-agent")
        self.profile_root = Path(self.profile_root or self.agents_root / "tooling/sbm-agent/config/profiles")
        self.final_root = Path(self.final_root or self.agents_root / "final")

class Orchestrator:
    def __init__(self, config, *, generator=None, factory=None, qa=None, intake=None, principal_provider=None, gepetto_adapter=None, architecture_adapter=None, darwin_review_adapter=None, noe_review_adapter=None, auto_route_agents=False):
        self.config = config; self.store = RuntimeStore(config.agents_root, config.runtime_root)
        self.profiles = CreationProfileResolver(config.agents_root, config.profile_root); self.context = CreationContextResolver(self.store, self.profiles)
        self.identity = IdentityAllocator(self.store); self.generator = generator or ContainerGeneratorAdapter(config.agents_root)
        self.factory = factory or FactoryAdapter(config.agents_root); self.qa = qa or IndependentQARunner(); self.intake = intake or IntentAccumulator()
        self.compiler = SpecCompiler(); self.darwin_submissions = DarwinSubmissionContract(); self.review_submissions = ReviewSubmissionContract(); self.approvals = ApprovalWriter()
        self.external_intent_briefs = ExternalIntentBriefContract()
        self.promotion = PromotionManager(self.store, config.final_root)
        self.gepetto_adapter = gepetto_adapter; self.architecture_adapter = architecture_adapter; self.darwin_review_adapter = darwin_review_adapter; self.noe_review_adapter = noe_review_adapter; self.auto_route_agents = auto_route_agents
        self.principal_provider = principal_provider or UnixPrincipalProvider(config.agents_root / "tooling/sbm-agent/config/authenticated-principals.json", config.agents_root)
        self.idempotency_path = self.store.state / "create-idempotency.json"

    def _event(self, state, action, **kwargs): return self.store.append_event(state["execution_id"], kwargs.pop("actor", "orchestrator"), action, **kwargs)
    def _principal(self, expected=None):
        principal = self.principal_provider.current()
        if not principal.authenticated or (expected and principal.principal_id != expected): raise OrchestratorError("UNAUTHORIZED_SUBMISSION", f"This operation requires authenticated {expected or 'principal'}")
        return principal
    def _idempotent_execution(self, principal, key, semantic_hash):
        with self.store.lock("create-idempotency"):
            index = read_json(self.idempotency_path, {"entries": []}); match = next((e for e in index["entries"] if e["principal"] == principal and e["idempotency_key"] == key), None)
            if match:
                if match["semantic_request_sha256"] != semantic_hash: raise OrchestratorError("IDEMPOTENCY_CONFLICT", "Idempotency key was already used with a different semantic request")
                return match["execution_id"], False
            execution_id = sortable_id("exec_"); index["entries"].append({"principal": principal, "idempotency_key": key, "semantic_request_sha256": semantic_hash, "execution_id": execution_id, "created_at": utc_now()}); atomic_write_json(self.idempotency_path, index)
            return execution_id, True

    def create(self, semantic_brief=None, *, principal, idempotency_key):
        if not principal or not idempotency_key: raise OrchestratorError("CREATE_CONTRACT_INVALID", "Authenticated principal and idempotency key are required")
        brief = normalize_brief(semantic_brief or ""); semantic_hash = sha256_object({"semantic_brief": brief}); execution_id, fresh = self._idempotent_execution(principal, idempotency_key, semantic_hash)
        if not fresh: return self.store.load_execution(execution_id)
        state = {"execution_id": execution_id, "state": "SYNCING_CONTEXT", "principal": principal, "idempotency_key": idempotency_key, "semantic_request_sha256": semantic_hash, "created_at": utc_now(), "updated_at": utc_now(), "relevant_agent_ids": []}
        self.store.create_execution(state); self._event(state, "CREATE_ACCEPTED", actor=principal, inputs={"semantic_request": semantic_hash})
        try: return self._start_intake(state, brief)
        except OrchestratorError as exc:
            state = self.store.load_execution(execution_id); target = "WAITING_FOR_CONTEXT" if exc.code in {"CONTEXT_REQUIRED", "CONTEXT_INVALID"} else "BLOCKED"; self.store.transition(state, target, details={"error": exc.code}); state["last_error"] = {"code": exc.code, "message": str(exc)}; self.store.save_execution(state); raise

    def create_from_intent_brief(self, intent_brief, *, intake_mode, principal, idempotency_key):
        if not principal or not idempotency_key: raise OrchestratorError("CREATE_CONTRACT_INVALID", "Authenticated principal and idempotency key are required")
        semantic_hash = sha256_object({"intent_brief": intent_brief, "intake_mode": intake_mode}); execution_id, fresh = self._idempotent_execution(principal, idempotency_key, semantic_hash)
        if not fresh:
            existing = self.store.load_execution(execution_id)
            if existing.get("last_error"):
                error = existing["last_error"]
                raise OrchestratorError(error["code"], "Existing external-intake execution is blocked by its recorded validation or pipeline error", details={"execution_id": execution_id})
            return existing
        state = {"execution_id": execution_id, "state": "SYNCING_CONTEXT", "principal": principal, "idempotency_key": idempotency_key, "semantic_request_sha256": semantic_hash, "created_at": utc_now(), "updated_at": utc_now(), "relevant_agent_ids": []}
        self.store.create_execution(state); self._event(state, "EXTERNAL_CREATE_ACCEPTED", actor=principal, inputs={"semantic_request": semantic_hash})
        try:
            intent = self.external_intent_briefs.accept(intent_brief, intake_mode=intake_mode, principal=principal)
            self._prepare_intake_context(state)
            intent_path, intent_hash = self.store.write_immutable(execution_id, "intake/INTENT_BRIEF.json", intent)
            provenance = intent["provenance"]
            state.update({"intent_revision": 1, "intent_brief_path": str(intent_path), "intent_brief_sha256": intent_hash, "semantic_source": provenance["semantic_source"], "intake_adapter": provenance["intake_adapter"], "intake_mode": provenance["intake_mode"], "intake_provenance": provenance, "unresolved_human_semantic_requirements": []})
            self.store.save_execution(state)
            self._event(state, "EXTERNAL_INTENT_BRIEF_FROZEN", actor=principal, inputs={"intent_brief": intent_hash}, details={"semantic_source": provenance["semantic_source"], "intake_adapter": provenance["intake_adapter"], "intake_mode": provenance["intake_mode"]})
            return self._continue_from_intent(state, intent, intent_path, intent_hash)
        except OrchestratorError as exc:
            state = self.store.load_execution(execution_id); target = "WAITING_FOR_CONTEXT" if exc.code in {"CONTEXT_REQUIRED", "CONTEXT_INVALID"} else "BLOCKED"; self.store.transition(state, target, details={"error": exc.code}); state["last_error"] = {"code": exc.code, "message": str(exc)}; self.store.save_execution(state); raise

    def _prepare_intake_context(self, state):
        execution_id = state["execution_id"]; profile, snapshot, fingerprint = self.context.resolve(execution_id)
        snapshot_path, _ = self.store.write_immutable(execution_id, "snapshots/creation-context-001.json", snapshot)
        registry = read_json(self.store.state / "final-agent-registry.json", {"agents": []}); view = self.context.intake_view(profile, snapshot, relevant_agents=registry.get("agents", [])); view_path, view_hash = self.store.write_immutable(execution_id, "intake/INTAKE_STATE_VIEW.json", view)
        state.update({"creation_snapshot_path": str(snapshot_path), "creation_snapshot_sha256": snapshot["snapshot_sha256"], "intake_creation_fingerprint": fingerprint, "creation_fingerprint": fingerprint, "intake_state_view_path": str(view_path), "intake_state_view_sha256": view_hash}); self.store.transition(state, "CAPTURING_INTENT")

    def _start_intake(self, state, brief):
        self._prepare_intake_context(state)
        if not brief:
            state["pending_question"] = INITIAL_QUESTION; state["unresolved_human_semantic_requirements"] = [{"field": "semantic_brief", "question": INITIAL_QUESTION}]; self.store.save_execution(state); return state
        return self._request_intake(state, brief)

    def submit_intent(self, execution_id, semantic_response):
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id)
            if state["state"] != "CAPTURING_INTENT": raise OrchestratorError("INTAKE_NOT_EXPECTED", "Execution is not waiting for semantic intake")
            if state.get("identity") and state.get("pending_gate") != "SBM_ADMIN_SEMANTIC_DECISION": raise OrchestratorError("INTAKE_NOT_EXPECTED", "Reserved execution is not waiting for a Darwin clarification")
            return self._request_intake(state, normalize_brief(semantic_response))

    def _request_intake(self, state, brief):
        if self.gepetto_adapter is None: raise OrchestratorError("AGENT_RUNTIME_NOT_CONFIGURED", "Gepetto execution adapter is not configured")
        execution_id = state["execution_id"]; root = self.store.execution_dir(execution_id); view = read_json(state["intake_state_view_path"]); progress = read_json(root / "intake/INTENT_PROGRESS.json", {"values": {}, "field_provenance": {}, "turns": []})
        request = {"contract": "GEPETTO_INTAKE_REQUEST/v1", "execution_id": execution_id, "free_form_text": brief, "current_intent_progress": progress, "intake_state_view": view, "directed_question": state.get("pending_question")}; request["request_sha256"] = sha256_object(request)
        routed = self.gepetto_adapter.request_intake(request, root)
        if isinstance(routed, RoutedAgentResponse): return self._accept_intent_update(state, routed.payload, routed.principal_id, routed.provider, request["request_sha256"])
        state.update({"pending_gate": "GEPETTO_INTENT_UPDATE", "pending_agent_request_sha256": routed["request_sha256"], "pending_agent_request_path": routed["request_path"], "pending_response_kind": "INTAKE"}); self.store.save_execution(state); return state

    def _accept_intent_update(self, state, update, principal, provider, request_sha256):
        execution_id = state["execution_id"]; view = read_json(state["intake_state_view_path"]); progress_path = self.store.execution_dir(execution_id) / "intake/INTENT_PROGRESS.json"; current = read_json(progress_path, {"values": {}, "field_provenance": {}, "turns": []}); intent = self.intake.accumulate(update, view, current_progress=current, provenance={"principal_id": principal, "provider": provider, "request_sha256": request_sha256})
        atomic_write_json(progress_path, intent["intent_progress"])
        if not intent["semantic_complete"]:
            state["unresolved_human_semantic_requirements"] = intent["unresolved_human_semantic_requirements"]; state["pending_question"] = intent["unresolved_human_semantic_requirements"][0]["question"]; self.store.save_execution(state); return state
        clarification = bool(state.get("identity")); sequence = state.get("intent_revision", 0) + 1; relative = "intake/INTENT_BRIEF.json" if not clarification else f"intake/INTENT_BRIEF-{sequence:03d}.json"
        intent_path, intent_hash = self.store.write_immutable(execution_id, relative, intent); state["intent_revision"] = sequence; state.pop("pending_question", None); state["unresolved_human_semantic_requirements"] = []
        if clarification:
            state["intent_brief_path"] = str(intent_path); state["intent_brief_sha256"] = intent_hash; profile, _ = self.profiles.resolve(); snapshot = read_json(state["creation_snapshot_path"]); proposal = read_yaml(state["generator_proposal_path"]); request = self.darwin_submissions.request(intent, proposal, snapshot, view, profile); request_path, _ = self.store.write_immutable(execution_id, f"prebuild/DARWIN_ARCHITECTURE_REQUEST-{sequence:03d}.json", request); state.update({"state": "PREBUILD", "darwin_architecture_request_path": str(request_path), "darwin_architecture_request_sha256": request["request_sha256"], "pending_gate": "DARWIN_SPEC_DECISIONS"}); self.store.save_execution(state); self._event(state, "DARWIN_ARCHITECTURE_RE_REQUESTED", inputs={"request": request["request_sha256"]});
            if self.auto_route_agents: self._route_pending_unlocked(state)
            return state
        return self._continue_from_intent(state, intent, intent_path, intent_hash)

    def _continue_from_intent(self, state, intent, intent_path, intent_hash):
        execution_id = state["execution_id"]
        reservation = self.identity.reserve(execution_id, intent["requested_name"]); state["identity"] = reservation; self._event(state, "IDENTITY_RESERVED", outputs={"reservation": sha256_object(reservation)}); self.store.transition(state, "PREBUILD")
        return self._run_generator(state, intent, intent_path, intent_hash)

    def _run_generator(self, state, intent, intent_path, intent_hash):
        execution_id = state["execution_id"]
        view = read_json(state["intake_state_view_path"])
        reservation = state["identity"]
        profile, _ = self.profiles.resolve(); root = self.store.execution_dir(execution_id); proposal_path, metadata_path = self.generator.generate(root, proposal_input(intent, reservation, profile, execution_id), profile)
        if read_yaml(proposal_path)["review_status"] != "DRAFT": raise OrchestratorError("GENERATOR_BOUNDARY_VIOLATION", "Generator proposal must remain DRAFT")
        prebuild = root / "prebuild"; prebuild.mkdir(); shutil.copy2(proposal_path, prebuild / "AGENT_PROPOSAL.yaml")
        state.update({"generator_proposal_sha256": sha256_file(proposal_path), "generator_proposal_path": str(proposal_path), "intent_brief_path": str(intent_path), "intent_brief_sha256": intent_hash, "scaffold_metadata_sha256": sha256_file(metadata_path)})
        snapshot = read_json(state["creation_snapshot_path"]); request = self.darwin_submissions.request(intent, read_yaml(proposal_path), snapshot, view, profile); request_path, _ = self.store.write_immutable(execution_id, "prebuild/DARWIN_ARCHITECTURE_REQUEST.json", request)
        state.update({"darwin_architecture_request_path": str(request_path), "darwin_architecture_request_sha256": request["request_sha256"], "pending_gate": "DARWIN_SPEC_DECISIONS"}); self.store.save_execution(state); self._event(state, "DARWIN_ARCHITECTURE_REQUESTED", inputs={"request": request["request_sha256"]});
        if self.auto_route_agents: self._route_pending_unlocked(state)
        return state

    def _generator_retry_checkpoint_valid(self, state):
        if state.get("state") != "BLOCKED" or state.get("last_error", {}).get("code") != "GENERATOR_FAILED": return False
        required = ("identity", "intent_brief_path", "intent_brief_sha256", "creation_snapshot_path", "creation_snapshot_sha256", "intake_state_view_path", "intake_state_view_sha256")
        if any(not state.get(field) for field in required): return False
        if any(state.get(field) for field in ("generator_proposal_path", "generator_proposal_sha256", "scaffold_metadata_sha256", "darwin_architecture_request_path", "spec_decisions_path", "prebuild_bundle_path")): return False
        root = self.store.execution_dir(state["execution_id"])
        if any((root / relative).exists() for relative in ("prebuild/AGENT_PROPOSAL.yaml", "prebuild/DARWIN_ARCHITECTURE_REQUEST.json", "prebuild/SPEC_DECISIONS.json", "prebuild/PREBUILD_BUNDLE.json")): return False
        try:
            paths = [Path(state[field]).resolve() for field in ("intent_brief_path", "creation_snapshot_path", "intake_state_view_path")]
            for path in paths: path.relative_to(root.resolve())
            intent, snapshot, view = (read_json(path) for path in paths)
            if sha256_object(intent) != state["intent_brief_sha256"]: return False
            if snapshot.get("snapshot_sha256") != state["creation_snapshot_sha256"]: return False
            if sha256_object(view) != state["intake_state_view_sha256"]: return False
            _, current_profile_hash = self.profiles.resolve()
            if current_profile_hash != snapshot.get("creation_profile", {}).get("sha256") or current_profile_hash != state.get("intake_creation_fingerprint", {}).get("creation_profile_sha256"): return False
            ledger = read_json(self.identity.path, {"reservations": []})
            reservation = next((item for item in ledger.get("reservations", []) if item.get("reservation_id") == state["identity"].get("reservation_id")), None)
            if reservation != state["identity"] or reservation.get("execution_id") != state["execution_id"] or reservation.get("state") != "RESERVED": return False
            events = [json.loads(line) for line in (root / "events.ndjson").read_text(encoding="utf-8").splitlines() if line.strip()]
        except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError, OrchestratorError):
            return False
        transitions = [event for event in events if event.get("action") == "STATE_TRANSITION"]
        identity_hash = sha256_object(state["identity"])
        reserved = any(event.get("action") == "IDENTITY_RESERVED" and event.get("output_hashes", {}).get("reservation") == identity_hash for event in events)
        reached_prebuild = any(event.get("details", {}).get("to") == "PREBUILD" for event in transitions)
        last_transition = transitions[-1].get("details", {}) if transitions else {}
        blocked_at_generator = last_transition.get("from") == "PREBUILD" and last_transition.get("to") == "BLOCKED" and last_transition.get("error") == "GENERATOR_FAILED"
        return reserved and reached_prebuild and blocked_at_generator

    def _resume_generator(self, state):
        execution_id = state["execution_id"]
        intent_path = Path(state["intent_brief_path"]); intent = read_json(intent_path); intent_hash = state["intent_brief_sha256"]
        self.store.transition(state, "PREBUILD", details={"recovery": "GENERATOR_RETRY", "error": "GENERATOR_FAILED"})
        self._event(state, "GENERATOR_RECOVERY_STARTED", inputs={"intent_brief": intent_hash}, outputs={"reservation": sha256_object(state["identity"])})
        try:
            recovered = self._run_generator(state, intent, intent_path, intent_hash)
        except Exception as exc:
            code = getattr(exc, "code", type(exc).__name__)
            current = self.store.load_execution(execution_id); self.store.transition(current, "BLOCKED", details={"error": code}); current["last_error"] = {"code": code, "message": str(exc)}; self.store.save_execution(current); raise
        recovered.pop("last_error", None); recovered["last_recovery"] = {"step": "GENERATOR", "status": "SUCCEEDED", "completed_at": utc_now()}; self.store.save_execution(recovered)
        self._event(recovered, "GENERATOR_RECOVERY_SUCCEEDED", outputs={"proposal": recovered["generator_proposal_sha256"]})
        return recovered

    def submit_spec_decisions(self, execution_id, submission):
        principal = self._principal("Darwin")
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id)
            return self._accept_spec_decisions(state, submission, principal.principal_id)

    def _accept_spec_decisions(self, state, submission, principal):
            if state.get("pending_gate") != "DARWIN_SPEC_DECISIONS": raise OrchestratorError("DARWIN_DECISIONS_NOT_EXPECTED", "Execution is not waiting for SPEC_DECISIONS")
            profile, _ = self.profiles.resolve(); accepted = self.darwin_submissions.accept(submission, read_json(state["darwin_architecture_request_path"]), principal, profile)
            if accepted["status"] == "HUMAN_DECISION_REQUIRED": state["pending_question"] = accepted["question"]; state["pending_gate"] = "SBM_ADMIN_SEMANTIC_DECISION"; self.store.transition(state, "CAPTURING_INTENT", details={"source": "Darwin", "reason": "HUMAN_DECISION_REQUIRED"}); return state
            decisions = accepted["decisions"]; execution_id = state["execution_id"]; path, digest = self.store.write_immutable(execution_id, "prebuild/SPEC_DECISIONS.json", decisions); state["spec_decisions_path"] = str(path); state["spec_decisions_sha256"] = digest; state["relevant_agent_ids"] = self._relevant_agents(state, decisions); self._compile_prebuild(state, profile, decisions); self._event(state, "DARWIN_SPEC_DECISIONS_ACCEPTED", actor=principal, outputs={"spec_decisions": digest}); return state

    def _relevant_agents(self, state, decisions):
        registry = read_json(self.store.state / "final-agent-registry.json", {"agents": []}); known = {item.get("agent_id") for item in registry.get("agents", [])}; intent = read_json(state["intent_brief_path"]); values = list(intent.get("important_relationships", []))
        def collect(value):
            if isinstance(value, str): values.append(value)
            elif isinstance(value, dict):
                for nested in value.values(): collect(nested)
            elif isinstance(value, list):
                for nested in value: collect(nested)
        for field in ("relationships", "execution_dependencies", "hierarchy", "referenced_agents"): collect(decisions.get(field, []))
        return sorted(agent_id for agent_id in known if agent_id and any(agent_id in value for value in values))

    def _compile_prebuild(self, state, profile, decisions):
        root = self.store.execution_dir(state["execution_id"]); prebuild = root / "prebuild"; proposal = read_yaml(prebuild / "AGENT_PROPOSAL.yaml"); ids = {"proposal": sortable_id("approval_proposal_"), "spec": sortable_id("approval_spec_"), "materialization": sortable_id("approval_materialization_")}; state["reserved_approval_ids"] = ids
        state["template_identity"] = {"template_id": profile["bindings"]["template"]["id"], "template_version": profile["bindings"]["template"]["version"]}; state["template_sha256"] = profile["bindings"]["template"]["sha256"]
        compiled = self.compiler.compile(prebuild, proposal, decisions, state["identity"], profile, ids["spec"]); self.compiler.validate_schema(prebuild / "AGENT_SPEC.yaml", self.config.agents_root / profile["bindings"]["schemas"]["agent_spec"]["path"])
        bundle = {"execution_id": state["execution_id"], "proposal_sha256": state["generator_proposal_sha256"], "scaffold_metadata_sha256": state["scaffold_metadata_sha256"], "intent_brief_sha256": state["intent_brief_sha256"], "intake_state_view_sha256": state["intake_state_view_sha256"], "spec_decisions_sha256": state["spec_decisions_sha256"], "compiled_artifacts": compiled, "creation_context_snapshot_sha256": state["creation_snapshot_sha256"]}; bundle["prebuild_bundle_sha256"] = sha256_object(bundle)
        bundle_path, _ = self.store.write_immutable(state["execution_id"], "prebuild/PREBUILD_BUNDLE.json", bundle); state["prebuild_bundle_sha256"] = bundle["prebuild_bundle_sha256"]; state["prebuild_bundle_path"] = str(bundle_path)
        creation = read_json(state["creation_snapshot_path"]); baseline = self.context.fingerprint(state["intake_creation_fingerprint"]["creation_profile_sha256"], creation["registry_document"], creation["registry"]["sha256"], creation["reservation_ledger_document"], creation["reservation_ledger"]["sha256"], state.get("relevant_agent_ids", []), self.config.agents_root); current = self._current_fingerprint(state); classification = classify_freshness(baseline, current, reservation_conflict=self.identity.conflicts(state["identity"])); state["intake_creation_fingerprint"] = baseline; state["current_prebuild_fingerprint"] = current
        snapshot = {"execution_id": state["execution_id"], "creation_snapshot_sha256": state["creation_snapshot_sha256"], "intake_creation_fingerprint": baseline, "current_prebuild_fingerprint": current, "freshness_classification": classification, "prebuild_bundle_sha256": bundle["prebuild_bundle_sha256"], "timestamp": utc_now()}; snapshot["build_context_snapshot_sha256"] = sha256_object(snapshot); snapshot_path, _ = self.store.write_immutable(state["execution_id"], "prebuild/BUILD_CONTEXT_SNAPSHOT.json", snapshot); state["build_context_snapshot_sha256"] = snapshot["build_context_snapshot_sha256"]; state["build_context_snapshot_path"] = str(snapshot_path)
        self._set_review_gate(state, "DARWIN_DESIGN_REVIEW_RECORD", "Darwin", {"prebuild_bundle_sha256": state["prebuild_bundle_sha256"], "build_context_snapshot_sha256": state["build_context_snapshot_sha256"]}, "PREBUILD")

    def _bundle_item(self, path):
        path = Path(path); payload = path.read_bytes()
        try: relative = path.resolve().relative_to(self.config.agents_root).as_posix()
        except ValueError: relative = path.name
        return {"path": relative, "sha256": sha256_file(path), "encoding": "base64", "content": base64.b64encode(payload).decode("ascii")}

    def _review_input_bundle(self, state, record_type, phase):
        root = self.store.execution_dir(state["execution_id"]); profile, _ = self.profiles.resolve(); items = {}
        if phase == "PREBUILD":
            paths = {"INTENT_BRIEF": state["intent_brief_path"], "AGENT_PROPOSAL": root / "prebuild/AGENT_PROPOSAL.yaml", "SPEC_DECISIONS": state["spec_decisions_path"], "AGENT_SPEC": root / "prebuild/AGENT_SPEC.yaml", "BUILD_CONTEXT_SNAPSHOT": state["build_context_snapshot_path"], "PREBUILD_BUNDLE": state["prebuild_bundle_path"], "INTAKE_STATE_VIEW": state["intake_state_view_path"]}
            for name, binding in profile["bindings"]["schemas"].items(): paths[f"NORMATIVE_SCHEMA_{name.upper()}"] = self.config.agents_root / binding["path"]
            paths["NORMATIVE_STANDARD"] = self.config.agents_root / profile["bindings"]["standard"]["path"]
            paths["NORMATIVE_GOVERNANCE"] = self.config.agents_root / profile["bindings"]["governance"]["path"]
        else:
            primary = root / "attempts" / state["primary_attempt_id"]
            paths = {"CANDIDATE": state["candidate_path"], "QA_EVIDENCE_BUNDLE": root / "qa/QA_EVIDENCE_BUNDLE.json", "REGISTRY_CANDIDATE": state["registry_candidate_path"], "EXECUTION_EVIDENCE": primary / "EXECUTION_EVIDENCE.yaml", "INTEGRITY_MANIFEST": primary / "output/MANIFEST.yaml", "INTEGRITY_CHECKSUMS": primary / "output/CHECKSUMS.sha256"}
            if record_type == "NOE_FINAL_FUNCTIONAL_REVIEW_RECORD": paths["DARWIN_FINAL_REVIEW"] = root / "final-review/DARWIN_FUNCTIONAL_REVIEW_RECORD.json"
        for label, path in paths.items():
            if not Path(path).is_file(): raise OrchestratorError("REVIEW_INPUT_BUNDLE_INCOMPLETE", f"Review input {label} is missing")
            items[label] = self._bundle_item(path)
        bundle = {"contract": "REVIEW_INPUT_BUNDLE/v1", "execution_id": state["execution_id"], "record_type": record_type, "phase": phase, "items": items}
        bundle["review_input_bundle_sha256"] = sha256_object(bundle)
        path, _ = self.store.write_immutable(state["execution_id"], f"{phase.lower() if phase == 'PREBUILD' else 'final-review'}/REVIEW_INPUT_BUNDLE-{record_type}.json", bundle)
        return path, bundle

    def _verify_review_input_bundle(self, state):
        bundle = read_json(state["pending_review_input_bundle_path"]); claimed = bundle.get("review_input_bundle_sha256"); unsigned = dict(bundle); unsigned.pop("review_input_bundle_sha256", None)
        if claimed != sha256_object(unsigned) or claimed != state["pending_review_input_bundle_sha256"]: raise OrchestratorError("REVIEW_INPUT_BUNDLE_HASH_MISMATCH", "Review input bundle hash is invalid")
        required = {"INTENT_BRIEF", "AGENT_PROPOSAL", "SPEC_DECISIONS", "AGENT_SPEC", "BUILD_CONTEXT_SNAPSHOT", "PREBUILD_BUNDLE", "INTAKE_STATE_VIEW", "NORMATIVE_STANDARD", "NORMATIVE_GOVERNANCE"} if bundle.get("phase") == "PREBUILD" else {"CANDIDATE", "QA_EVIDENCE_BUNDLE", "REGISTRY_CANDIDATE", "EXECUTION_EVIDENCE", "INTEGRITY_MANIFEST", "INTEGRITY_CHECKSUMS"}
        if state.get("pending_gate") == "NOE_FINAL_FUNCTIONAL_REVIEW_RECORD": required.add("DARWIN_FINAL_REVIEW")
        if not required <= set(bundle.get("items", {})): raise OrchestratorError("REVIEW_INPUT_BUNDLE_INCOMPLETE", "Review input bundle is incomplete")
        for label, item in bundle.get("items", {}).items():
            try: payload = base64.b64decode(item["content"], validate=True)
            except Exception as exc: raise OrchestratorError("REVIEW_INPUT_BUNDLE_INVALID", f"Review input {label} encoding is invalid") from exc
            if __import__("hashlib").sha256(payload).hexdigest() != item.get("sha256"): raise OrchestratorError("REVIEW_INPUT_BUNDLE_TAMPERED", f"Review input {label} was modified")
        return bundle

    def _set_review_gate(self, state, record_type, reviewer, subjects, phase):
        bundle_path, bundle = self._review_input_bundle(state, record_type, phase); subjects = dict(subjects); subjects["review_input_bundle_sha256"] = bundle["review_input_bundle_sha256"]
        state.setdefault("review_input_bundles", {})[record_type] = {"path": str(bundle_path), "sha256": bundle["review_input_bundle_sha256"]}
        state.update({"pending_gate": record_type, "pending_reviewer": reviewer, "pending_review_subjects": subjects, "pending_review_input_bundle_path": str(bundle_path), "pending_review_input_bundle_sha256": bundle["review_input_bundle_sha256"], "review_phase": phase}); self.store.save_execution(state); self._event(state, "REVIEW_REQUESTED", details={"record_type": record_type, "reviewer": reviewer}, inputs=subjects)
        if self.auto_route_agents: self._route_pending_unlocked(state)

    def submit_review(self, execution_id, submission):
        principal = self._principal()
        with self.store.lock(f"execution-{execution_id}"):
            return self._accept_review(self.store.load_execution(execution_id), submission, principal.principal_id)

    def _accept_review(self, state, submission, principal):
            execution_id = state["execution_id"]; record_type = state.get("pending_gate"); allowed = {"DARWIN_DESIGN_REVIEW_RECORD", "NOE_PREBUILD_REVIEW_RECORD", "DARWIN_FUNCTIONAL_REVIEW_RECORD", "NOE_FINAL_FUNCTIONAL_REVIEW_RECORD"}
            if record_type not in allowed: raise OrchestratorError("REVIEW_NOT_EXPECTED", "Execution is not waiting for a review")
            self._verify_review_input_bundle(state)
            reviewer = state["pending_reviewer"]; subjects = state["pending_review_subjects"]; folder = "prebuild" if state["review_phase"] == "PREBUILD" else "final-review"; record = self.review_submissions.accept(self.store.execution_dir(execution_id) / folder, record_type, execution_id, reviewer, subjects, submission, principal)
            self._event(state, "REVIEW_SUBMITTED", actor=principal, inputs=subjects, outputs={"record": record["record_sha256"]}, details={"verdict": record["verdict"]})
            if record["verdict"] != "PASS": state["pending_gate"] = None; self.store.transition(state, "BLOCKED", details={"review": record_type, "verdict": "FAIL"}); return state
            if record_type == "DARWIN_DESIGN_REVIEW_RECORD": state["darwin_prebuild_review_sha256"] = record["record_sha256"]; self._set_review_gate(state, "NOE_PREBUILD_REVIEW_RECORD", "Noe", subjects, "PREBUILD")
            elif record_type == "NOE_PREBUILD_REVIEW_RECORD": state["noe_prebuild_review_sha256"] = record["record_sha256"]; state["pending_gate"] = None; self.store.transition(state, "WAITING_BUILD_APPROVAL")
            elif record_type == "DARWIN_FUNCTIONAL_REVIEW_RECORD": state["darwin_final_review_sha256"] = record["record_sha256"]; self._set_review_gate(state, "NOE_FINAL_FUNCTIONAL_REVIEW_RECORD", "Noe", subjects, "FINAL")
            else: state["noe_final_review_sha256"] = record["record_sha256"]; state["pending_gate"] = None; self.store.transition(state, "WAITING_PROMOTION_APPROVAL")
            return state

    def route_pending(self, execution_id):
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id); self._route_pending_unlocked(state); return state

    def import_agent_response(self, execution_id, envelope):
        """Operational MANUAL_CHAT/API seam; authentication remains adapter-owned and Core-validated."""
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id); gate = state.get("pending_gate")
            adapter = self.gepetto_adapter if gate == "GEPETTO_INTENT_UPDATE" else (self.architecture_adapter if gate == "DARWIN_SPEC_DECISIONS" else (self.darwin_review_adapter if state.get("pending_reviewer") == "Darwin" else self.noe_review_adapter))
            if not hasattr(adapter, "import_response"): raise OrchestratorError("AGENT_RESPONSE_IMPORT_UNSUPPORTED", "Configured adapter does not support response import")
            response = adapter.import_response(envelope, state["pending_agent_request_sha256"])
            if not response.authenticated: raise OrchestratorError("AGENT_ADAPTER_UNAUTHENTICATED", "Imported agent response is not authenticated")
            if gate == "GEPETTO_INTENT_UPDATE": return self._accept_intent_update(state, response.payload, response.principal_id, response.provider, state["pending_agent_request_sha256"])
            return self._accept_spec_decisions(state, response.payload, response.principal_id) if gate == "DARWIN_SPEC_DECISIONS" else self._accept_review(state, response.payload, response.principal_id)

    def _route_pending_unlocked(self, state):
        gate = state.get("pending_gate"); root = self.store.execution_dir(state["execution_id"])
        if gate == "DARWIN_SPEC_DECISIONS":
            request = read_json(state["darwin_architecture_request_path"]); response = self.architecture_adapter.request_architecture(request, root)
            if isinstance(response, dict) and response.get("waiting"):
                state.update({"pending_agent_request_sha256": response["request_sha256"], "pending_agent_request_path": response["request_path"], "pending_response_kind": "ARCHITECTURE"}); self.store.save_execution(state); return state
            if not response.authenticated: raise OrchestratorError("AGENT_ADAPTER_UNAUTHENTICATED", "Architecture adapter response is not authenticated")
            return self._accept_spec_decisions(state, response.payload, response.principal_id)
        review_gates = {"DARWIN_DESIGN_REVIEW_RECORD", "NOE_PREBUILD_REVIEW_RECORD", "DARWIN_FUNCTIONAL_REVIEW_RECORD", "NOE_FINAL_FUNCTIONAL_REVIEW_RECORD"}
        if gate in review_gates:
            request = {"contract": "AGENT_REVIEW_REQUEST/v1", "record_type": gate, "execution_id": state["execution_id"], "expected_reviewer": state["pending_reviewer"], "subject_hashes": state["pending_review_subjects"], "review_input_bundle_sha256": state["pending_review_input_bundle_sha256"], "review_input_bundle": self._verify_review_input_bundle(state)}; request["request_sha256"] = sha256_object(request)
            adapter = self.darwin_review_adapter if state["pending_reviewer"] == "Darwin" else self.noe_review_adapter; response = adapter.request_review(request, root)
            if isinstance(response, dict) and response.get("waiting"):
                state.update({"pending_agent_request_sha256": response["request_sha256"], "pending_agent_request_path": response["request_path"], "pending_response_kind": "REVIEW"}); self.store.save_execution(state); return state
            if not response.authenticated: raise OrchestratorError("AGENT_ADAPTER_UNAUTHENTICATED", "Review adapter response is not authenticated")
            return self._accept_review(state, response.payload, response.principal_id)
        return state

    def _current_fingerprint(self, state):
        _, profile_hash = self.profiles.resolve(); registry = read_json(self.store.state / "final-agent-registry.json", {"revision": 0, "agents": []}); ledger = read_json(self.store.state / "identity-reservations.json", {"revision": 0, "reservations": []})
        return self.context.fingerprint(profile_hash, registry, sha256_object(registry), ledger, sha256_object(ledger), state.get("relevant_agent_ids", []), self.config.agents_root)
    def freshness(self, execution_id, state_override=None):
        state = state_override or self.store.load_execution(execution_id); current = self._current_fingerprint(state); conflict = self.identity.conflicts(state["identity"]) if state.get("identity") else False; baseline = state.get("intake_creation_fingerprint", state["creation_fingerprint"]); return {"classification": classify_freshness(baseline, current, reservation_conflict=conflict), "fingerprint": current}
    def approve(self, execution_id):
        principal = self._principal("sbm-admin")
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id)
            if state["state"] == "WAITING_BUILD_APPROVAL": return self._approve_build(state, principal)
            if state["state"] == "WAITING_PROMOTION_APPROVAL": return self._approve_promotion(state, principal)
            raise OrchestratorError("APPROVAL_NOT_EXPECTED", "Execution is not waiting for an approval", details={"state": state["state"]})
    def approval_view(self, execution_id):
        state = self.store.load_execution(execution_id)
        if state["state"] == "WAITING_BUILD_APPROVAL": return {"gate": "BUILD_APPROVAL", "execution_id": execution_id, "prebuild_bundle_sha256": state["prebuild_bundle_sha256"], "agent": state["identity"]}
        if state["state"] == "WAITING_PROMOTION_APPROVAL": return {"gate": "PROMOTION_APPROVAL", "execution_id": execution_id, "candidate_sha256": state["candidate_sha256"], "qa_evidence_sha256": state["qa_evidence_sha256"], "agent": state["identity"]}
        raise OrchestratorError("APPROVAL_NOT_EXPECTED", "Execution is not waiting for approval")
    def _approve_build(self, state, principal):
        classification = self.freshness(state["execution_id"])["classification"]; self._event(state, "PREBUILD_CONTEXT_SYNC", details={"classification": classification})
        if classification == "CONTRACT_DELTA": self.store.transition(state, "STALE_CREATION_CONTEXT"); raise OrchestratorError("CONTRACT_DELTA", "Creation profile changed; rebase required")
        if classification in ("ECOSYSTEM_RELEVANT_DELTA", "RESERVATION_CONFLICT"): state["pending_gate"] = "PREBUILD_RECOMPUTE_REQUIRED"; self.store.transition(state, "PREBUILD"); raise OrchestratorError(classification, "Prebuild/reviews must be recomputed")
        state["build_frozen_fingerprint"] = self._current_fingerprint(state); self.store.save_execution(state)
        root = self.store.execution_dir(state["execution_id"]); base_subjects = {"prebuild_bundle_sha256": state["prebuild_bundle_sha256"], "build_context_snapshot_sha256": state["build_context_snapshot_sha256"]}
        for name in ("DARWIN_DESIGN_REVIEW_RECORD", "NOE_PREBUILD_REVIEW_RECORD"):
            record = read_json(root / "prebuild" / f"{name}.json"); expected = dict(base_subjects); expected["review_input_bundle_sha256"] = state["review_input_bundles"][name]["sha256"]
            if not self.review_submissions.valid(record, expected): raise OrchestratorError("STALE_REVIEW", f"{name} is stale")
        event = self.approvals.write_build_approval(root, state, principal); self._event(state, "BUILD_APPROVED", actor=principal.principal_id, inputs={"prebuild_bundle": state["prebuild_bundle_sha256"]}, outputs={"decision": event["event_sha256"]}); self.identity.set_state(state["identity"]["reservation_id"], "CONSUMING"); self.store.transition(state, "BUILDING"); return self._build(state)
    def _build(self, state):
        root = self.store.execution_dir(state["execution_id"]); profile, _ = self.profiles.resolve()
        profile["_agents_root"] = str(self.config.agents_root); profile["_execution_id"] = state["execution_id"]; profile["_reservation_id"] = state["identity"]["reservation_id"]
        try:
            first_id = sortable_id("attempt_"); second_id = sortable_id("attempt_"); first = self.factory.materialize(root, first_id, root / "approved", root / "prebuild", profile); replay = self.factory.materialize(root, second_id, root / "approved", root / "prebuild", profile); qa = self.qa.run(root, first, replay, profile); candidate_sha = sha256_file(first["candidate"]); registry_sha = sha256_file(first["registry_candidate"])
            state.update({"primary_attempt_id": first_id, "replay_attempt_id": second_id, "candidate_path": str(first["candidate"]), "candidate_sha256": candidate_sha, "qa_evidence_sha256": qa["qa_evidence_sha256"], "registry_candidate_path": str(first["registry_candidate"]), "registry_candidate_sha256": registry_sha}); self.store.transition(state, "FINAL_REVIEW"); self._set_review_gate(state, "DARWIN_FUNCTIONAL_REVIEW_RECORD", "Darwin", {"candidate_sha256": candidate_sha, "qa_evidence_sha256": qa["qa_evidence_sha256"], "registry_candidate_sha256": registry_sha}, "FINAL"); return state
        except Exception as exc:
            current = self.store.load_execution(state["execution_id"]); self.store.transition(current, "BLOCKED", details={"error": getattr(exc, "code", type(exc).__name__)}); raise
    def _approve_promotion(self, state, principal):
        if sha256_file(state["candidate_path"]) != state["candidate_sha256"]: raise OrchestratorError("CANDIDATE_MUTATED", "Candidate changed after final reviews")
        root = self.store.execution_dir(state["execution_id"]); base_subjects = {"candidate_sha256": state["candidate_sha256"], "qa_evidence_sha256": state["qa_evidence_sha256"], "registry_candidate_sha256": state["registry_candidate_sha256"]}
        for name, field in (("DARWIN_FUNCTIONAL_REVIEW_RECORD", "darwin_final_review_sha256"), ("NOE_FINAL_FUNCTIONAL_REVIEW_RECORD", "noe_final_review_sha256")):
            record = read_json(root / "final-review" / f"{name}.json")
            expected = dict(base_subjects); expected["review_input_bundle_sha256"] = state["review_input_bundles"][name]["sha256"]
            if not self.review_submissions.valid(record, expected) or record["record_sha256"] != state[field]: raise OrchestratorError("STALE_FINAL_REVIEW", f"{name} does not bind current candidate")
        event = self.approvals.write_promotion_approval(root, state, principal.principal_id); self.store.transition(state, "PROMOTING"); tx = self.promotion.prepare(state, event)
        try: self.promotion.commit(tx)
        except Exception: self.store.save_execution(state); raise
        self.identity.set_state(state["identity"]["reservation_id"], "CONSUMED"); self.store.transition(state, "PROMOTED"); return state
    def resume(self, execution_id):
        with self.store.lock(f"execution-{execution_id}"):
            state = self.store.load_execution(execution_id)
            if state["state"] == "PROMOTING":
                tx = self.promotion.resume(execution_id)
                if tx["state"] == "COMMITTED": self.identity.set_state(state["identity"]["reservation_id"], "CONSUMED"); self.store.transition(state, "PROMOTED")
            elif state["state"] == "BUILDING": return self._build(state)
            elif self._generator_retry_checkpoint_valid(state): return self._resume_generator(state)
            return state
    def status(self, execution_id=None):
        if execution_id: return self.store.load_execution(execution_id)
        return [read_json(path) for path in sorted(self.store.executions.glob("*/state.json"))]
