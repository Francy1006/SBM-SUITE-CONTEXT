from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTEXT_ROOT / "scripts"))

from qa_lifecycle import (  # noqa: E402
    QAContractError,
    evaluate_progress_qa,
    evaluate_qa,
    normalize_context_export,
    require_closure_qa,
    validate_closure_manifest_qa,
)


class QALifecycleTests(unittest.TestCase):
    def _write_transversal_evidence(
        self, root: Path, *, status: str = "passed", exit_code: int = 0
    ) -> None:
        output = root / "QA/output"
        output.mkdir(parents=True)
        (output / "qa-all-without-sonar-results.md").write_text(
            "# QA transversal\n\n"
            "| Project | Repository | Status | Evidence |\n"
            "|---|---|---|---|\n"
            f"| example | `SBM/example` | {status} | `evidence.md` |\n",
            encoding="utf-8",
        )
        queue_status = "passed" if status == "passed" else "failed"
        (output / "qa-all-without-sonar-queue.tsv").write_text(
            "project\trepository\tmode\tstatus\texit_code\n"
            f"example\tSBM/example\twithout-sonar\t{queue_status}\t{exit_code}\n",
            encoding="utf-8",
        )

    def test_suite_progress_uses_successful_transversal_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_transversal_evidence(root)

            result = evaluate_progress_qa("sbm-suite-context", root)

            self.assertIsNotNone(result)
            decision, evidence = result
            self.assertEqual(decision.status, "passed")
            self.assertTrue(decision.applicable)
            self.assertEqual(decision.workflow_path, "scripts/qa-check.sh")
            self.assertIn("qa-all-without-sonar-results.md", evidence)
            self.assertIn("example\tSBM/example\twithout-sonar\tpassed\t0", evidence)
            self.assertNotIn("No QA results were provided.", evidence)
            self.assertIsNotNone(decision.manifest())

    def test_suite_progress_without_evidence_does_not_invent_passed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = evaluate_progress_qa(
                "sbm-suite-context", Path(directory)
            )

            self.assertIsNone(result)

    def test_suite_closure_uses_successful_transversal_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_transversal_evidence(root)

            decision, evidence = require_closure_qa("sbm-suite-context", root)

            self.assertEqual(decision.status, "passed")
            self.assertTrue(decision.applicable)
            self.assertIn("qa-all-without-sonar-results.md", evidence)
            self.assertNotIn("QA status: not-applicable", evidence)

    def test_suite_closure_failed_transversal_evidence_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_transversal_evidence(root, status="failed (1)", exit_code=1)

            with self.assertRaisesRegex(QAContractError, "failed QA"):
                require_closure_qa("sbm-suite-context", root)

    def test_suite_progress_failed_transversal_evidence_is_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_transversal_evidence(
                root, status="failed (1)", exit_code=1
            )

            result = evaluate_progress_qa("sbm-suite-context", root)

            self.assertIsNotNone(result)
            decision, evidence = result
            self.assertEqual(decision.status, "failed")
            self.assertIn("Overall status: failed", evidence)

    def test_suite_progress_accepts_context_qa_generated_bullet_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "QA/output"
            output.mkdir(parents=True)
            context_evidence = (
                "# Context QA\n\n"
                "- Scope: `SBM-SUITE/context`\n"
                "- Overall status: passed\n"
            )
            (output / "context-qa-results.md").write_text(
                context_evidence, encoding="utf-8"
            )

            result = evaluate_progress_qa("sbm-suite-context", root)

            self.assertIsNotNone(result)
            decision, evidence = result
            self.assertEqual(decision.status, "passed")
            self.assertEqual(decision.workflow_path, "scripts/qa-check.sh")
            self.assertEqual(evidence, context_evidence)

    def test_case_a_missing_workflow_is_explicitly_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            decision, evidence = require_closure_qa("example", root)

            self.assertEqual(decision.status, "not-applicable")
            self.assertFalse(decision.applicable)
            self.assertEqual(decision.workflow_path, "scripts/qa-check.sh")
            self.assertIn("QA status: not-applicable", evidence)
            self.assertNotIn("No QA results were provided", evidence)
            self.assertEqual(
                decision.evidence_sha256,
                hashlib.sha256(evidence.encode()).hexdigest(),
            )
            self.assertEqual(
                validate_closure_manifest_qa(
                    decision.manifest(), "example", root
                ),
                decision,
            )

    def test_case_b_applicable_passed_qa_allows_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/qa-check.sh").write_text("#!/bin/sh\n")
            (root / "context").mkdir()
            evidence = "# QA Results\n\n> **Overall status:** passed\n"
            (root / "context/qa-results.md").write_text(evidence)

            decision, preserved = require_closure_qa("example", root)

            self.assertEqual(decision.status, "passed")
            self.assertTrue(decision.applicable)
            self.assertEqual(preserved, evidence)

    def test_success_evidence_is_normalized_to_passed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/qa-check.sh").write_text("#!/bin/sh\n")
            (root / "context").mkdir()
            (root / "context/qa-results.md").write_text(
                "**Overall status:** success\n"
            )

            decision, _ = require_closure_qa("example", root)

            self.assertEqual(decision.status, "passed")

    def test_case_c_failed_qa_blocks_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/qa-check.sh").write_text("#!/bin/sh\n")
            (root / "context").mkdir()
            (root / "context/qa-results.md").write_text(
                "Overall status: failed\n"
            )

            decision, _ = evaluate_qa("example", root)
            self.assertEqual(decision.status, "failed")
            with self.assertRaisesRegex(QAContractError, "failed QA"):
                require_closure_qa("example", root)

    def test_case_d_applicable_but_not_executed_never_becomes_na(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/qa-check.sh").write_text("#!/bin/sh\n")

            with self.assertRaisesRegex(QAContractError, "evidence is missing"):
                require_closure_qa("example", root)

    def test_applicable_project_cannot_forge_not_applicable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/qa-check.sh").write_text("#!/bin/sh\n")
            (root / "context").mkdir()
            (root / "context/qa-results.md").write_text(
                "Overall status: passed\n"
            )
            forged = {
                "status": "not-applicable",
                "applicable": False,
                "workflow_path": "scripts/qa-check.sh",
                "evidence_file": "qa-results.md",
                "evidence_sha256": "0" * 64,
                "reason": "manually selected",
            }

            with self.assertRaisesRegex(QAContractError, "does not match"):
                validate_closure_manifest_qa(forged, "example", root)

    def test_export_normalization_updates_source_and_upload_packages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context_package = root / "context-package.zip"
            upload_package = root / "context-deploy-package.zip"
            with ZipFile(context_package, "w") as archive:
                archive.writestr(
                    "manifest.json",
                    json.dumps(
                        {
                            "project_name": "example",
                            "lifecycle_phase": "implementation-closure",
                        }
                    ),
                )
                archive.writestr("qa-results.md", "No QA results were provided.\n")
            with ZipFile(upload_package, "w") as archive:
                archive.write(context_package, "context-package.zip")

            decision, evidence = require_closure_qa("example", root)
            normalize_context_export(
                context_package,
                upload_package,
                "example",
                decision,
                evidence,
            )

            with ZipFile(context_package) as archive:
                manifest = json.loads(archive.read("manifest.json"))
                self.assertEqual(manifest["qa"], decision.manifest())
                self.assertEqual(archive.read("qa-results.md").decode(), evidence)
                expected_inner = context_package.read_bytes()
            with ZipFile(upload_package) as archive:
                self.assertEqual(archive.read("context-package.zip"), expected_inner)

    def test_progress_export_normalization_preserves_transversal_qa(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_transversal_evidence(root)
            decision, evidence = evaluate_progress_qa("sbm-suite-context", root)
            context_package = root / "context-package.zip"
            upload_package = root / "context-deploy-package.zip"
            with ZipFile(context_package, "w") as archive:
                archive.writestr(
                    "manifest.json",
                    json.dumps(
                        {
                            "project_name": "sbm-suite-context",
                            "lifecycle_phase": "implementation-progress",
                            "qa": None,
                        }
                    ),
                )
                archive.writestr("qa-results.md", "No QA results were provided.\n")
            with ZipFile(upload_package, "w") as archive:
                archive.write(context_package, "context-package.zip")

            normalize_context_export(
                context_package,
                upload_package,
                "sbm-suite-context",
                decision,
                evidence,
            )

            with ZipFile(context_package) as archive:
                manifest = json.loads(archive.read("manifest.json"))
                self.assertEqual(manifest["qa"]["status"], "passed")
                self.assertEqual(archive.read("qa-results.md").decode(), evidence)

    def test_suite_qa_evaluation_does_not_mutate_operational_context(self) -> None:
        project_context = CONTEXT_ROOT / "PROJECT_CONTEXT.md"
        before = project_context.read_bytes()
        decision, evidence = require_closure_qa(
            "sbm-suite-context", CONTEXT_ROOT
        )

        self.assertEqual(decision.status, "passed")
        self.assertTrue(decision.applicable)
        self.assertIn("qa-all-without-sonar-results.md", evidence)
        self.assertEqual(project_context.read_bytes(), before)

        deploy = (CONTEXT_ROOT / "scripts/context-deploy.sh").read_text()
        self.assertIn(
            'if [[ "${LIFECYCLE_ROUTE}" == "implementation-closure" ]]; then',
            deploy,
        )
        self.assertIn('evaluate-progress', deploy)
        self.assertIn('PAYLOAD_QA_MANIFEST_JSON="${QA_MANIFEST_JSON}"', deploy)
        self.assertIn('QA_MANIFEST_JSON="${PAYLOAD_QA_MANIFEST_JSON}"', deploy)


if __name__ == "__main__":
    unittest.main()
