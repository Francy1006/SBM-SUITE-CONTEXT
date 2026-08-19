from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CONTEXT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_NAMES = (
    "objective-git-finalize.sh",
    "objective-git-cleanup.sh",
    "objective-branches.sh",
    "suite-repositories.py",
    "git-flow-policy.py",
    "objective-git-state.py",
    "workflow-state.py",
)
SOURCES = tuple(CONTEXT_ROOT / "scripts" / name for name in SCRIPT_NAMES)


def run(*args: str, cwd: Path, check: bool = True):
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class Environment:
    repositories = ("context", "DP/DP-API", "SBM/SBM-API")

    def __init__(self, root: Path):
        self.root = root
        self.suite = root / "SBM-SUITE"
        self.context = self.suite / "context"
        self.remotes = root / "remotes"
        self.remotes.mkdir()

        for relative in self.repositories:
            repository = self.suite / relative
            repository.mkdir(parents=True)
            remote = self.remotes / f"{relative.replace('/', '-')}.git"
            run("git", "init", "--bare", str(remote), cwd=root)
            run("git", "init", "-b", "main", cwd=repository)
            run("git", "config", "user.email", "tests@example.com", cwd=repository)
            run("git", "config", "user.name", "Tests", cwd=repository)
            (repository / "tracked.txt").write_text(relative + "\n", encoding="utf-8")
            run("git", "add", ".", cwd=repository)
            run("git", "commit", "-m", "initial", cwd=repository)
            run("git", "remote", "add", "origin", str(remote), cwd=repository)
            run("git", "push", "-u", "origin", "main", cwd=repository)

        scripts = self.context / "scripts"
        scripts.mkdir(exist_ok=True)
        for source in SOURCES:
            shutil.copy2(source, scripts / source.name)
            (scripts / source.name).chmod(0o755)

        self.write_context([], [])
        self.write_completed([])
        run("git", "add", ".", cwd=self.context)
        run("git", "commit", "-m", "scripts", cwd=self.context)
        run("git", "push", "origin", "main", cwd=self.context)

    def repository(self, relative: str) -> Path:
        return self.suite / relative

    def write_context(self, active, pending):
        def rows(items, status):
            return "\n".join(
                f"| {oid} | TEST | Objective {oid} | {status} | 5 | N/A | {branch} | docs/{oid}.md |"
                for oid, branch in items
            )

        text = (
            "# PROJECT_CONTEXT.md\n\n## 3. Active objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n"
            + rows(active, "active")
            + "\n\n## 4. Pending objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n"
            + rows(pending, "pending")
            + "\n"
        )
        (self.context / "PROJECT_CONTEXT.md").write_text(text, encoding="utf-8")

    def write_completed(self, records):
        rows = "\n".join(
            f"| {oid} | TEST | Objective {oid} | {status} | 5 | {branch} | N/A | "
            f"2026-08-19 | done | full QA passed | docs/{oid}.md | N/A |"
            for oid, branch, status in records
        )
        text = (
            "# COMPLETED_OBJECTIVES.md\n\n## 1. Completed objectives by project\n\n### TEST\n\n"
            "| Objective ID | Project | Objective | Final status | Priority | Branch | Started | Completed | Summary | Validation | Documentation | Proposed commit |\n"
            "|---|---|---|---|---:|---|---|---|---|---|---|---|\n"
            + rows
            + "\n"
        )
        (self.context / "COMPLETED_OBJECTIVES.md").write_text(text, encoding="utf-8")

    def prepare(self, branch):
        for relative in self.repositories:
            run("git", "checkout", "-b", branch, "main", cwd=self.repository(relative))

    def state(self, scope: str) -> str:
        result = run(
            "python3",
            str(self.context / "scripts/workflow-state.py"),
            "--suite-root",
            str(self.suite),
            "--repository-helper",
            str(self.context / "scripts/suite-repositories.py"),
            "--scope",
            scope,
            cwd=self.context,
        )
        return result.stdout.strip()

    def write_gates(self, ids, branch):
        qa_dir = self.context / "QA/output"
        doc_dir = self.context / "documentation/output"
        qa_dir.mkdir(parents=True, exist_ok=True)
        doc_dir.mkdir(parents=True, exist_ok=True)
        qa = {
            "branch": branch,
            "status": "passed",
            "mode": "full-suite-with-sonar",
            "objectives": list(ids),
            "state_sha256": self.state("qa"),
        }
        doc = {
            "branch": branch,
            "status": "updated",
            "objectives": list(ids),
            "state_sha256": self.state("documentation"),
        }
        (qa_dir / "finalization-gate.json").write_text(
            json.dumps(qa, indent=2) + "\n", encoding="utf-8"
        )
        (doc_dir / "finalization-gate.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )

    def finalize(self, ids, branch):
        return run(
            str(self.context / "scripts/objective-git-finalize.sh"),
            *ids,
            branch,
            cwd=self.context,
            check=False,
        )


class ObjectiveGitFinalizeTests(unittest.TestCase):
    def test_pending_batch_finalizes_with_gates_and_deletes_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-finalizes-pending-batch"
            ids = ("OBJ-PENDING-001", "OBJ-PENDING-002")
            env.prepare(branch)
            env.write_context([], [(ids[0], branch), (ids[1], branch)])
            (env.repository("DP/DP-API") / "tracked.txt").write_text("changed\n", encoding="utf-8")
            env.write_gates(ids, branch)

            result = env.finalize(ids, branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in env.repositories:
                repository = env.repository(relative)
                self.assertEqual(run("git", "branch", "--show-current", cwd=repository).stdout.strip(), "main")
                self.assertEqual(run("git", "status", "--porcelain", cwd=repository).stdout, "")
                self.assertNotIn(branch, run("git", "branch", "--list", branch, cwd=repository).stdout)
                self.assertEqual(
                    run("git", "ls-remote", "--heads", "origin", branch, cwd=repository).stdout.strip(),
                    "",
                )
            self.assertEqual(
                run("git", "log", "main", "-1", "--pretty=%s", cwd=env.repository("DP/DP-API")).stdout.strip(),
                "merge: finalize transversal objective batch",
            )

    def test_active_objective_is_supported_with_current_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-finalizes-active"
            oid = "OBJ-ACTIVE-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            env.write_gates((oid,), branch)
            result = env.finalize((oid,), branch)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_completed_objective_is_supported_with_current_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "BUGFIX-finalizes-completed"
            oid = "OBJ-COMPLETE-001"
            env.prepare(branch)
            env.write_completed([(oid, branch, "completed")])
            env.write_gates((oid,), branch)
            result = env.finalize((oid,), branch)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_documentation_gate_aborts_before_git_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-missing-doc-gate"
            oid = "OBJ-GATE-001"
            env.prepare(branch)
            env.write_context([], [(oid, branch)])
            env.write_gates((oid,), branch)
            (env.context / "documentation/output/finalization-gate.json").unlink()
            before = run("git", "rev-parse", "HEAD", cwd=env.context).stdout
            result = env.finalize((oid,), branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Documentation gate inexistente", result.stderr)
            self.assertEqual(run("git", "rev-parse", "HEAD", cwd=env.context).stdout, before)

    def test_stale_documentation_gate_aborts_before_git_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-stale-doc-gate"
            oid = "OBJ-STALE-001"
            env.prepare(branch)
            env.write_context([], [(oid, branch)])
            env.write_gates((oid,), branch)
            (env.repository("DP/DP-API") / "tracked.txt").write_text("changed after gate\n", encoding="utf-8")
            result = env.finalize((oid,), branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Documentation gate no corresponde al estado actual", result.stderr)
            self.assertEqual(run("git", "branch", "--show-current", cwd=env.context).stdout.strip(), branch)

    def test_gate_batch_order_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-order-mismatch"
            ids = ("OBJ-ORDER-001", "OBJ-ORDER-002")
            env.prepare(branch)
            env.write_context([], [(ids[0], branch), (ids[1], branch)])
            env.write_gates(tuple(reversed(ids)), branch)
            result = env.finalize(ids, branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("batch ordenado", result.stderr)

    def test_lifecycle_branch_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-current-branch"
            oid = "OBJ-BRANCH-MISMATCH"
            env.prepare(branch)
            env.write_context([], [(oid, "FEATURE-other-branch")])
            result = env.finalize((oid,), branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Branch lifecycle", result.stderr)

    def test_wrong_repository_branch_aborts_before_any_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-atomic-finalization"
            oid = "OBJ-MUST-ABORT"
            env.prepare(branch)
            env.write_context([], [(oid, branch)])
            env.write_gates((oid,), branch)
            before = {relative: run("git", "rev-parse", "HEAD", cwd=env.repository(relative)).stdout for relative in env.repositories}
            run("git", "checkout", "main", cwd=env.repository("SBM/SBM-API"))
            result = env.finalize((oid,), branch)
            self.assertNotEqual(result.returncode, 0)
            for relative in env.repositories:
                self.assertEqual(run("git", "rev-parse", "HEAD", cwd=env.repository(relative)).stdout, before[relative])

    def test_source_enforces_gates_and_integrated_cleanup(self):
        source = (CONTEXT_ROOT / "scripts/objective-git-finalize.sh").read_text(encoding="utf-8")
        self.assertIn("QA/output/finalization-gate.json", source)
        self.assertIn("documentation/output/finalization-gate.json", source)
        self.assertIn("objective-git-state.py", source)
        self.assertIn("objective-git-cleanup.sh", source)
        self.assertIn("chore: finalize transversal objective batch", source)


if __name__ == "__main__":
    unittest.main()
