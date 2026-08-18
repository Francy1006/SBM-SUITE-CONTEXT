from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
POLICY = CONTEXT_ROOT / "scripts/git-flow-policy.py"


class GitFlowPolicyTests(unittest.TestCase):
    def describe(self, branch: str) -> dict[str, object]:
        result = subprocess.run(
            ("python3", str(POLICY), "describe", branch),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        return json.loads(result.stdout)

    def test_branch_semantics_are_canonical(self) -> None:
        for branch in (
            "FEATURE-adds-flow",
            "BUGFIX-fixes-flow",
            "RELEASE-suite-flow",
            "HOTFIX-repairs-flow",
        ):
            with self.subTest(branch=branch):
                policy = self.describe(branch)
                self.assertEqual(policy["base_branch"], "main")
                self.assertEqual(policy["integration_branch"], "main")
                self.assertEqual(policy["final_branch"], "main")
                self.assertTrue(policy["requires_qa_gate"])
                self.assertTrue(policy["requires_documentation"])
                self.assertNotIn("develop", json.dumps(policy).casefold())

    def test_every_temporary_branch_fails_closed_without_full_qa_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                (
                    "python3",
                    str(POLICY),
                    "verify-finalization-gates",
                    "FEATURE-suite-flow",
                    "--qa",
                    str(root / "qa.json"),
                    "--documentation",
                    str(root / "documentation.json"),
                    "OBJ-TEST-001",
                ),
                check=False,
                text=True,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("gate requerido inexistente", result.stderr)

    def test_release_branch_is_part_of_name_contract(self) -> None:
        invalid = subprocess.run(
            ("python3", str(POLICY), "describe", "release-lowercase"),
            check=False,
            text=True,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(invalid.returncode, 0)


if __name__ == "__main__":
    unittest.main()
