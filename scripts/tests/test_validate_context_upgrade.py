from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = CONTEXT_ROOT / "scripts" / "validate-context-upgrade.py"
TARGET = "SBM-SUITE/context/QA_CONTEXT.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ValidationEnvironment:
    def __init__(
        self,
        root: Path,
        source_markdown: str,
        *,
        target: str = TARGET,
        project_name: str = "sbm-manager",
        canonical_project_path: str = "SBM-SUITE/sbm/SBM-MANAGER",
        lifecycle_phase: str = "implementation-progress",
        objectives: list[dict] | None = None,
        patch_path: str = "patches/global-qa-context.json",
    ):
        self.root = root
        self.suite_root = root / "SBM-SUITE"
        self.context_root = self.suite_root / "context"
        self.context_root.mkdir(parents=True)
        self.target = target
        self.project_name = project_name
        self.canonical_project_path = canonical_project_path
        self.lifecycle_phase = lifecycle_phase
        self.objectives = objectives or [{"objective_id": "SBM-MANAGER-002"}]
        self.patch_path = patch_path
        self.target_path = self.suite_root.joinpath(*Path(target).parts[1:])
        self.target_path.parent.mkdir(parents=True, exist_ok=True)
        self.source_bytes = source_markdown.encode("utf-8")
        self.target_path.write_bytes(self.source_bytes)
        self.deploy_package = root / "context-deploy-package.zip"
        self.upgrade_zip = root / "context-upgrade.zip"

    @property
    def source_manifest(self) -> dict:
        return {
            "contract_version": "contract-test",
            "project_name": self.project_name,
            "workflow": "context-deploy",
            "execution_mode": "evidence",
            "canonical_project_path": self.canonical_project_path,
            "lifecycle_phase": self.lifecycle_phase,
            "objectives": self.objectives,
            "supported_patch_paths": [self.patch_path],
            "target_content_hashes": {self.target: sha256(self.source_bytes)},
        }

    @property
    def upgrade_manifest(self) -> dict:
        source = self.source_manifest
        return {
            "contract_version": source["contract_version"],
            "project_name": source["project_name"],
            "workflow": "context-upgrade",
            "execution_mode": source["execution_mode"],
            "canonical_project_path": source["canonical_project_path"],
            "lifecycle_phase": source["lifecycle_phase"],
            "objectives": source["objectives"],
            "supported_patch_paths": source["supported_patch_paths"],
        }

    def write_deploy_package(self) -> None:
        nested = BytesIO()
        with ZipFile(nested, "w", ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(self.source_manifest))
            archive.writestr(self.target, self.source_bytes)
        with ZipFile(self.deploy_package, "w", ZIP_DEFLATED) as archive:
            archive.writestr("context-package.zip", nested.getvalue())
            archive.writestr("context-export-response.json", "{}")
            archive.writestr("SYS_PROMPT.md", "test")

    def write_upgrade(self, heading: str, content: str) -> None:
        patch = {
            "target_file": self.target,
            "operations": [
                {
                    "operation": "replace_section",
                    "heading": heading,
                    "content": content,
                }
            ],
        }
        with ZipFile(self.upgrade_zip, "w", ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", json.dumps(self.upgrade_manifest))
            archive.writestr(self.patch_path, json.dumps(patch))

    def run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                str(self.upgrade_zip),
                str(self.deploy_package),
                str(self.suite_root),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )


class ValidateContextUpgradeTests(unittest.TestCase):
    def test_repository_summary_uses_canonical_schema(self) -> None:
        markdown = (CONTEXT_ROOT / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        canonical = (
            "| Project | Purpose | Active objective | Pending objectives | "
            "Branch | Main context | QA context | Documentation |"
        )
        legacy = "| Project/group | Current role | Active objective | Pending direction |"
        self.assertIn(canonical, markdown)
        self.assertNotIn(legacy, markdown)

    def test_activation_rejects_legacy_summary_schema_mutation(self) -> None:
        source = """# PROJECT_CONTEXT.md

## 6. Project objective summaries

| Project/group | Current role | Active objective | Pending direction |
|---|---|---|---|
| SBM-SUITE/context | Global governance/orchestration | N/A | OBJ-CTX-038 |

## 7. Global architecture

N/A
"""
        patched_section = """## 6. Project objective summaries

| Project/group | Current role | Active objective | Pending direction |
|---|---|---|---|
| SBM-SUITE/context | Global governance/orchestration | OBJ-CTX-038 | N/A |
"""
        objective = {
            "objective_id": "OBJ-CTX-038",
            "objective": "Standardize transversal Git Flow governance",
            "status": "active",
            "priority": 5,
            "target_date": "N/A",
            "branch": "FEATURE-standardizes-suite-governance",
        }
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(
                Path(tmp),
                source,
                target="SBM-SUITE/context/PROJECT_CONTEXT.md",
                project_name="sbm-suite-context",
                canonical_project_path="SBM-SUITE/context",
                lifecycle_phase="objective-activation",
                objectives=[objective],
                patch_path="patches/global-project-context.json",
            )
            env.write_deploy_package()
            env.write_upgrade("## 6. Project objective summaries", patched_section)
            result = env.run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must use canonical table schema", result.stderr)

    def test_activation_allows_only_selected_suite_summary_active_objective(self) -> None:
        source = """# PROJECT_CONTEXT.md

## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | QA completion | FEATURE-integrates-sbm-manager | `SBM/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `SBM/SBM-MANAGER/context/QA_CONTEXT.md` | N/A |
| SBM-SUITE/context | Global governance/orchestration | N/A | `OBJ-CTX-038` | N/A | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |

## 7. Global architecture

N/A
"""
        patched_section = """## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | QA completion | FEATURE-integrates-sbm-manager | `SBM/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `SBM/SBM-MANAGER/context/QA_CONTEXT.md` | N/A |
| SBM-SUITE/context | Global governance/orchestration | `OBJ-CTX-038` | N/A | FEATURE-standardizes-suite-governance | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |
"""
        objective = {
            "objective_id": "OBJ-CTX-038",
            "objective": "Standardize transversal Git Flow governance",
            "status": "active",
            "priority": 5,
            "target_date": "N/A",
            "branch": "FEATURE-standardizes-suite-governance",
        }
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(
                Path(tmp),
                source,
                target="SBM-SUITE/context/PROJECT_CONTEXT.md",
                project_name="sbm-suite-context",
                canonical_project_path="SBM-SUITE/context",
                lifecycle_phase="objective-activation",
                objectives=[objective],
                patch_path="patches/global-project-context.json",
            )
            env.write_deploy_package()
            env.write_upgrade("## 6. Project objective summaries", patched_section)
            result = env.run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preflight de fidelidad validado.", result.stdout)

    def test_activation_rejects_other_selected_suite_summary_cell_changes(self) -> None:
        source = """# PROJECT_CONTEXT.md

## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-SUITE/context | Global governance/orchestration | N/A | `OBJ-CTX-038` | N/A | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |

## 7. Global architecture

N/A
"""
        patched_section = """## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-SUITE/context | Changed unrelated role | `OBJ-CTX-038` | N/A | FEATURE-standardizes-suite-governance | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |
"""
        objective = {
            "objective_id": "OBJ-CTX-038",
            "objective": "Standardize transversal Git Flow governance",
            "status": "active",
            "priority": 5,
            "target_date": "N/A",
            "branch": "FEATURE-standardizes-suite-governance",
        }
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(
                Path(tmp),
                source,
                target="SBM-SUITE/context/PROJECT_CONTEXT.md",
                project_name="sbm-suite-context",
                canonical_project_path="SBM-SUITE/context",
                lifecycle_phase="objective-activation",
                objectives=[objective],
                patch_path="patches/global-project-context.json",
            )
            env.write_deploy_package()
            env.write_upgrade("## 6. Project objective summaries", patched_section)
            result = env.run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrelated table row", result.stderr)

    def test_activation_batch_updates_selected_suite_summary_atomically(self) -> None:
        source = """# PROJECT_CONTEXT.md

## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | QA completion | FEATURE-integrates-sbm-manager | `SBM/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `SBM/SBM-MANAGER/context/QA_CONTEXT.md` | N/A |
| SBM-SUITE/context | Global governance/orchestration | N/A | `OBJ-CTX-012`, `OBJ-CTX-002` | N/A | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |

## 7. Global architecture

N/A
"""
        patched_section = """## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | QA completion | FEATURE-integrates-sbm-manager | `SBM/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `SBM/SBM-MANAGER/context/QA_CONTEXT.md` | N/A |
| SBM-SUITE/context | Global governance/orchestration | `OBJ-CTX-012`, `OBJ-CTX-002` | N/A | FEATURE-standardizes-suite-governance | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |
"""
        objectives = [
            {
                "objective_id": objective_id,
                "objective": objective,
                "status": "active",
                "priority": 5,
                "target_date": "N/A",
                "branch": "FEATURE-standardizes-suite-governance",
            }
            for objective_id, objective in (
                ("OBJ-CTX-012", "Create the SBM Agent bootstrap"),
                ("OBJ-CTX-002", "Enable transversal Context tooling"),
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(
                Path(tmp),
                source,
                target="SBM-SUITE/context/PROJECT_CONTEXT.md",
                project_name="sbm-suite-context",
                canonical_project_path="SBM-SUITE/context",
                lifecycle_phase="objective-activation",
                objectives=objectives,
                patch_path="patches/global-project-context.json",
            )
            env.write_deploy_package()
            env.write_upgrade("## 6. Project objective summaries", patched_section)
            result = env.run()

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_change_to_unrelated_coverage_row(self) -> None:
        source = """# QA_CONTEXT.md

## 6. Coverage summary

| Project | Tool | Coverage | Threshold | Status | Last execution | Evidence |
|---|---|---|---|---|---|---|
| DP-API | pytest-cov | 88% | N/A | recorded | 2026-08-02 | existing |
| SBM-MANAGER | Vitest / V8 | N/A | 70% | not validated | N/A | pending |

## 7. Static analysis summary

N/A
"""
        patched_section = """## 6. Coverage summary

| Project | Tool | Coverage | Threshold | Status | Last execution | Evidence |
|---|---|---|---|---|---|---|
| DP-API | pytest-cov | 88% | N/A | recorded | 2026-08-02 | existing |
| SBM-MANAGER | Vitest / V8 | 70.14% | 70% | passed | 2026-08-13 | current QA |
"""
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(Path(tmp), source)
            env.write_deploy_package()
            env.write_upgrade("## 6. Coverage summary", patched_section)
            result = env.run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Patch removes or changes an unrelated table row: "
            "SBM-SUITE/context/QA_CONTEXT.md ## 6. Coverage summary",
            result.stderr,
        )

    def test_allows_selected_project_global_qa_summary_row(self) -> None:
        source = """# QA_CONTEXT.md

## 4. Project QA summaries

| Project | QA context | Test count | Passed | Failed | Coverage | SonarQube status | Last execution | Overall risk | Evidence |
|---|---|---:|---:|---:|---|---|---|---:|---|
| DP-API | dp | 65 | 65 | 0 | 88% | PASSED | 2026-08-02 | 3 | existing |
| SBM-MANAGER | manager | N/A | N/A | N/A | N/A | N/A | N/A | 3 | pending |

## 5. Test inventory

N/A
"""
        patched_section = """## 4. Project QA summaries

| Project | QA context | Test count | Passed | Failed | Coverage | SonarQube status | Last execution | Overall risk | Evidence |
|---|---|---:|---:|---:|---|---|---|---:|---|
| DP-API | dp | 65 | 65 | 0 | 88% | PASSED | 2026-08-02 | 3 | existing |
| SBM-MANAGER | manager | 45 | 45 | 0 | 70.14% | PASSED | 2026-08-13 | 3 | current QA |
"""
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(Path(tmp), source)
            env.write_deploy_package()
            env.write_upgrade("## 4. Project QA summaries", patched_section)
            result = env.run()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Preflight de fidelidad validado.", result.stdout)

    def test_rejects_source_drift_since_context_deploy(self) -> None:
        source = """# QA_CONTEXT.md

## 16. Current QA status

Status: pending
"""
        patched_section = """## 16. Current QA status

Status: passed
"""
        with tempfile.TemporaryDirectory() as tmp:
            env = ValidationEnvironment(Path(tmp), source)
            env.write_deploy_package()
            env.write_upgrade("## 16. Current QA status", patched_section)
            env.target_path.write_text(source + "\nexternal drift\n", encoding="utf-8")
            result = env.run()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Source-of-truth cambió desde context-deploy", result.stderr)


if __name__ == "__main__":
    unittest.main()
