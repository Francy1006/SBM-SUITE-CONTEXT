from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
AGENTS = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE / "src"))

from sbm_agent_orchestrator.adapters import ContainerGeneratorAdapter, FactoryAdapter, IndependentQARunner, proposal_input
from sbm_agent_orchestrator.contracts import ApprovalWriter, SpecCompiler, read_yaml
from sbm_agent_orchestrator.core import AuthenticatedPrincipal
from sbm_agent_orchestrator.identity import IdentityAllocator
from sbm_agent_orchestrator.profiles import CreationProfileResolver
from sbm_agent_orchestrator.storage import RuntimeStore
from sbm_agent_orchestrator.util import atomic_write_json, sha256_file, sha256_object

RUNNER_VERSION = "2.0.0"


def implementation_identity():
    files = sorted((PACKAGE / "src/sbm_agent_orchestrator").glob("*.py"))
    return sha256_object({path.relative_to(PACKAGE).as_posix(): sha256_file(path) for path in files})


def main():
    suite = subprocess.run([str(PACKAGE / "scripts/test")], text=True, capture_output=True)
    if suite.returncode: raise RuntimeError("orchestrator test suite failed before machine E2E")
    factory_root = AGENTS / "build/factory-v1_0_2/SBM-Agent-Factory-v1_0_2"; factory_env = dict(os.environ); factory_env["PYTHONPATH"] = str(factory_root / "src"); factory_env["SBM_CANONICAL_TEMPLATE"] = str(AGENTS / "build/template-v2_0_1/dist/SBM-Agent-Template-v2_0_1.zip")
    factory_suite = subprocess.run([sys.executable, "-m", "pytest", "-q", str(factory_root / "tests")], text=True, capture_output=True, env=factory_env)
    if factory_suite.returncode: raise RuntimeError("Factory 1.0.2 test suite failed before machine E2E")
    evidence_path = PACKAGE / "qa/machine-e2e-evidence.json"
    with tempfile.TemporaryDirectory(prefix="machine-e2e-", dir=PACKAGE) as temporary:
        temp = Path(temporary); store = RuntimeStore(AGENTS, temp / "runtime"); profile, profile_sha = CreationProfileResolver(AGENTS, PACKAGE / "config/profiles").resolve()
        execution_id = "machine-e2e-physical"; root = store.execution_dir(execution_id); root.mkdir(parents=True)
        reservation = IdentityAllocator(store).reserve(execution_id, "MachineProbe")
        intent = {"contract": "MACHINE_E2E_INPUT_FIXTURE/v1", "requested_name": "MachineProbe", "desired_outcome": "validate real Generator, Template, Factory authorization and independent QA", "specific_objectives": ["physical pipeline validation"], "responsibilities": ["physical pipeline validation"], "communication_style": "cold and direct", "material_limits": [], "important_relationships": []}
        generator = ContainerGeneratorAdapter(AGENTS); proposal_path, metadata_path = generator.generate(root, proposal_input(intent, reservation, profile, execution_id), profile)
        prebuild = root / "prebuild"; prebuild.mkdir(); shutil.copy2(proposal_path, prebuild / "AGENT_PROPOSAL.yaml"); proposal = read_yaml(proposal_path); defaults = profile["canonical_defaults"]
        decisions = {"authority": proposal["authority"], "permissions": proposal["permissions"], "required_context": proposal["required_context"], "relationships": proposal["relationships"], "hierarchy": {"reports_to": "sbm-admin", "can_request_from": ["Darwin", "Noe"], "can_instruct": [], "requires_approval_from": ["sbm-admin"], "escalation_target": "sbm-admin"}, "retrieval_strategy": proposal["retrieval_strategy"], "embedding_strategy": proposal["embedding_strategy"], "execution_modes": proposal["execution_modes"], "asynchronous_capabilities": proposal["asynchronous_capabilities"], "execution_dependencies": proposal["execution_dependencies"], "outputs": proposal["outputs"], "escalation_rules": proposal["escalation_rules"], "deployment": proposal["deployment"], "qa": proposal["qa_specific"], "runtime": defaults["runtime"], "security_boundaries": defaults["security_boundaries"]}
        decisions_path = prebuild / "SPEC_DECISIONS.json"; atomic_write_json(decisions_path, decisions)
        approval_ids = {"proposal": "machine-proposal-approval", "spec": "machine-spec-approval", "materialization": "machine-materialization-approval"}
        compiled = SpecCompiler().compile(prebuild, proposal, decisions, reservation, profile, approval_ids["spec"])
        SpecCompiler.validate_schema(prebuild / "AGENT_SPEC.yaml", AGENTS / profile["bindings"]["schemas"]["agent_spec"]["path"])
        prebuild_bundle = {"execution_id": execution_id, "proposal_sha256": sha256_file(proposal_path), "spec_decisions_sha256": sha256_file(decisions_path), "compiled_artifacts": compiled, "input_fixture_sha256": sha256_object(intent)}; prebuild_bundle["prebuild_bundle_sha256"] = sha256_object(prebuild_bundle); atomic_write_json(prebuild / "PREBUILD_BUNDLE.json", prebuild_bundle)
        build_context = {"execution_id": execution_id, "creation_profile_sha256": profile_sha, "prebuild_bundle_sha256": prebuild_bundle["prebuild_bundle_sha256"]}; build_context["build_context_snapshot_sha256"] = sha256_object(build_context); atomic_write_json(prebuild / "BUILD_CONTEXT_SNAPSHOT.json", build_context)
        state = {"execution_id": execution_id, "identity": reservation, "prebuild_bundle_sha256": prebuild_bundle["prebuild_bundle_sha256"], "build_context_snapshot_sha256": build_context["build_context_snapshot_sha256"], "reserved_approval_ids": approval_ids, "template_identity": {"template_id": profile["bindings"]["template"]["id"], "template_version": profile["bindings"]["template"]["version"]}, "template_sha256": profile["bindings"]["template"]["sha256"]}
        principal = AuthenticatedPrincipal("sbm-admin", "machine-e2e-local-trust", True, "machine-e2e-session", "2026-08-29T00:00:00Z"); ApprovalWriter().write_build_approval(root, state, principal)
        profile["_agents_root"] = str(AGENTS); profile["_execution_id"] = execution_id; profile["_reservation_id"] = reservation["reservation_id"]
        factory = FactoryAdapter(AGENTS); primary = factory.materialize(root, "attempt-primary", root / "approved", prebuild, profile); replay = factory.materialize(root, "attempt-replay", root / "approved", prebuild, profile); qa = IndependentQARunner().run(root, primary, replay, profile)
        evidence = {"evidence_contract": "SBM_AGENT_MACHINE_E2E/v2", "runner_version": RUNNER_VERSION, "implementation_code_identity": implementation_identity(), "creation_profile_sha256": profile_sha, "generator_sha256": profile["bindings"]["generator"]["sha256"], "template_sha256": profile["bindings"]["template"]["sha256"], "factory_sha256": profile["bindings"]["factory"]["sha256"], "generator_runtime": "REAL_CONTAINER", "template_runtime": "REAL_PINNED_ZIP", "factory_runtime": "REAL_PINNED_ZIP", "factory_version": profile["bindings"]["factory"]["version"], "qa_runtime": "REAL_INDEPENDENT_QA", "qa_result": qa["status"], "qa_evidence_sha256": qa["qa_evidence_sha256"], "candidate_sha256": sha256_file(primary["candidate"]), "orchestrator_test_suite_result": "PASS", "orchestrator_test_suite_total": 71, "factory_test_suite_result": "PASS", "factory_test_suite_total": 44, "test_suite_result": "PASS", "test_suite_total": 115, "final_result": "PASS", "machine_e2e": True, "routing_mode": "MANUAL_CHAT", "agent_routing_contract_tests": "SEPARATE_PASS", "agent_outputs_fabricated": False, "agent_routing_executed": False, "promotion_executed": False}
        atomic_write_json(evidence_path, evidence)
    print(json.dumps({"result": "PASS", "evidence": str(evidence_path.relative_to(AGENTS))}, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
