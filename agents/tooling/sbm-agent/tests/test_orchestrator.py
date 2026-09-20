from __future__ import annotations

import json
import io
import shutil
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from contextlib import redirect_stdout

from sbm_agent_orchestrator.adapters import FactoryAdapter, InProcessFactoryAdapter, InProcessGeneratorAdapter, PinnedZipRuntime, verify_factory_authorization
from sbm_agent_orchestrator.cli import main as cli_main
from sbm_agent_orchestrator.core import Orchestrator, OrchestratorConfig, StaticPrincipalProvider, UnixPrincipalProvider
from sbm_agent_orchestrator.errors import OrchestratorError
from sbm_agent_orchestrator.identity import IdentityAllocator
from sbm_agent_orchestrator.profiles import CreationProfileResolver, classify_freshness
from sbm_agent_orchestrator.storage import RuntimeStore
from sbm_agent_orchestrator.routing import AgentIdentity, HMACResponseAttestor, ManualChatAgentExecutionAdapter, PackageIdentityVerifier, RoutedAgentResponse
from sbm_agent_orchestrator.util import atomic_write_json, read_json, sha256_file, sha256_object, sortable_id


AGENTS_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class TestAgentExecutionAdapter:
    """Test-only semantic/agent seam; production contains no synthetic responses."""
    def __init__(self, principal): self.principal = principal
    def request_intake(self, request, execution_dir):
        text = request["free_form_text"]; lower = text.casefold(); fields = {"semantic_brief": text}
        import re
        match = re.search(r"(?:se llama|llamado|el nombre es)\s+([A-Za-z0-9_-]+)", text, re.I) or re.search(r"(?:quiero crear(?: un agente)?|es el agente)\s+([A-Za-z0-9_-]+)", text, re.I)
        if ":" in text: fields.update({"requested_name": text.split(":", 1)[0].strip(), "desired_outcome": text.split(":", 1)[1].strip()})
        elif match:
            fields["requested_name"] = match.group(1); remainder = text[match.end():].strip(" ,.:;-")
            if len(remainder.split()) >= 2: fields["desired_outcome"] = remainder
        if lower.startswith(("quiero que", "necesito que", "debe ")): fields["desired_outcome"] = text
        if request["current_intent_progress"].get("values", {}).get("requested_name") and request.get("directed_question"): fields["clarifications"] = [text]
        return RoutedAgentResponse("gepetto", "test-agent-execution", True, {"contract": "STRUCTURED_INTENT_UPDATE/v1", "fields": fields})
    def request_architecture(self, request, execution_dir):
        proposal = request["agent_proposal"]
        decisions = {"authority": proposal["authority"], "permissions": proposal["permissions"], "required_context": proposal["required_context"], "relationships": proposal["relationships"], "hierarchy": {"reports_to": "sbm-admin", "can_request_from": ["Darwin", "Noe"], "can_instruct": [], "requires_approval_from": ["sbm-admin"], "escalation_target": "sbm-admin"}, "retrieval_strategy": proposal["retrieval_strategy"], "embedding_strategy": proposal["embedding_strategy"], "execution_modes": proposal["execution_modes"], "asynchronous_capabilities": proposal["asynchronous_capabilities"], "execution_dependencies": proposal["execution_dependencies"], "outputs": proposal["outputs"], "escalation_rules": proposal["escalation_rules"], "deployment": proposal["deployment"], "qa": proposal["qa_specific"], "runtime": {"context_delivery": "ZIP", "idempotency": "REQUIRED"}, "security_boundaries": ["NO_SELF_APPROVAL", "NO_LLM_BY_DEFAULT"]}
        return RoutedAgentResponse("Darwin", "test-agent-execution", True, {"status": "RESOLVED", "architecture_request_sha256": request["request_sha256"], "decisions": decisions})
    def request_review(self, request, execution_dir): return RoutedAgentResponse(self.principal, "test-agent-execution", True, {"verdict": "PASS", "subject_hashes": request["subject_hashes"]})


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.test_root = PACKAGE_ROOT / ".test-runtime" / sortable_id("case_")
        self.runtime = self.test_root / "runtime"
        self.final = self.test_root / "final"
        self.test_root.mkdir(parents=True)
        config = OrchestratorConfig(AGENTS_ROOT, runtime_root=self.runtime, final_root=self.final)
        self.orch = Orchestrator(
            config,
            generator=InProcessGeneratorAdapter(),
            factory=InProcessFactoryAdapter(),
            gepetto_adapter=TestAgentExecutionAdapter("gepetto"),
            principal_provider=StaticPrincipalProvider("sbm-admin"),
        )

    def tearDown(self):
        shutil.rmtree(self.test_root, ignore_errors=True)

    def raw_create(self, name="Roberto", key=None, brief=None):
        return self.orch.create(brief or f"{name}: analiza resultados de negocio", principal="local:operator", idempotency_key=key or sortable_id("key_"))

    def external_intent_brief(self, **overrides):
        intent = {
            "contract": "INTENT_BRIEF/v1",
            "requested_name": "Roberto",
            "semantic_brief": "Crear Roberto para analizar resultados de negocio",
            "desired_outcome": "analizar resultados de negocio",
            "specific_objectives": ["analizar resultados de negocio"],
            "material_limits": [],
            "important_relationships": [],
            "clarifications": [],
            "unresolved_human_semantic_requirements": [],
            "semantic_complete": True,
            "provenance": {"semantic_source": "sbm-admin", "intake_adapter": "Darwin", "intake_mode": "DARWIN_TEMPORARY_INTAKE"},
        }
        intent.update(overrides)
        return intent

    def external_create(self, intent=None, mode="DARWIN_TEMPORARY_INTAKE", principal="sbm-admin", key=None):
        return self.orch.create_from_intent_brief(intent or self.external_intent_brief(), intake_mode=mode, principal=principal, idempotency_key=key or sortable_id("external_"))

    def submit_decisions(self, state, relationships=None, dependencies=None, overrides=None):
        profile, _ = self.orch.profiles.resolve(); proposal = __import__("yaml").safe_load(Path(state["generator_proposal_path"]).read_text())
        defaults = profile["canonical_defaults"]
        decisions = {
            "authority": proposal["authority"], "permissions": proposal["permissions"], "required_context": proposal["required_context"],
            "relationships": relationships if relationships is not None else proposal["relationships"],
            "hierarchy": {"reports_to": "sbm-admin", "can_request_from": ["Darwin", "Noe"], "can_instruct": [], "requires_approval_from": ["sbm-admin"], "escalation_target": "sbm-admin"},
            "retrieval_strategy": proposal["retrieval_strategy"], "embedding_strategy": proposal["embedding_strategy"],
            "execution_modes": proposal["execution_modes"], "asynchronous_capabilities": proposal["asynchronous_capabilities"],
            "execution_dependencies": dependencies if dependencies is not None else proposal["execution_dependencies"],
            "outputs": proposal["outputs"], "escalation_rules": proposal["escalation_rules"], "deployment": proposal["deployment"],
            "qa": proposal["qa_specific"], "runtime": defaults["runtime"], "security_boundaries": defaults["security_boundaries"],
        }
        decisions.update(overrides or {})
        self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        return self.orch.submit_spec_decisions(state["execution_id"], {"status": "RESOLVED", "architecture_request_sha256": state["darwin_architecture_request_sha256"], "decisions": decisions})

    def submit_pending_review(self, state, reviewer=None, subjects=None):
        reviewer = reviewer or state["pending_reviewer"]; self.orch.principal_provider = StaticPrincipalProvider(reviewer)
        return self.orch.submit_review(state["execution_id"], {"verdict": "PASS", "subject_hashes": subjects or state["pending_review_subjects"]})

    def create(self, name="Roberto", key=None, brief=None, relationships=None, dependencies=None):
        state = self.raw_create(name, key, brief); state = self.submit_decisions(state, relationships, dependencies)
        state = self.submit_pending_review(state); state = self.submit_pending_review(state)
        self.orch.principal_provider = StaticPrincipalProvider("sbm-admin")
        return state

    def build(self):
        state = self.create()
        state = self.orch.approve(state["execution_id"])
        state = self.submit_pending_review(state); state = self.submit_pending_review(state)
        self.orch.principal_provider = StaticPrincipalProvider("sbm-admin")
        return state

    def test_create_happy_path(self):
        state = self.create()
        self.assertEqual(state["state"], "WAITING_BUILD_APPROVAL")
        self.assertTrue((self.orch.store.execution_dir(state["execution_id"]) / "events.ndjson").is_file())

    def test_create_retry_idempotency(self):
        key = "durable-token"
        first = self.orch.create("Roberto: analiza", principal="p", idempotency_key=key)
        second = self.orch.create("Roberto: analiza", principal="p", idempotency_key=key)
        self.assertEqual(first["execution_id"], second["execution_id"])

    def test_create_idempotency_conflict(self):
        self.orch.create("Roberto: analiza", principal="p", idempotency_key="same")
        with self.assertRaisesRegex(OrchestratorError, "different semantic"):
            self.orch.create("Ana: redacta", principal="p", idempotency_key="same")

    def copied_profiles(self):
        root = self.test_root / "profiles"; shutil.copytree(PACKAGE_ROOT / "config/profiles", root); return root

    def test_profile_exactly_one_active(self):
        root = self.copied_profiles(); activation = read_json(root / "activation.json"); activation["active_profiles"].append(dict(activation["active_profiles"][0])); atomic_write_json(root / "activation.json", activation)
        with self.assertRaisesRegex(OrchestratorError, "Exactly one"):
            CreationProfileResolver(AGENTS_ROOT, root).resolve()

    def test_profile_revoked(self):
        root = self.copied_profiles(); activation = read_json(root / "activation.json"); activation["revoked_profiles"] = [activation["active_profiles"][0]["profile_id"]]; atomic_write_json(root / "activation.json", activation)
        with self.assertRaisesRegex(OrchestratorError, "revoked"):
            CreationProfileResolver(AGENTS_ROOT, root).resolve()

    def test_profile_hash_mismatch(self):
        root = self.copied_profiles(); profile = read_json(root / "creation-profile-v1.json"); profile["profile_version"] = "tampered"; atomic_write_json(root / "creation-profile-v1.json", profile)
        with self.assertRaisesRegex(OrchestratorError, "hash mismatch"):
            CreationProfileResolver(AGENTS_ROOT, root).resolve()

    def test_snapshot_immutability(self):
        state = self.create(); execution = state["execution_id"]
        with self.assertRaises(OrchestratorError):
            self.orch.store.write_immutable(execution, "snapshots/creation-context-001.json", {"changed": True})

    def test_identity_concurrent_reservation(self):
        store = self.orch.store; allocator = IdentityAllocator(store)
        def reserve(i):
            try: return allocator.reserve(f"parallel-{i}", "Concurrent")
            except OrchestratorError as exc: return exc.code
        with ThreadPoolExecutor(max_workers=8) as pool: results = list(pool.map(reserve, range(8)))
        self.assertEqual(sum(isinstance(x, dict) for x in results), 1)
        self.assertEqual(results.count("IDENTITY_CONFLICT"), 7)

    def test_monotonic_sequence_not_reused(self):
        a = self.orch.identity.reserve("a", "Alpha"); self.orch.identity.set_state(a["reservation_id"], "RELEASED")
        b = self.orch.identity.reserve("b", "Beta")
        self.assertGreater(b["sequence"], a["sequence"])

    def test_identity_conflict(self):
        self.orch.identity.reserve("a", "Same")
        with self.assertRaisesRegex(OrchestratorError, "already reserved"):
            self.orch.identity.reserve("b", "Same")

    def test_generator_draft_immutable(self):
        state = self.create(); original = state["generator_proposal_sha256"]
        self.orch.approve(state["execution_id"])
        self.assertEqual(sha256_file(state["generator_proposal_path"]), original)

    def test_approved_projection_binding(self):
        state = self.create(); self.orch.approve(state["execution_id"]); root = self.orch.store.execution_dir(state["execution_id"])
        projection = read_json(root / "approved/APPROVED_PROPOSAL_PROJECTION.json")
        self.assertEqual(projection["original_proposal_sha256"], state["generator_proposal_sha256"])
        self.assertEqual(projection["prebuild_bundle_sha256"], state["prebuild_bundle_sha256"])

    def test_unauthorized_approval_rejected(self):
        state = self.create(); self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        with self.assertRaisesRegex(OrchestratorError, "authenticated sbm-admin"):
            self.orch.approve(state["execution_id"])

    def test_authenticated_sbm_admin_approval_accepted(self):
        state = self.create(); built = self.orch.approve(state["execution_id"])
        self.assertEqual(built["state"], "FINAL_REVIEW")

    def test_stale_review_invalidation(self):
        state = self.create(); root = self.orch.store.execution_dir(state["execution_id"])
        record = read_json(root / "prebuild/DARWIN_DESIGN_REVIEW_RECORD.json"); record["subject_hashes"]["prebuild_bundle_sha256"] = "0" * 64; atomic_write_json(root / "prebuild/DARWIN_DESIGN_REVIEW_RECORD.json", record)
        with self.assertRaisesRegex(OrchestratorError, "stale"):
            self.orch.approve(state["execution_id"])

    def fingerprint(self, profile="a", registry="a", relevant="a", ledger="a"):
        return {"creation_profile_sha256": profile, "registry_sha256": registry, "relevant_final_agents_sha256": relevant, "reservation_ledger_sha256": ledger}

    def test_contract_delta(self):
        self.assertEqual(classify_freshness(self.fingerprint(), self.fingerprint(profile="b")), "CONTRACT_DELTA")

    def test_ecosystem_relevant_delta(self):
        self.assertEqual(classify_freshness(self.fingerprint(), self.fingerprint(registry="b", relevant="b")), "ECOSYSTEM_RELEVANT_DELTA")

    def test_ecosystem_irrelevant_delta(self):
        self.assertEqual(classify_freshness(self.fingerprint(), self.fingerprint(registry="b")), "ECOSYSTEM_IRRELEVANT_DELTA")

    def test_reservation_conflict_classification(self):
        self.assertEqual(classify_freshness(self.fingerprint(), self.fingerprint(), reservation_conflict=True), "RESERVATION_CONFLICT")

    def test_factory_invocation_binding(self):
        state = self.build(); root = self.orch.store.execution_dir(state["execution_id"])
        evidence = (root / "attempts" / state["primary_attempt_id"] / "EXECUTION_EVIDENCE.yaml").read_text()
        self.assertIn("factory_version: 1.0.2", evidence); self.assertIn("template_version: 2.0.1", evidence)

    def test_attempt_isolation(self):
        state = self.build(); root = self.orch.store.execution_dir(state["execution_id"])
        self.assertNotEqual(state["primary_attempt_id"], state["replay_attempt_id"])
        self.assertTrue((root / "attempts" / state["primary_attempt_id"]).is_dir())
        self.assertTrue((root / "attempts" / state["replay_attempt_id"]).is_dir())

    def test_qa_independence_and_replay(self):
        state = self.build(); qa = read_json(self.orch.store.execution_dir(state["execution_id"]) / "qa/QA_EVIDENCE_BUNDLE.json")
        self.assertTrue(qa["independent_of_factory"]); self.assertEqual(qa["candidate_sha256"], qa["replay_candidate_sha256"])

    def test_candidate_mutation_invalidates_final_reviews(self):
        state = self.build(); Path(state["candidate_path"]).write_bytes(Path(state["candidate_path"]).read_bytes() + b"mutation")
        with self.assertRaisesRegex(OrchestratorError, "Candidate changed"):
            self.orch.approve(state["execution_id"])

    def test_promotion_approval_candidate_binding(self):
        state = self.build(); state["candidate_sha256"] = "0" * 64; self.orch.store.save_execution(state)
        with self.assertRaises(OrchestratorError): self.orch.approve(state["execution_id"])

    def promotion_fixture(self):
        state = self.build(); root = self.orch.store.execution_dir(state["execution_id"])
        event = self.orch.approvals.write_promotion_approval(root, state, "sbm-admin")
        return state, self.orch.promotion.prepare(state, event)

    def test_crash_before_artifact_promotion(self):
        state, tx = self.promotion_fixture()
        with self.assertRaises(RuntimeError): self.orch.promotion.commit(tx, crash_at="before_artifact")
        self.assertEqual(self.orch.promotion.inspect_physical_state(tx), "NOT_APPLIED")

    def test_crash_after_artifact_before_registry(self):
        state, tx = self.promotion_fixture()
        with self.assertRaises(RuntimeError): self.orch.promotion.commit(tx, crash_at="after_artifact")
        self.assertEqual(self.orch.promotion.inspect_physical_state(tx), "ARTIFACT_APPLIED_REGISTRY_PENDING")

    def test_crash_after_registry_before_reconciliation(self):
        state, tx = self.promotion_fixture()
        with self.assertRaises(RuntimeError): self.orch.promotion.commit(tx, crash_at="after_registry")
        self.assertEqual(self.orch.promotion.inspect_physical_state(tx), "COMMITTED")

    def test_resume_promotion_transaction(self):
        state, tx = self.promotion_fixture()
        with self.assertRaises(RuntimeError): self.orch.promotion.commit(tx, crash_at="after_artifact")
        resumed = self.orch.promotion.resume(state["execution_id"])
        self.assertEqual(resumed["state"], "COMMITTED")

    def test_no_duplicate_final_registration(self):
        state, tx = self.promotion_fixture(); self.orch.promotion.commit(tx); self.orch.promotion.resume(state["execution_id"])
        registry = read_json(self.orch.promotion.registry_path)
        self.assertEqual(sum(a["execution_id"] == state["execution_id"] for a in registry["agents"]), 1)

    def test_reservation_consumed_only_completed_promotion(self):
        state = self.build(); ledger = read_json(self.orch.identity.path); reservation = next(r for r in ledger["reservations"] if r["execution_id"] == state["execution_id"])
        self.assertEqual(reservation["state"], "CONSUMING")
        promoted = self.orch.approve(state["execution_id"]); ledger = read_json(self.orch.identity.path); reservation = next(r for r in ledger["reservations"] if r["execution_id"] == state["execution_id"])
        self.assertEqual(promoted["state"], "PROMOTED"); self.assertEqual(reservation["state"], "CONSUMED")

    def test_forbidden_write_outside_agents(self):
        with self.assertRaisesRegex(OrchestratorError, "escapes agents"):
            self.orch.store.safe("..", "outside")

    def test_events_are_append_only_and_auditable(self):
        state = self.create(); events = (self.orch.store.execution_dir(state["execution_id"]) / "events.ndjson").read_text().splitlines()
        parsed = [json.loads(line) for line in events]
        self.assertGreater(len(parsed), 4)
        for event in parsed:
            self.assertTrue({"event_id", "execution_id", "actor", "action", "input_hashes", "output_hashes", "timestamp"} <= set(event))

    def test_status_all_and_single(self):
        state = self.create(); self.assertEqual(self.orch.status(state["execution_id"])["execution_id"], state["execution_id"])
        self.assertEqual(len(self.orch.status()), 1)

    def test_approval_view_binds_exact_subject(self):
        state = self.create(); view = self.orch.approval_view(state["execution_id"])
        self.assertEqual(view["gate"], "BUILD_APPROVAL"); self.assertEqual(view["prebuild_bundle_sha256"], state["prebuild_bundle_sha256"])

    def test_workflow_waits_for_real_darwin_decisions(self):
        state = self.raw_create()
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS")
        self.assertFalse((self.orch.store.execution_dir(state["execution_id"]) / "prebuild/SPEC_DECISIONS.json").exists())

    def test_fabricated_darwin_decisions_rejected(self):
        state = self.raw_create(); self.orch.principal_provider = StaticPrincipalProvider("orchestrator")
        with self.assertRaisesRegex(OrchestratorError, "authenticated Darwin"):
            self.orch.submit_spec_decisions(state["execution_id"], {})

    def test_autogenerated_review_passes_prohibited(self):
        state = self.raw_create(); root = self.orch.store.execution_dir(state["execution_id"])
        self.assertFalse((root / "prebuild/DARWIN_DESIGN_REVIEW_RECORD.json").exists())
        state = self.submit_decisions(state)
        self.assertFalse((root / "prebuild/DARWIN_DESIGN_REVIEW_RECORD.json").exists())
        self.assertEqual(state["pending_gate"], "DARWIN_DESIGN_REVIEW_RECORD")

    def test_wrong_reviewer_and_fake_noe_pass_rejected(self):
        state = self.submit_decisions(self.raw_create()); self.orch.principal_provider = StaticPrincipalProvider("Noe")
        with self.assertRaisesRegex(OrchestratorError, "authenticated Darwin"):
            self.orch.submit_review(state["execution_id"], {"verdict": "PASS", "subject_hashes": state["pending_review_subjects"]})
        state = self.submit_pending_review(state); self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        with self.assertRaisesRegex(OrchestratorError, "authenticated Noe"):
            self.orch.submit_review(state["execution_id"], {"verdict": "PASS", "subject_hashes": state["pending_review_subjects"]})

    def test_wrong_review_subject_rejected(self):
        state = self.submit_decisions(self.raw_create()); self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        with self.assertRaisesRegex(OrchestratorError, "current subjects"):
            self.orch.submit_review(state["execution_id"], {"verdict": "PASS", "subject_hashes": {"wrong": "0" * 64}})

    def test_explicit_valid_review_accepted_and_waits_for_noe(self):
        state = self.submit_decisions(self.raw_create()); state = self.submit_pending_review(state)
        self.assertEqual(state["pending_gate"], "NOE_PREBUILD_REVIEW_RECORD")
        self.assertFalse((self.orch.store.execution_dir(state["execution_id"]) / "prebuild/NOE_PREBUILD_REVIEW_RECORD.json").exists())

    def test_bare_cli_create_enters_dynamic_intake(self):
        output = io.StringIO()
        with redirect_stdout(output): self.assertEqual(cli_main(["create"], orchestrator=self.orch), 0)
        payload = json.loads(output.getvalue()); state = self.orch.status(payload["execution_id"])
        self.assertEqual(state["state"], "CAPTURING_INTENT"); self.assertIn("Qué agente", state["pending_question"])

    def test_normal_create_remains_fail_closed_for_historical_gepetto(self):
        identity = AgentIdentity("gepetto", "1.0.0", "Gepetto-v1.0.1-r3.zip", "99dc7d6f30872f5a0fb27f48acc309b6b9b31fb3ffe641305b86362c8e09d2a0", ())
        gepetto = ManualChatAgentExecutionAdapter(PackageIdentityVerifier(AGENTS_ROOT), identity, attestor=HMACResponseAttestor(b"g" * 32))
        orch = Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / "fail-closed", final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=gepetto, principal_provider=StaticPrincipalProvider("sbm-admin"))
        with self.assertRaisesRegex(OrchestratorError, "does not support") as raised:
            orch.create("Roberto: analiza resultados", principal="sbm-admin", idempotency_key="normal-gepetto")
        self.assertEqual(raised.exception.code, "AGENT_CAPABILITY_UNSUPPORTED")

    def test_valid_external_intent_brief_is_frozen_and_reaches_generator_flow(self):
        state = self.external_create()
        root = self.orch.store.execution_dir(state["execution_id"])
        self.assertEqual(state["state"], "PREBUILD")
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS")
        self.assertEqual((state["semantic_source"], state["intake_adapter"], state["intake_mode"]), ("sbm-admin", "Darwin", "DARWIN_TEMPORARY_INTAKE"))
        self.assertEqual(read_json(root / "intake/INTENT_BRIEF.json"), self.external_intent_brief())
        self.assertTrue(Path(state["generator_proposal_path"]).is_file())
        self.assertTrue((root / "prebuild/DARWIN_ARCHITECTURE_REQUEST.json").is_file())
        self.assertFalse((root / "prebuild/SPEC_DECISIONS.json").exists())
        self.assertFalse((root / "approved").exists())
        self.assertFalse((root / "attempts").exists())
        with self.assertRaisesRegex(OrchestratorError, "Immutable"):
            self.orch.store.write_immutable(state["execution_id"], "intake/INTENT_BRIEF.json", self.external_intent_brief())

    def test_external_intent_brief_invalid_schema_fails(self):
        intent = self.external_intent_brief(); intent.pop("desired_outcome")
        key = "invalid-external-retry"
        with self.assertRaises(OrchestratorError) as raised: self.external_create(intent, key=key)
        self.assertEqual(raised.exception.code, "INTENT_BRIEF_SCHEMA_INVALID")
        with self.assertRaises(OrchestratorError) as retried: self.external_create(intent, key=key)
        self.assertEqual(retried.exception.code, "INTENT_BRIEF_SCHEMA_INVALID")

    def test_external_intent_brief_missing_or_incorrect_provenance_fails(self):
        missing = self.external_intent_brief(); missing.pop("provenance")
        wrong = self.external_intent_brief(provenance={"semantic_source": "sbm-admin", "intake_adapter": "Noe", "intake_mode": "DARWIN_TEMPORARY_INTAKE"})
        for label, intent in (("missing", missing), ("wrong", wrong)):
            with self.subTest(label=label), self.assertRaises(OrchestratorError) as raised: self.external_create(intent)
            self.assertEqual(raised.exception.code, "INTENT_BRIEF_PROVENANCE_INVALID")

    def test_external_intake_adapter_not_authorized_fails(self):
        with self.assertRaises(OrchestratorError) as raised: self.external_create(mode="NOE_TEMPORARY_INTAKE")
        self.assertEqual(raised.exception.code, "INTAKE_ADAPTER_UNAUTHORIZED")

    def test_external_intent_semantic_source_must_be_sbm_admin(self):
        intent = self.external_intent_brief(provenance={"semantic_source": "Darwin", "intake_adapter": "Darwin", "intake_mode": "DARWIN_TEMPORARY_INTAKE"})
        with self.assertRaises(OrchestratorError) as raised: self.external_create(intent)
        self.assertEqual(raised.exception.code, "INTENT_BRIEF_PROVENANCE_INVALID")

    def test_external_intake_does_not_execute_gepetto(self):
        class ForbiddenGepetto:
            def request_intake(inner, request, execution_dir): raise AssertionError("external intake executed Gepetto")
        orch = Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / "no-gepetto", final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=ForbiddenGepetto(), principal_provider=StaticPrincipalProvider("sbm-admin"))
        state = orch.create_from_intent_brief(self.external_intent_brief(), intake_mode="DARWIN_TEMPORARY_INTAKE", principal="sbm-admin", idempotency_key="no-gepetto")
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS")

    def generator_recovery_fixture(self, suffix="generator-recovery"):
        class FailOnceGenerator:
            def __init__(inner): inner.calls = 0; inner.delegate = InProcessGeneratorAdapter()
            def generate(inner, execution_dir, generator_input, profile):
                inner.calls += 1
                if inner.calls == 1: raise OrchestratorError("GENERATOR_FAILED", "injected recoverable operational failure")
                return inner.delegate.generate(execution_dir, generator_input, profile)
        class ForbiddenGepetto:
            def request_intake(inner, request, execution_dir): raise AssertionError("resume executed Gepetto")
        generator = FailOnceGenerator()
        orch = Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / suffix, final_root=self.final), generator=generator, factory=InProcessFactoryAdapter(), gepetto_adapter=ForbiddenGepetto(), principal_provider=StaticPrincipalProvider("sbm-admin"))
        with self.assertRaises(OrchestratorError) as raised:
            orch.create_from_intent_brief(self.external_intent_brief(), intake_mode="DARWIN_TEMPORARY_INTAKE", principal="sbm-admin", idempotency_key=suffix)
        self.assertEqual(raised.exception.code, "GENERATOR_FAILED")
        blocked = orch.status()[0]
        return orch, generator, blocked

    def test_resume_recoverable_generator_failure_preserves_frozen_checkpoint(self):
        orch, generator, blocked = self.generator_recovery_fixture()
        execution_id = blocked["execution_id"]; reservation = dict(blocked["identity"]); intent_sha = blocked["intent_brief_sha256"]; intent_bytes = Path(blocked["intent_brief_path"]).read_bytes()
        recovered = orch.resume(execution_id)
        self.assertEqual(recovered["execution_id"], execution_id)
        self.assertEqual(recovered["identity"], reservation)
        self.assertEqual(recovered["identity"]["reservation_id"], reservation["reservation_id"])
        self.assertEqual(recovered["intent_brief_sha256"], intent_sha)
        self.assertEqual(Path(recovered["intent_brief_path"]).read_bytes(), intent_bytes)
        self.assertEqual(recovered["pending_gate"], "DARWIN_SPEC_DECISIONS")
        self.assertNotIn("last_error", recovered)
        self.assertEqual(generator.calls, 2)
        root = orch.store.execution_dir(execution_id)
        self.assertEqual(len(list(root.glob("build/scaffolds/*/AGENT_PROPOSAL.yaml"))), 1)
        ledger = read_json(orch.identity.path)
        self.assertEqual([item["reservation_id"] for item in ledger["reservations"]], [reservation["reservation_id"]])
        again = orch.resume(execution_id)
        self.assertEqual(again["execution_id"], execution_id)
        self.assertEqual(again["identity"], reservation)
        self.assertEqual(generator.calls, 2)
        self.assertEqual(len(list(root.glob("build/scaffolds/*/AGENT_PROPOSAL.yaml"))), 1)

    def test_resume_capability_block_remains_fail_closed(self):
        identity = AgentIdentity("gepetto", "1.0.0", "Gepetto-v1.0.1-r3.zip", "99dc7d6f30872f5a0fb27f48acc309b6b9b31fb3ffe641305b86362c8e09d2a0", ())
        gepetto = ManualChatAgentExecutionAdapter(PackageIdentityVerifier(AGENTS_ROOT), identity, attestor=HMACResponseAttestor(b"g" * 32))
        orch = Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / "capability-resume", final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=gepetto, principal_provider=StaticPrincipalProvider("sbm-admin"))
        with self.assertRaises(OrchestratorError): orch.create("Roberto: analiza", principal="sbm-admin", idempotency_key="capability-resume")
        blocked = orch.status()[0]; resumed = orch.resume(blocked["execution_id"])
        self.assertEqual(resumed["state"], "BLOCKED")
        self.assertEqual(resumed["last_error"]["code"], "AGENT_CAPABILITY_UNSUPPORTED")

    def test_resume_integrity_auth_and_governance_blocks_remain_fail_closed(self):
        for code in ("INTEGRITY_CHECK_FAILED", "UNAUTHORIZED_SUBMISSION", "CONTRACT_DELTA"):
            with self.subTest(code=code):
                orch, generator, blocked = self.generator_recovery_fixture("non-recoverable-" + code.lower())
                blocked["last_error"] = {"code": code, "message": "non-recoverable"}; orch.store.save_execution(blocked)
                resumed = orch.resume(blocked["execution_id"])
                self.assertEqual(resumed["state"], "BLOCKED")
                self.assertEqual(resumed["last_error"]["code"], code)
                self.assertEqual(generator.calls, 1)

    def test_resume_generator_error_at_wrong_checkpoint_remains_fail_closed(self):
        orch, generator, blocked = self.generator_recovery_fixture("wrong-generator-checkpoint")
        blocked["generator_proposal_sha256"] = "a" * 64
        orch.store.save_execution(blocked)
        resumed = orch.resume(blocked["execution_id"])
        self.assertEqual(resumed["state"], "BLOCKED")
        self.assertEqual(resumed["last_error"]["code"], "GENERATOR_FAILED")
        self.assertEqual(generator.calls, 1)

    def test_external_intent_cli_accepts_file_or_json(self):
        output = io.StringIO(); payload = json.dumps(self.external_intent_brief())
        with redirect_stdout(output):
            self.assertEqual(cli_main(["create", "--intent-brief", payload, "--intake-adapter", "DARWIN_TEMPORARY_INTAKE"], orchestrator=self.orch), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(self.orch.status(result["execution_id"])["pending_gate"], "DARWIN_SPEC_DECISIONS")

    def test_complete_brief_skips_redundant_question_and_parses_name(self):
        state = self.raw_create(brief="Quiero crear un agente llamado Roberto que analice resultados de negocio")
        self.assertEqual(state["state"], "PREBUILD"); self.assertEqual(state["identity"]["canonical_agent_name"], "Roberto Agent"); self.assertNotIn("pending_question", state)

    def governed_orchestrator(self, modifier):
        profiles = self.copied_profiles(); profile = read_json(profiles / "creation-profile-v1.json"); modifier(profile); atomic_write_json(profiles / "creation-profile-v1.json", profile)
        activation = read_json(profiles / "activation.json"); activation["active_profiles"][0]["sha256"] = sha256_file(profiles / "creation-profile-v1.json"); atomic_write_json(profiles / "activation.json", activation)
        return Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / sortable_id("policy_"), profile_root=profiles, final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=TestAgentExecutionAdapter("gepetto"), principal_provider=StaticPrincipalProvider("sbm-admin"))

    def test_conditional_question_only_when_policy_requires_it(self):
        orch = self.governed_orchestrator(lambda p: p["field_source_policy"]["conditional_required"].append("style"))
        state = orch.create("Roberto: analiza resultados de negocio", principal="p", idempotency_key="conditional")
        self.assertEqual(state["state"], "CAPTURING_INTENT"); self.assertEqual(state["unresolved_human_semantic_requirements"][0]["field"], "style")

    def test_new_deterministic_field_does_not_change_gepetto(self):
        orch = self.governed_orchestrator(lambda p: p["field_source_policy"]["fields"].update({"NEW_PARAMETER_X": "DETERMINISTIC"}))
        state = orch.create("Roberto: analiza resultados de negocio", principal="p", idempotency_key="new-field")
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS")

    def test_referenced_final_agent_mutation_invalidates_workflow(self):
        registry = {"revision": 1, "agents": [{"agent_id": "Alpha-Agent", "agent_name": "Alpha Agent", "agent_version": "1.0.0", "metadata_sha256": "a" * 64}]}
        atomic_write_json(self.orch.store.state / "final-agent-registry.json", registry)
        state = self.create(brief="Roberto: analiza resultados con Alpha-Agent", relationships=[{"agent_id": "Alpha-Agent"}])
        self.assertEqual(state["relevant_agent_ids"], ["Alpha-Agent"])
        registry["revision"] = 2; registry["agents"][0]["metadata_sha256"] = "b" * 64; atomic_write_json(self.orch.store.state / "final-agent-registry.json", registry)
        self.orch.principal_provider = StaticPrincipalProvider("sbm-admin")
        with self.assertRaisesRegex(OrchestratorError, "ECOSYSTEM_RELEVANT_DELTA"):
            self.orch.approve(state["execution_id"])

    def test_tampered_generator_runtime_blocked(self):
        profile, _ = self.orch.profiles.resolve(); execution = self.test_root / "runtime-binding-generator"; execution.mkdir()
        runtime = PinnedZipRuntime.prepare(execution, AGENTS_ROOT, profile["bindings"]["generator"], "generator"); (runtime / "unexpected.txt").write_text("tamper")
        with self.assertRaisesRegex(OrchestratorError, "does not exactly match"):
            PinnedZipRuntime.prepare(execution, AGENTS_ROOT, profile["bindings"]["generator"], "generator")

    def test_tampered_factory_runtime_blocked(self):
        profile, _ = self.orch.profiles.resolve(); execution = self.test_root / "runtime-binding-factory"; execution.mkdir()
        runtime = PinnedZipRuntime.prepare(execution, AGENTS_ROOT, profile["bindings"]["factory"], "factory"); source = next((runtime / "src").rglob("*.py")); source.write_text(source.read_text() + "\n# tamper\n")
        with self.assertRaisesRegex(OrchestratorError, "does not exactly match"):
            PinnedZipRuntime.prepare(execution, AGENTS_ROOT, profile["bindings"]["factory"], "factory")

    def test_stateful_multiturn_intake_reaches_prebuild(self):
        state = self.orch.create(None, principal="p", idempotency_key="multi-turn")
        state = self.orch.submit_intent(state["execution_id"], "El agente se llama Roberto")
        self.assertEqual(state["state"], "CAPTURING_INTENT"); progress = read_json(self.orch.store.execution_dir(state["execution_id"]) / "intake/INTENT_PROGRESS.json"); self.assertEqual(progress["values"]["requested_name"], "Roberto")
        state = self.orch.submit_intent(state["execution_id"], "Quiero que analice resultados del negocio y entregue recomendaciones")
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS"); intent = read_json(state["intent_brief_path"]); self.assertEqual(intent["requested_name"], "Roberto"); self.assertIn("analice resultados", intent["desired_outcome"])
        self.assertIn("requested_name", intent["intent_progress"]["field_provenance"])

    def test_natural_name_forms(self):
        forms = ["El agente se llama Roberto", "Agente llamado Roberto", "el nombre es Roberto", "quiero crear Roberto", "quiero crear un agente Roberto", "es el agente Roberto"]
        adapter = TestAgentExecutionAdapter("gepetto")
        for phrase in forms:
            request = {"free_form_text": phrase, "current_intent_progress": {}, "directed_question": None}
            with self.subTest(phrase=phrase): self.assertEqual(adapter.request_intake(request, self.test_root).payload["fields"]["requested_name"], "Roberto")

    def test_darwin_human_decision_clarification_preserves_identity(self):
        state = self.raw_create(); reservation = dict(state["identity"]); self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        state = self.orch.submit_spec_decisions(state["execution_id"], {"status": "HUMAN_DECISION_REQUIRED", "architecture_request_sha256": state["darwin_architecture_request_sha256"], "question": "¿Debe limitarse a recomendaciones no vinculantes?"})
        self.assertEqual(state["state"], "CAPTURING_INTENT"); state = self.orch.submit_intent(state["execution_id"], "Sí, solo recomendaciones no vinculantes")
        self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS"); self.assertEqual(state["identity"], reservation); self.assertIn("recomendaciones no vinculantes", read_json(state["intent_brief_path"])["clarifications"][0])

    def test_spec_decisions_roundtrip_to_materialized_contracts(self):
        state = self.raw_create(); distinctive = {
            "authority": ["TEST-PERMISSION-X"], "permissions": ["TEST-PERMISSION-X"], "required_context": ["TEST-CONTEXT-X"],
            "relationships": [{"actor": "TEST-RELATIONSHIP-X", "relationship_type": "ADVISOR", "direction": "BIDIRECTIONAL", "purpose": "TEST-PURPOSE-X"}],
            "hierarchy": {"reports_to": "TEST-REPORTS-X", "can_request_from": ["TEST-REQUEST-X"], "can_instruct": ["TEST-INSTRUCT-X"], "requires_approval_from": ["sbm-admin"], "escalation_target": "TEST-ESCALATION-TARGET-X"},
            "retrieval_strategy": "TEST-RETRIEVAL-X", "embedding_strategy": "TEST-EMBEDDING-X", "execution_modes": ["TEST-MODE-X"], "asynchronous_capabilities": ["TEST-ASYNC-X"], "execution_dependencies": ["TEST-DEPENDENCY-X"], "outputs": ["TEST-OUTPUT-X"], "escalation_rules": ["TEST-ESCALATION-X"], "deployment": {"target": "OPENAI_API", "enabled": True}, "qa": ["TEST-QA-X"], "runtime": {"context_delivery": "TEST-DELIVERY-X", "idempotency": "TEST-IDEMPOTENCY-X", "caching_policy": "TEST-CACHE-X"}, "security_boundaries": ["TEST-SECURITY-X"],
        }
        state = self.submit_decisions(state, overrides=distinctive); state = self.submit_pending_review(state); state = self.submit_pending_review(state); self.orch.principal_provider = StaticPrincipalProvider("sbm-admin"); state = self.orch.approve(state["execution_id"]); out = Path(state["candidate_path"]).parents[1] / "output"
        self.assertIn("TEST-RELATIONSHIP-X", (out / "config/RELATIONSHIPS.yaml").read_text()); self.assertIn("TEST-REPORTS-X", (out / "config/HIERARCHY.yaml").read_text()); self.assertIn("TEST-PERMISSION-X", (out / "config/PERMISSIONS.yaml").read_text()); self.assertIn("TEST-OUTPUT-X", (out / "AGENT_DEFINITION.yaml").read_text()); self.assertIn("TEST-QA-X", (out / "AGENT_DEFINITION.yaml").read_text()); self.assertIn("TEST-CACHE-X", (out / "config/RUNTIME_PROFILE.yaml").read_text()); self.assertIn("TEST-CONTEXT-X", (out / "config/CONTEXT_CONTRACT.yaml").read_text()); self.assertIn("TEST-SECURITY-X", (out / "AGENT_DEFINITION.yaml").read_text()); self.assertTrue((out / "deployment/DEPLOYMENT_PROFILE.yaml").is_file())

    def routed_orchestrator(self, architecture=None, darwin=None, noe=None):
        darwin_adapter = TestAgentExecutionAdapter("Darwin"); noe_adapter = TestAgentExecutionAdapter("Noe")
        return Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / sortable_id("routed_"), final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=TestAgentExecutionAdapter("gepetto"), principal_provider=UnixPrincipalProvider(PACKAGE_ROOT / "config/authenticated-principals.json", AGENTS_ROOT), architecture_adapter=architecture or darwin_adapter, darwin_review_adapter=darwin or darwin_adapter, noe_review_adapter=noe or noe_adapter, auto_route_agents=True)

    def test_real_adapters_route_architecture_and_prebuild_reviews(self):
        orch = self.routed_orchestrator(); state = orch.create("Roberto: analiza resultados de negocio", principal="local:operator", idempotency_key="routed")
        self.assertEqual(state["state"], "WAITING_BUILD_APPROVAL"); root = orch.store.execution_dir(state["execution_id"]); self.assertTrue((root / "prebuild/SPEC_DECISIONS.json").is_file()); self.assertTrue((root / "prebuild/DARWIN_DESIGN_REVIEW_RECORD.json").is_file()); self.assertTrue((root / "prebuild/NOE_PREBUILD_REVIEW_RECORD.json").is_file())

    def test_real_adapters_route_final_reviews_without_static_principal(self):
        orch = self.routed_orchestrator(); state = orch.create("Roberto: analiza resultados de negocio", principal="local:operator", idempotency_key="routed-final"); state = orch.approve(state["execution_id"])
        self.assertEqual(state["state"], "WAITING_PROMOTION_APPROVAL"); root = orch.store.execution_dir(state["execution_id"]); self.assertTrue((root / "final-review/DARWIN_FUNCTIONAL_REVIEW_RECORD.json").is_file()); self.assertTrue((root / "final-review/NOE_FINAL_FUNCTIONAL_REVIEW_RECORD.json").is_file())

    def test_fake_adapter_identity_rejected(self):
        class Fake:
            def request_architecture(inner, request, execution_dir): return RoutedAgentResponse("Mallory", "fake", True, {"status": "RESOLVED", "architecture_request_sha256": request["request_sha256"], "decisions": {}})
        orch = self.routed_orchestrator(architecture=Fake())
        with self.assertRaisesRegex(OrchestratorError, "authenticated Darwin"): orch.create("Roberto: analiza resultados", principal="p", idempotency_key="fake")

    def test_adapter_subject_mutation_rejected(self):
        class MutatingReview:
            def request_review(inner, request, execution_dir): return RoutedAgentResponse("Darwin", "mutating", True, {"verdict": "PASS", "subject_hashes": {"mutated": "0" * 64}})
        orch = self.routed_orchestrator(darwin=MutatingReview())
        with self.assertRaisesRegex(OrchestratorError, "current subjects"): orch.create("Roberto: analiza resultados", principal="p", idempotency_key="mutated")

    def test_manual_chat_emits_request_and_rejects_unverified_import(self):
        verifier = PackageIdentityVerifier(AGENTS_ROOT); manual = ManualChatAgentExecutionAdapter(verifier, AgentIdentity("darwin", "1.2.0", "Darwin-v0_1_0.zip", "45661d31e355f428bc2ac8cbbb5a5196d2f1606c6644fc35078c6840722d3c86", ("DARWIN_ARCHITECTURE_REQUEST/v1", "SPEC_DECISIONS/v1")), attestor=HMACResponseAttestor(b"d" * 32)); orch = Orchestrator(OrchestratorConfig(AGENTS_ROOT, runtime_root=self.test_root / "manual", final_root=self.final), generator=InProcessGeneratorAdapter(), factory=InProcessFactoryAdapter(), gepetto_adapter=TestAgentExecutionAdapter("gepetto"), principal_provider=UnixPrincipalProvider(PACKAGE_ROOT / "config/authenticated-principals.json", AGENTS_ROOT), architecture_adapter=manual, auto_route_agents=True)
        state = orch.create("Roberto: analiza resultados", principal="p", idempotency_key="manual"); self.assertEqual(state["pending_gate"], "DARWIN_SPEC_DECISIONS"); self.assertEqual(len(list((orch.store.execution_dir(state["execution_id"]) / "routing").glob("*.json"))), 1)
        with self.assertRaises(OrchestratorError): orch.import_agent_response(state["execution_id"], {"agent_id": "darwin"})

    def manual_response_fixture(self):
        identity = AgentIdentity("darwin", "1.2.0", "Darwin-v0_1_0.zip", "45661d31e355f428bc2ac8cbbb5a5196d2f1606c6644fc35078c6840722d3c86", ("AGENT_REVIEW_REQUEST/v1", "AGENT_REVIEW_RESPONSE/v1")); attestor = HMACResponseAttestor(b"t" * 32); adapter = ManualChatAgentExecutionAdapter(PackageIdentityVerifier(AGENTS_ROOT), identity, "Darwin", attestor); pending = adapter.request_review({"contract": "AGENT_REVIEW_REQUEST/v1", "subject_hashes": {"x": "a" * 64}}, self.test_root)
        envelope = {"agent_id": "darwin", "agent_version": "1.2.0", "package_sha256": identity.package_sha256, "request_sha256": pending["request_sha256"], "response_kind": "REVIEW", "response_contract": "AGENT_REVIEW_RESPONSE/v1", "response": {"contract": "AGENT_REVIEW_RESPONSE/v1", "verdict": "PASS", "subject_hashes": {"x": "a" * 64}}}
        request_package = read_json(pending["request_path"]); envelope["provenance"] = attestor.provenance(envelope, request_package["attestation"]["nonce"])
        return adapter, pending, envelope

    def test_manual_response_wrong_identity_fails(self):
        adapter, pending, envelope = self.manual_response_fixture(); envelope["agent_id"] = "noe"
        with self.assertRaisesRegex(OrchestratorError, "identity mismatch"): adapter.import_response(envelope, pending["request_sha256"])

    def test_manual_response_wrong_package_sha_fails(self):
        adapter, pending, envelope = self.manual_response_fixture(); envelope["package_sha256"] = "0" * 64
        with self.assertRaisesRegex(OrchestratorError, "package SHA"): adapter.import_response(envelope, pending["request_sha256"])

    def test_manual_response_wrong_request_sha_fails(self):
        adapter, pending, envelope = self.manual_response_fixture(); envelope["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(OrchestratorError, "request SHA"): adapter.import_response(envelope, pending["request_sha256"])

    def test_manual_response_wrong_schema_fails(self):
        adapter, pending, envelope = self.manual_response_fixture(); envelope["response"] = {"verdict": "MAYBE"}
        with self.assertRaisesRegex(OrchestratorError, "schema is invalid"): adapter.import_response(envelope, pending["request_sha256"])

    def test_gepetto_package_identity_and_accumulator_separation(self):
        verified = PackageIdentityVerifier(AGENTS_ROOT).verify(AgentIdentity("gepetto", "1.0.0", "Gepetto-v1.0.1-r3.zip", "99dc7d6f30872f5a0fb27f48acc309b6b9b31fb3ffe641305b86362c8e09d2a0"))
        self.assertEqual(verified["package_sha256"], "99dc7d6f30872f5a0fb27f48acc309b6b9b31fb3ffe641305b86362c8e09d2a0"); self.assertFalse(hasattr(PackageIdentityVerifier(AGENTS_ROOT), "request_review")); self.assertFalse(hasattr(self.orch.intake, "interpret"))

    def test_routed_capability_contract_positive_and_negative(self):
        verifier = PackageIdentityVerifier(AGENTS_ROOT); base = ("darwin", "1.2.0", "Darwin-v0_1_0.zip", "45661d31e355f428bc2ac8cbbb5a5196d2f1606c6644fc35078c6840722d3c86")
        with self.assertRaisesRegex(OrchestratorError, "does not support"):
            verifier.verify(AgentIdentity(*base, ("AGENT_REVIEW_REQUEST/v1",)), "DARWIN_ARCHITECTURE_REQUEST/v1")
        identity = AgentIdentity(*base, ("AGENT_REVIEW_REQUEST/v1", "AGENT_REVIEW_RESPONSE/v1")); adapter = ManualChatAgentExecutionAdapter(verifier, identity, attestor=HMACResponseAttestor(b"c" * 32))
        with self.assertRaisesRegex(OrchestratorError, "Expected AGENT_REVIEW_REQUEST/v1"):
            adapter.request_review({"contract": "AGENT_REVIEW_REQUEST/v2"}, self.test_root)
        pending = adapter.request_review({"contract": "AGENT_REVIEW_REQUEST/v1", "subject_hashes": {}}, self.test_root)
        self.assertTrue(pending["waiting"])

    def test_historical_gepetto_is_not_intake_capable(self):
        identity = AgentIdentity("gepetto", "1.0.0", "Gepetto-v1.0.1-r3.zip", "99dc7d6f30872f5a0fb27f48acc309b6b9b31fb3ffe641305b86362c8e09d2a0", ())
        adapter = ManualChatAgentExecutionAdapter(PackageIdentityVerifier(AGENTS_ROOT), identity, attestor=HMACResponseAttestor(b"g" * 32))
        with self.assertRaisesRegex(OrchestratorError, "does not support"):
            adapter.request_intake({"contract": "GEPETTO_INTAKE_REQUEST/v1"}, self.test_root)

    def test_manual_response_requires_valid_provenance_and_rejects_replay(self):
        adapter, pending, envelope = self.manual_response_fixture(); unsigned = dict(envelope); unsigned.pop("provenance")
        with self.assertRaisesRegex(OrchestratorError, "requires trusted provenance"): adapter.import_response(unsigned, pending["request_sha256"])
        forged = dict(envelope); forged["provenance"] = dict(forged["provenance"]); forged["provenance"]["signature"] = "0" * 64
        with self.assertRaisesRegex(OrchestratorError, "signature is invalid"): adapter.import_response(forged, pending["request_sha256"])
        accepted = adapter.import_response(envelope, pending["request_sha256"]); self.assertTrue(accepted.authenticated)
        with self.assertRaisesRegex(OrchestratorError, "already consumed"): adapter.import_response(envelope, pending["request_sha256"])

    def test_review_input_bundle_integrity_complete_and_tamper(self):
        state = self.submit_decisions(self.raw_create()); bundle = read_json(state["pending_review_input_bundle_path"])
        self.assertTrue({"INTENT_BRIEF", "AGENT_PROPOSAL", "SPEC_DECISIONS", "AGENT_SPEC", "BUILD_CONTEXT_SNAPSHOT", "PREBUILD_BUNDLE", "NORMATIVE_STANDARD"} <= set(bundle["items"]))
        self.assertEqual(self.orch._verify_review_input_bundle(state)["review_input_bundle_sha256"], state["pending_review_input_bundle_sha256"])
        bundle["items"]["AGENT_SPEC"]["content"] += "A"; atomic_write_json(state["pending_review_input_bundle_path"], bundle)
        self.orch.principal_provider = StaticPrincipalProvider("Darwin")
        with self.assertRaisesRegex(OrchestratorError, "Review input bundle"): self.orch.submit_review(state["execution_id"], {"verdict": "PASS", "subject_hashes": state["pending_review_subjects"]})

    def test_review_input_bundle_incomplete_fails_even_with_recomputed_hash(self):
        state = self.submit_decisions(self.raw_create()); bundle = read_json(state["pending_review_input_bundle_path"]); bundle["items"].pop("AGENT_SPEC"); bundle.pop("review_input_bundle_sha256"); bundle["review_input_bundle_sha256"] = sha256_object(bundle); state["pending_review_input_bundle_sha256"] = bundle["review_input_bundle_sha256"]; self.orch.store.save_execution(state); atomic_write_json(state["pending_review_input_bundle_path"], bundle)
        with self.assertRaisesRegex(OrchestratorError, "incomplete"): self.orch._verify_review_input_bundle(state)

    def test_intake_registry_a_then_material_b_is_not_no_delta(self):
        registry = {"revision": 1, "agents": [{"agent_id": "Alpha-Agent", "agent_version": "1.0.0", "metadata_sha256": "a" * 64}]}; atomic_write_json(self.orch.store.state / "final-agent-registry.json", registry)
        state = self.raw_create(); registry["revision"] = 2; registry["agents"][0]["metadata_sha256"] = "b" * 64; atomic_write_json(self.orch.store.state / "final-agent-registry.json", registry)
        state = self.submit_decisions(state, relationships=[{"agent_id": "Alpha-Agent"}]); self.assertEqual(self.orch.freshness(state["execution_id"])["classification"], "ECOSYSTEM_RELEVANT_DELTA")

    def test_final_registry_conflict_blocks_empty_ledger(self):
        atomic_write_json(self.orch.identity.path, {"revision": 0, "next_sequence": 1, "reservations": []}); atomic_write_json(self.orch.store.state / "final-agent-registry.json", {"revision": 1, "agents": [{"agent_id": "Roberto-Agent", "agent_version": "1.0.0"}]})
        with self.assertRaisesRegex(OrchestratorError, "already registered"): self.orch.identity.reserve("new-execution", "Roberto")

    def test_build_approval_preserves_authentication_provenance(self):
        state = self.create(); self.orch.approve(state["execution_id"]); event = read_json(self.orch.store.execution_dir(state["execution_id"]) / "BUILD_APPROVAL_EVENT.json")
        self.assertTrue({"authenticated_principal", "authentication_provider_method", "authentication_session_reference", "authentication_timestamp", "execution_id", "build_context_snapshot_sha256", "prebuild_bundle_sha256", "proposal_identity", "proposal_sha256", "spec_identity", "spec_sha256", "human_decision_id", "decision_timestamp"} <= set(event))

    def test_factory_authorization_all_bindings(self):
        state = self.create(); self.orch.approve(state["execution_id"]); root = self.orch.store.execution_dir(state["execution_id"]); profile, _ = self.orch.profiles.resolve(); template = AGENTS_ROOT / profile["bindings"]["template"]["path"]
        auth_path = root / "approved/FACTORY_AUTHORIZATION.json"; self.assertEqual(verify_factory_authorization(auth_path, root, root / "approved", root / "prebuild", template, state["identity"]["reservation_id"])["execution_id"], state["execution_id"])
        for field, value in (("execution_id", "wrong"), ("reservation_id", "wrong"), ("prebuild_bundle_sha256", "0" * 64), ("approved_proposal_projection_sha256", "0" * 64), ("build_approval_event_sha256", "0" * 64)):
            with self.subTest(field=field):
                auth = read_json(auth_path); auth[field] = value; auth.pop("authorization_sha256"); auth["authorization_sha256"] = sha256_object(auth); mutated = self.test_root / f"auth-{field}.json"; atomic_write_json(mutated, auth)
                with self.assertRaisesRegex(OrchestratorError, "mismatch"): verify_factory_authorization(mutated, root, root / "approved", root / "prebuild", template, state["identity"]["reservation_id"])

    def test_explicit_responsibilities_and_style_survive_materialization(self):
        state = self.orch.create(None, principal="local:operator", idempotency_key="semantic-roundtrip"); update = {"contract": "STRUCTURED_INTENT_UPDATE/v1", "fields": {"requested_name": "Roberto", "desired_outcome": "analizar negocio", "responsibilities": ["valor distintivo"], "style": "frío y directo"}}
        state = self.orch._accept_intent_update(state, update, "gepetto-intake-v2", "trusted-test", "a" * 64); state = self.submit_decisions(state); state = self.submit_pending_review(state); state = self.submit_pending_review(state); self.orch.principal_provider = StaticPrincipalProvider("sbm-admin"); state = self.orch.approve(state["execution_id"]); output = Path(state["candidate_path"]).parents[1] / "output"; definition = __import__("yaml").safe_load((output / "AGENT_DEFINITION.yaml").read_text())
        self.assertIn("valor distintivo", definition["responsibilities"]); self.assertEqual(definition["communication_style"], "frío y directo")


if __name__ == "__main__":
    unittest.main()
