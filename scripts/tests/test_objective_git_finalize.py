from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CONTEXT_ROOT = Path(__file__).resolve().parents[2]
SOURCES = tuple(
    CONTEXT_ROOT / "scripts" / name
    for name in (
        "objective-git-finalize.sh",
        "objective-branches.sh",
        "suite-repositories.py",
        "git-flow-policy.py",
    )
)


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
            f"2026-08-18 | done | full QA passed | docs/{oid}.md | N/A |"
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

    def finalize(self, ids, branch):
        return run(
            str(self.context / "scripts/objective-git-finalize.sh"),
            *ids,
            branch,
            cwd=self.context,
            check=False,
        )


class ObjectiveGitFinalizeTests(unittest.TestCase):
    def test_completed_objective_finalizes_without_gate_and_preserves_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-finalizes-objective"
            objective_id = "OBJ-FINALIZE-001"
            env.prepare(branch)
            env.write_completed([(objective_id, branch, "completed")])
            (env.repository("DP/DP-API") / "tracked.txt").write_text(
                "changed\n", encoding="utf-8"
            )

            self.assertFalse((env.context / "QA/output/finalization-gate.json").exists())
            self.assertFalse(
                (env.context / "documentation/output/finalization-gate.json").exists()
            )

            result = env.finalize((objective_id,), branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("finalization-gate", result.stderr)
            for relative in env.repositories:
                repository = env.repository(relative)
                self.assertEqual(
                    run("git", "branch", "--show-current", cwd=repository).stdout.strip(),
                    "main",
                )
                self.assertEqual(run("git", "status", "--porcelain", cwd=repository).stdout, "")
                self.assertEqual(
                    run(
                        "git",
                        "show-ref",
                        "--verify",
                        "--quiet",
                        f"refs/heads/{branch}",
                        cwd=repository,
                        check=False,
                    ).returncode,
                    0,
                )

            for relative in ("context", "DP/DP-API"):
                repository = env.repository(relative)
                self.assertEqual(
                    run(
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        branch,
                        "main",
                        cwd=repository,
                        check=False,
                    ).returncode,
                    0,
                )
                self.assertNotEqual(
                    run(
                        "git",
                        "ls-remote",
                        "--heads",
                        "origin",
                        branch,
                        cwd=repository,
                    ).stdout.strip(),
                    "",
                )
                self.assertEqual(
                    run(
                        "git",
                        "log",
                        branch,
                        "-1",
                        "--pretty=%s",
                        cwd=repository,
                    ).stdout.strip(),
                    f"chore(objective): finalize {objective_id}",
                )

    def test_active_objective_is_rejected_even_without_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-still-active"
            objective_id = "OBJ-STILL-ACTIVE"
            env.prepare(branch)
            env.write_context([(objective_id, branch)], [])

            result = env.finalize((objective_id,), branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("todavía figura como active", result.stderr)
            for relative in env.repositories:
                self.assertEqual(
                    run(
                        "git", "branch", "--show-current", cwd=env.repository(relative)
                    ).stdout.strip(),
                    branch,
                )

    def test_completed_branch_mismatch_aborts_before_git_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-current-branch"
            objective_id = "OBJ-BRANCH-MISMATCH"
            env.prepare(branch)
            env.write_completed(
                [(objective_id, "FEATURE-other-branch", "completed")]
            )
            before = {
                relative: run(
                    "git", "rev-parse", "HEAD", cwd=env.repository(relative)
                ).stdout
                for relative in env.repositories
            }

            result = env.finalize((objective_id,), branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Branch de cierre", result.stderr)
            for relative in env.repositories:
                self.assertEqual(
                    run("git", "rev-parse", "HEAD", cwd=env.repository(relative)).stdout,
                    before[relative],
                )

    def test_non_completed_final_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-not-completed"
            objective_id = "OBJ-NOT-COMPLETED"
            env.prepare(branch)
            env.write_completed([(objective_id, branch, "registered")])

            result = env.finalize((objective_id,), branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Final status=completed", result.stderr)

    def test_wrong_repository_branch_aborts_before_any_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-atomic-finalization"
            objective_id = "OBJ-MUST-ABORT"
            env.prepare(branch)
            env.write_completed([(objective_id, branch, "completed")])
            (env.repository("DP/DP-API") / "tracked.txt").write_text(
                "dirty\n", encoding="utf-8"
            )
            before = {
                relative: run(
                    "git", "rev-parse", "HEAD", cwd=env.repository(relative)
                ).stdout
                for relative in env.repositories
            }
            run("git", "checkout", "main", cwd=env.repository("SBM/SBM-API"))

            result = env.finalize((objective_id,), branch)

            self.assertNotEqual(result.returncode, 0)
            for relative in env.repositories:
                self.assertEqual(
                    run("git", "rev-parse", "HEAD", cwd=env.repository(relative)).stdout,
                    before[relative],
                )

    def test_completed_batch_remains_supported_without_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-completes-batch"
            ids = ("OBJ-BATCH-001", "OBJ-BATCH-002")
            env.prepare(branch)
            env.write_completed(
                [(ids[0], branch, "completed"), (ids[1], branch, "completed")]
            )

            result = env.finalize(ids, branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                run("git", "branch", "--show-current", cwd=env.context).stdout.strip(),
                "main",
            )

    def test_source_has_no_finalization_gate_dependency(self):
        source = (CONTEXT_ROOT / "scripts/objective-git-finalize.sh").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("finalization-gate.json", source)
        self.assertNotIn("verify-finalization-gates", source)
        self.assertNotIn("QA_GATE_FILE", source)
        self.assertNotIn("DOCUMENTATION_GATE_FILE", source)


if __name__ == "__main__":
    unittest.main()
