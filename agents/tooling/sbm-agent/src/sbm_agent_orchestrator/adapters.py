from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from .contracts import read_yaml, write_yaml
from .errors import OrchestratorError
from .util import atomic_write_json, sha256_file, sha256_object, sortable_id, utc_now


def verify_factory_authorization(authorization_path, execution_dir, approved_root, compiled_root, template_path, reservation_id=None):
    authorization = json.loads(Path(authorization_path).read_text(encoding="utf-8")); unsigned = dict(authorization); claimed = unsigned.pop("authorization_sha256", None)
    if authorization.get("contract") != "FACTORY_AUTHORIZATION/v1" or claimed != sha256_object(unsigned): raise OrchestratorError("FACTORY_AUTHORIZATION_INVALID", "Factory authorization hash is invalid")
    event_path = Path(execution_dir) / "BUILD_APPROVAL_EVENT.json"; projection_path = Path(approved_root) / "APPROVED_PROPOSAL_PROJECTION.json"; spec_path = Path(compiled_root) / "AGENT_SPEC.yaml"
    event = json.loads(event_path.read_text(encoding="utf-8")); event_unsigned = dict(event); event_claimed = event_unsigned.pop("event_sha256", None); spec = read_yaml(spec_path)
    checks = [
        (authorization.get("execution_id") == Path(execution_dir).name, "execution_id"),
        (authorization.get("reservation_id") == event.get("reservation_id") and (reservation_id is None or authorization.get("reservation_id") == reservation_id), "reservation_id"),
        (authorization.get("prebuild_bundle_sha256") == event.get("prebuild_bundle_sha256"), "prebuild_bundle_sha256"),
        (authorization.get("approved_proposal_projection_sha256") == sha256_file(projection_path), "approved_proposal_projection_sha256"),
        (authorization.get("build_approval_event_sha256") == event_claimed == sha256_object(event_unsigned), "build_approval_event_sha256"),
        (authorization.get("spec_identity") == {"spec_id": spec.get("spec_id"), "spec_version": spec.get("spec_version")} and authorization.get("spec_sha256") == sha256_file(spec_path), "spec binding"),
        (authorization.get("template_sha256") == sha256_file(template_path), "template_sha256"),
    ]
    for valid, field in checks:
        if not valid: raise OrchestratorError("FACTORY_AUTHORIZATION_MISMATCH", f"Factory authorization mismatch: {field}")
    return authorization


class PinnedZipRuntime:
    """Materializes and verifies the exact pinned ZIP before every execution."""
    @staticmethod
    def prepare(execution_dir, agents_root, binding, label):
        archive = (Path(agents_root) / binding["path"]).resolve()
        if sha256_file(archive) != binding["sha256"]:
            raise OrchestratorError("PINNED_RUNTIME_HASH_MISMATCH", f"Pinned {label} ZIP hash mismatch")
        target = Path(execution_dir) / "runtimes" / f"{label}-{binding['sha256']}"
        with zipfile.ZipFile(archive) as package:
            files = {name: package.read(name) for name in package.namelist() if not name.endswith("/")}
            for name in files:
                candidate = (target / name).resolve(strict=False)
                try: candidate.relative_to(target.resolve(strict=False))
                except ValueError as exc: raise OrchestratorError("PINNED_RUNTIME_INVALID", f"Unsafe {label} ZIP entry") from exc
            if not target.exists():
                target.mkdir(parents=True)
                for name, payload in files.items():
                    path = target / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
        physical = {path.relative_to(target).as_posix(): path.read_bytes() for path in target.rglob("*") if path.is_file()}
        if physical != files:
            raise OrchestratorError("EXECUTED_RUNTIME_SHA_BINDING_FAILED", f"Executed {label} runtime does not exactly match pinned ZIP")
        roots = {name.split("/", 1)[0] for name in files}
        if len(roots) != 1:
            raise OrchestratorError("PINNED_RUNTIME_INVALID", f"Pinned {label} ZIP must have one root")
        return target / next(iter(roots))


def proposal_input(intent, reservation, profile, execution_id):
    defaults = profile["canonical_defaults"]
    return {
        "execution_id": execution_id,
        "proposal_id": f"PROP-{reservation['canonical_agent_id']}",
        "proposal_version": "1.0.0",
        "agent_name": reservation["canonical_agent_name"],
        "agent_description": intent["desired_outcome"],
        "agent_purpose": intent["desired_outcome"],
        "general_context": "SBM-SUITE governed agent creation",
        "hierarchy": "Reports to sbm-admin; Darwin advises architecture; Noe reviews independently",
        "personality": intent.get("personality") or defaults["personality"],
        "communication_style": intent.get("communication_style") or intent.get("style") or defaults["communication_style"],
        "retrieval_strategy": defaults["retrieval_strategy"],
        "embedding_strategy": defaults["embedding_strategy"],
        "llm_policy": "NO_LLM_BY_DEFAULT",
        "expected_frequency": defaults["expected_frequency"],
        "specific_objectives": [intent["desired_outcome"]],
        "responsibilities": intent.get("responsibilities") or defaults["responsibilities"],
        "authority": defaults["authority"],
        "permissions": defaults["permissions"],
        "relationships": defaults["relationships"],
        "required_context": ["context.zip"],
        "execution_modes": defaults["execution_modes"],
        "asynchronous_capabilities": defaults["asynchronous_capabilities"],
        "execution_dependencies": defaults["execution_dependencies"],
        "outputs": defaults["outputs"],
        "escalation_rules": defaults["escalation_rules"],
        "qa_specific": defaults["qa"],
        "deployment": None,
        "creation_mode": "NEW",
        "review_status": "DRAFT",
        "origin": "sbm-agent-orchestrator",
        "non_interactive": True,
        "standard_upgrade_requested": False,
        "source_agent_id_hint": None,
        "source_agent_version_hint": None,
        "source_standard_version_hint": None,
    }


class ContainerGeneratorAdapter:
    """Invokes the immutable Generator 2.0.0 through existing container tooling."""

    def __init__(self, agents_root):
        self.agents_root = Path(agents_root).resolve()

    def generate(self, execution_dir, generator_input, profile):
        execution_dir = Path(execution_dir).resolve()
        runtime = PinnedZipRuntime.prepare(execution_dir, self.agents_root, profile["bindings"]["generator"], "generator")
        dependencies = runtime / "node_modules"
        if not dependencies.exists() and not dependencies.is_symlink():
            dependencies.symlink_to("/usr/local/lib/node_modules", target_is_directory=True)
        if not dependencies.is_symlink() or os.readlink(dependencies) != "/usr/local/lib/node_modules":
            raise OrchestratorError("GENERATOR_DEPENDENCY_BINDING_FAILED", "Generator dependencies are not bound to the pinned tooling image")
        input_path = execution_dir / "generator-input.json"
        atomic_write_json(input_path, generator_input)
        rel = execution_dir.relative_to(self.agents_root).as_posix()
        compose = self.agents_root.parent / "docker-compose.yml"
        generator = "/workspace/context/agents/" + (runtime / "generators/app").relative_to(self.agents_root).as_posix()
        command = [
            "docker", "compose", "-f", str(compose), "run", "--rm",
            "--workdir", f"/workspace/context/agents/{rel}", "sbm-agent-tooling",
            "yo", generator, "--config", "./generator-input.json", "--non-interactive",
        ]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            raise OrchestratorError("GENERATOR_FAILED", "Generator 2.0.0 failed", details={"stderr": result.stderr[-2000:]})
        scaffold = execution_dir / "build" / "scaffolds" / generator_input["execution_id"]
        proposal = scaffold / "AGENT_PROPOSAL.yaml"
        metadata = scaffold / ".sbm" / "scaffold.json"
        if not proposal.is_file() or not metadata.is_file():
            raise OrchestratorError("GENERATOR_OUTPUT_INVALID", "Generator did not emit its contractual DRAFT")
        if read_yaml(proposal).get("review_status") != "DRAFT":
            raise OrchestratorError("GENERATOR_BOUNDARY_VIOLATION", "Generator output is not DRAFT")
        return proposal, metadata


class InProcessGeneratorAdapter:
    """Test adapter preserving the Generator-owned DRAFT output contract."""

    def generate(self, execution_dir, generator_input, profile):
        scaffold = Path(execution_dir) / "build" / "scaffolds" / generator_input["execution_id"]
        scaffold.mkdir(parents=True, exist_ok=False)
        fields = [
            "proposal_id", "proposal_version", "agent_name", "agent_description", "agent_purpose",
            "specific_objectives", "general_context", "responsibilities", "authority", "permissions",
            "hierarchy", "relationships", "personality", "communication_style", "required_context",
            "retrieval_strategy", "embedding_strategy", "llm_policy", "execution_modes", "expected_frequency",
            "asynchronous_capabilities", "execution_dependencies", "outputs", "escalation_rules", "deployment", "qa_specific",
        ]
        proposal = {key: generator_input[key] for key in fields}
        proposal.update({"creation_mode": "NEW", "parent_reference": None, "review_status": "DRAFT"})
        proposal_path = scaffold / "AGENT_PROPOSAL.yaml"; write_yaml(proposal_path, proposal)
        metadata = scaffold / ".sbm" / "scaffold.json"
        atomic_write_json(metadata, {"execution_id": generator_input["execution_id"], "origin": "generator-sbm-agent-v2_0_0"})
        return proposal_path, metadata


class FactoryAdapter:
    def __init__(self, agents_root, python=None):
        self.agents_root = Path(agents_root).resolve()
        self.python = python or sys.executable

    def materialize(self, execution_dir, attempt_id, approved_root, compiled_root, profile):
        runtime = PinnedZipRuntime.prepare(execution_dir, self.agents_root, profile["bindings"]["factory"], "factory")
        attempt = Path(execution_dir) / "attempts" / attempt_id
        input_root = attempt / "input"; output = attempt / "output"
        input_root.mkdir(parents=True, exist_ok=False)
        for path in compiled_root.rglob("*"):
            if path.is_file():
                target = input_root / path.relative_to(compiled_root); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, target)
        for name in ("AGENT_PROPOSAL.yaml", "PROPOSAL_APPROVAL.yaml", "SPEC_APPROVAL.yaml", "MATERIALIZATION_APPROVAL.yaml", "APPROVED_PROPOSAL_PROJECTION.json", "FACTORY_AUTHORIZATION.json"):
            shutil.copy2(Path(approved_root) / name, input_root / name)
        template = self.agents_root / profile["bindings"]["template"]["path"]
        authorization = verify_factory_authorization(input_root / "FACTORY_AUTHORIZATION.json", execution_dir, input_root, input_root, template, profile["_reservation_id"])
        env = dict(os.environ); env["PYTHONPATH"] = str(runtime / "src"); env["PYTHONDONTWRITEBYTECODE"] = "1"
        args = [
            self.python, "-m", "sbm_agent_factory.cli", "create",
            "--proposal", str((input_root / "AGENT_PROPOSAL.yaml").resolve()),
            "--proposal-approval", str((input_root / "PROPOSAL_APPROVAL.yaml").resolve()),
            "--spec", str((input_root / "AGENT_SPEC.yaml").resolve()),
            "--spec-approval", str((input_root / "SPEC_APPROVAL.yaml").resolve()),
            "--materialization-approval", str((input_root / "MATERIALIZATION_APPROVAL.yaml").resolve()),
            "--orchestrator-authorization", str((input_root / "FACTORY_AUTHORIZATION.json").resolve()),
            "--build-approval-event", str((execution_dir / "BUILD_APPROVAL_EVENT.json").resolve()),
            "--approved-proposal-projection", str((input_root / "APPROVED_PROPOSAL_PROJECTION.json").resolve()),
            "--execution-id", profile["_execution_id"], "--reservation-id", profile["_reservation_id"],
            "--template", str(template.resolve()), "--output-dir", str(output.resolve()),
        ]
        result = subprocess.run(args, text=True, capture_output=True, env=env)
        if result.returncode:
            raise OrchestratorError("FACTORY_FAILED", f"Factory {profile['bindings']['factory']['version']} failed", details={"stderr": result.stderr[-3000:]})
        zips = list((attempt / "dist").glob("*.zip"))
        if len(zips) != 1:
            raise OrchestratorError("FACTORY_OUTPUT_INVALID", "Factory emitted an invalid candidate set")
        return {
            "attempt_id": attempt_id, "attempt_root": attempt, "output": output, "candidate": zips[0],
            "execution_evidence": attempt / "EXECUTION_EVIDENCE.yaml", "registry_candidate": attempt / "REGISTRY_CANDIDATE.yaml",
        }


class InProcessFactoryAdapter:
    """Deterministic isolated factory seam for orchestration tests."""

    def materialize(self, execution_dir, attempt_id, approved_root, compiled_root, profile):
        import zipfile
        template = Path(profile.get("_agents_root", Path(execution_dir).parents[3])) / profile["bindings"]["template"]["path"]
        verify_factory_authorization(Path(approved_root) / "FACTORY_AUTHORIZATION.json", execution_dir, approved_root, compiled_root, template, profile["_reservation_id"])
        attempt = Path(execution_dir) / "attempts" / attempt_id; output = attempt / "output"; dist = attempt / "dist"
        output.mkdir(parents=True, exist_ok=False); dist.mkdir()
        for path in Path(compiled_root).rglob("*"):
            if path.is_file():
                target = output / path.relative_to(compiled_root); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, target)
        shutil.copy2(Path(approved_root) / "AGENT_PROPOSAL.yaml", output / "AGENT_PROPOSAL.yaml")
        (output / "INIT.md").write_text("LOADING_AGENT -> WAITING_FOR_CONTEXT -> ACTIVE; BLOCKED\n", encoding="utf-8")
        scripts = output / "scripts"; scripts.mkdir()
        (scripts / "validate").write_text("print('VALID')\n", encoding="utf-8")
        (scripts / "test").write_text("print('TESTS: PASS')\n", encoding="utf-8")
        (output / "MANIFEST.yaml").write_text("files: []\n", encoding="utf-8")
        (output / "CHECKSUMS.sha256").write_text("", encoding="utf-8")
        def integrity():
            files = sorted(p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file())
            entries = []
            for rel in files:
                digest = None if rel in ("MANIFEST.yaml", "CHECKSUMS.sha256") else sha256_file(output / rel)
                entries.append({"path": rel, "purpose": "package artifact", "required": True, "sha256": digest})
            write_yaml(output / "MANIFEST.yaml", {"agent_id": read_yaml(output/'AGENT_SPEC.yaml')["agent_id"], "files": entries})
            checks = [f"{sha256_file(output/rel)}  {rel}" for rel in files if rel != "CHECKSUMS.sha256"]
            (output / "CHECKSUMS.sha256").write_text("\n".join(checks) + "\n", encoding="utf-8")
        integrity(); integrity()
        candidate = dist / f"{read_yaml(output/'AGENT_SPEC.yaml')['agent_id']}-v1_0_0.zip"
        with zipfile.ZipFile(candidate, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(output.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(f"Agent/{path.relative_to(output).as_posix()}", (1980, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, path.read_bytes())
        candidate_sha = sha256_file(candidate)
        evidence = attempt / "EXECUTION_EVIDENCE.yaml"; registry = attempt / "REGISTRY_CANDIDATE.yaml"
        write_yaml(evidence, {"status": "SUCCEEDED", "factory_version": profile["bindings"]["factory"]["version"], "template_version": profile["bindings"]["template"]["version"], "package_sha256": candidate_sha})
        write_yaml(registry, {"agent_id": read_yaml(output/'AGENT_SPEC.yaml')["agent_id"], "package_sha256": candidate_sha, "status": "CANDIDATE"})
        return {"attempt_id": attempt_id, "attempt_root": attempt, "output": output, "candidate": candidate, "execution_evidence": evidence, "registry_candidate": registry}


class IndependentQARunner:
    VERSION = "1.0.0"

    def run(self, execution_dir, primary, replay, profile):
        if sha256_file(primary["candidate"]) != sha256_file(replay["candidate"]):
            raise OrchestratorError("DETERMINISM_FAILURE", "Independent replay candidate differs")
        first_files = {p.relative_to(primary["output"]).as_posix(): sha256_file(p) for p in primary["output"].rglob("*") if p.is_file()}
        second_files = {p.relative_to(replay["output"]).as_posix(): sha256_file(p) for p in replay["output"].rglob("*") if p.is_file()}
        if first_files != second_files:
            raise OrchestratorError("DETERMINISM_FAILURE", "Independent replay file set/bytes differ")
        evidence = read_yaml(primary["execution_evidence"]); registry = read_yaml(primary["registry_candidate"])
        candidate_sha = sha256_file(primary["candidate"])
        if evidence.get("status") != "SUCCEEDED" or evidence.get("package_sha256") != candidate_sha:
            raise OrchestratorError("QA_EVIDENCE_INVALID", "Factory evidence does not bind candidate")
        if registry.get("package_sha256") != candidate_sha:
            raise OrchestratorError("REGISTRY_CANDIDATE_INVALID", "Registry candidate does not bind candidate")
        output = primary["output"]
        for script in (output / "scripts/validate", output / "scripts/test"):
            if not script.is_file(): raise OrchestratorError("QA_SCRIPT_MISSING", "Generated agent QA script is missing")
            result = subprocess.run([sys.executable, str(script.resolve())], cwd=output, text=True, capture_output=True)
            if result.returncode: raise OrchestratorError("INDEPENDENT_AGENT_QA_FAILED", "Generated agent QA failed", details={"script": script.name, "stderr": result.stderr[-1000:]})
        checksums = output / "CHECKSUMS.sha256"; manifest_path = output / "MANIFEST.yaml"
        if not checksums.is_file() or not manifest_path.is_file():
            raise OrchestratorError("INTEGRITY_ARTIFACT_MISSING", "MANIFEST/CHECKSUMS are required")
        parsed_checksums = {}
        for line in checksums.read_text(encoding="utf-8").splitlines():
            if line.strip():
                digest, relative = line.split("  ", 1); parsed_checksums[relative] = digest
        for relative, digest in parsed_checksums.items():
            if sha256_file(output / relative) != digest: raise OrchestratorError("CHECKSUM_MISMATCH", "Independent checksum verification failed", details={"path": relative})
        manifest = read_yaml(manifest_path); physical = sorted(p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file())
        entries = {item["path"]: item for item in manifest.get("files", [])}
        if set(entries) != set(physical): raise OrchestratorError("MANIFEST_MISMATCH", "Manifest does not inventory physical output")
        spec = read_yaml(output / "AGENT_SPEC.yaml"); definition = read_yaml(output / "AGENT_DEFINITION.yaml")
        if spec["agent_id"] != definition["agent_id"] or spec["component_references"]["AGENT_DEFINITION"]["artifact_id"] != definition["agent_definition_id"]:
            raise OrchestratorError("CROSS_REFERENCE_MISMATCH", "Independent cross-reference verification failed")
        runtime = read_yaml(output / "config/RUNTIME_PROFILE.yaml")
        if runtime.get("llm_invocation_policy") != "NO_LLM_BY_DEFAULT":
            raise OrchestratorError("POLICY_VIOLATION", "NO_LLM_BY_DEFAULT is not preserved")
        execution_root = Path(execution_dir).resolve()
        for value in (primary["candidate"], primary["execution_evidence"], primary["registry_candidate"]):
            try: Path(value).resolve().relative_to(execution_root)
            except ValueError as exc: raise OrchestratorError("FORBIDDEN_WRITE", "Factory evidence escapes execution workspace") from exc
        bundle = {
            "qa_runner_version": self.VERSION, "independent_of_factory": True, "candidate_sha256": candidate_sha,
            "replay_candidate_sha256": sha256_file(replay["candidate"]), "file_set_sha256": sha256_object(first_files),
            "manifest_present": True, "checksums_verified": len(parsed_checksums), "agent_scripts": "PASS",
            "execution_evidence_sha256": sha256_file(primary["execution_evidence"]),
            "registry_candidate_sha256": sha256_file(primary["registry_candidate"]),
            "policy_assertions": {"no_llm_by_default": True, "forbidden_writes": "PASS", "cross_references": "PASS"},
            "status": "PASS", "timestamp": utc_now(),
        }
        bundle["qa_evidence_sha256"] = sha256_object(bundle)
        atomic_write_json(Path(execution_dir) / "qa" / "QA_EVIDENCE_BUNDLE.json", bundle)
        return bundle
