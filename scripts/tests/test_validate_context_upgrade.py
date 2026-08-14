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
    def __init__(self, root: Path, source_markdown: str):
        self.root = root
        self.suite_root = root / "SBM-SUITE"
        self.context_root = self.suite_root / "context"
        self.context_root.mkdir(parents=True)
        self.target_path = self.context_root / "QA_CONTEXT.md"
        self.source_bytes = source_markdown.encode("utf-8")
        self.target_path.write_bytes(self.source_bytes)
        self.deploy_package = root / "context-deploy-package.zip"
        self.upgrade_zip = root / "context-upgrade.zip"

    @property
    def source_manifest(self) -> dict:
        return {
            "contract_version": "contract-test",
            "project_name": "sbm-manager",
            "workflow": "context-deploy",
            "execution_mode": "evidence",
            "canonical_project_path": "SBM-SUITE/sbm/SBM-MANAGER",
            "lifecycle_phase": "implementation-progress",
            "objectives": [{"objective_id": "SBM-MANAGER-002"}],
            "supported_patch_paths": ["patches/global-qa-context.json"],
            "target_content_hashes": {TARGET: sha256(self.source_bytes)},
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
            archive.writestr(TARGET, self.source_bytes)
        with ZipFile(self.deploy_package, "w", ZIP_DEFLATED) as archive:
            archive.writestr("context-package.zip", nested.getvalue())
            archive.writestr("context-export-response.json", "{}")
            archive.writestr("SYS_PROMPT.md", "test")

    def write_upgrade(self, heading: str, content: str) -> None:
        patch = {
            "target_file": TARGET,
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
            archive.writestr("patches/global-qa-context.json", json.dumps(patch))

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
