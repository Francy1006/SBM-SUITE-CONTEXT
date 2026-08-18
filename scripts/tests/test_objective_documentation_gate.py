from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
GATE = CONTEXT_ROOT / "scripts" / "objective-documentation-gate.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class DocumentationGateTests(unittest.TestCase):
    def prepare(self, root: Path, documented_status: str) -> tuple[Path, Path]:
        suite = root / "SBM-SUITE"
        context = suite / "context"
        docs = context / "documentation" / "pages"
        docs.mkdir(parents=True)

        branch = "FEATURE-documentation-gate"
        (context / "PROJECT_CONTEXT.md").write_text(
            f"""# PROJECT_CONTEXT.md

## 3. Active objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
| OBJ-A | TEST | Objective A | active | 5 | N/A | {branch} | N/A |

## 4. Pending objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|

## 5. Boundary
""",
            encoding="utf-8",
        )
        (context / "COMPLETED_OBJECTIVES.md").write_text(
            """# COMPLETED_OBJECTIVES.md

## 1. Completed objectives by project

### TEST

| Objective ID | Project | Objective | Final status | Documentation |
|---|---|---|---|---|

## 2. Boundary
""",
            encoding="utf-8",
        )
        (context / "project-tree.txt").write_text("SBM-SUITE/context\n", encoding="utf-8")
        (docs / "roadmap.md").write_text(
            f"""# Roadmap

## 12. Roadmap

| Objective ID | Project | Status |
|---|---|---|
| OBJ-A | TEST | {documented_status} |
""",
            encoding="utf-8",
        )
        helper = root / "repositories.py"
        helper.write_text("print('context')\n", encoding="utf-8")

        run("git", "init", "-b", "main", cwd=context)
        run("git", "config", "user.email", "tests@example.com", cwd=context)
        run("git", "config", "user.name", "Tests", cwd=context)
        run("git", "add", ".", cwd=context)
        run("git", "commit", "-m", "initial", cwd=context)
        run("git", "checkout", "-b", branch, cwd=context)
        return context, helper

    def test_gate_uses_real_reconciliation_and_allows_na_lifecycle_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context, helper = self.prepare(root, "active")
            output = context / "documentation" / "output" / "finalization-gate.json"
            result = run(
                "python3",
                str(GATE),
                "--branch",
                "FEATURE-documentation-gate",
                "--project-context",
                str(context / "PROJECT_CONTEXT.md"),
                "--completed-objectives",
                str(context / "COMPLETED_OBJECTIVES.md"),
                "--documentation-root",
                str(context / "documentation"),
                "--project-tree",
                str(context / "project-tree.txt"),
                "--repository-helper",
                str(helper),
                "--output",
                str(output),
                "OBJ-A",
                cwd=context,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["branch"], "FEATURE-documentation-gate")
            self.assertEqual(payload["status"], "updated")
            self.assertEqual(payload["objectives"], ["OBJ-A"])
            self.assertRegex(payload["state_sha256"], r"^[0-9a-f]{64}$")

    def test_unsynchronized_documentation_does_not_create_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            context, helper = self.prepare(root, "pending")
            output = context / "documentation" / "output" / "finalization-gate.json"
            result = run(
                "python3",
                str(GATE),
                "--branch",
                "FEATURE-documentation-gate",
                "--project-context",
                str(context / "PROJECT_CONTEXT.md"),
                "--completed-objectives",
                str(context / "COMPLETED_OBJECTIVES.md"),
                "--documentation-root",
                str(context / "documentation"),
                "--project-tree",
                str(context / "project-tree.txt"),
                "--repository-helper",
                str(helper),
                "--output",
                str(output),
                "OBJ-A",
                cwd=context,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Documentation no está sincronizada", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
