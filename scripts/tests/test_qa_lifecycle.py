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
    evaluate_qa,
    normalize_context_export,
    require_closure_qa,
    validate_closure_manifest_qa,
)


class QALifecycleTests(unittest.TestCase):
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

    def test_suite_qa_evaluation_does_not_mutate_operational_context(self) -> None:
        project_context = CONTEXT_ROOT / "PROJECT_CONTEXT.md"
        before = project_context.read_bytes()
        decision, evidence = require_closure_qa(
            "sbm-suite-context", CONTEXT_ROOT
        )

        self.assertEqual(decision.status, "not-applicable")
        self.assertIn("QA status: not-applicable", evidence)
        self.assertEqual(project_context.read_bytes(), before)

        deploy = (CONTEXT_ROOT / "scripts/context-deploy.sh").read_text()
        self.assertIn(
            'if [[ "${LIFECYCLE_ROUTE}" == "implementation-closure" ]]; then',
            deploy,
        )


if __name__ == "__main__":
    unittest.main()
