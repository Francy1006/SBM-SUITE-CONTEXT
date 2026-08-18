from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
CLEANUP_SOURCE = CONTEXT_ROOT / "scripts" / "objective-git-cleanup.sh"
REPOSITORY_SOURCE = CONTEXT_ROOT / "scripts" / "suite-repositories.py"
POLICY_SOURCE = CONTEXT_ROOT / "scripts" / "git-flow-policy.py"
STATE_SOURCE = CONTEXT_ROOT / "scripts" / "objective-git-state.py"


def _run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class CleanupEnvironment:
    repositories = ("context", "DP/DP-API", "SBM/SBM-API")

    def __init__(self, root: Path):
        self.root = root
        self.suite_root = root / "SBM-SUITE"
        self.context_root = self.suite_root / "context"
        self.remotes = root / "remotes"
        self.remotes.mkdir(parents=True)
        for repository in self.repositories:
            self._initialize_repository(repository)
        self._write_project_context()
        self._write_completed_objectives()
        scripts = self.context_root / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CLEANUP_SOURCE, scripts / CLEANUP_SOURCE.name)
        shutil.copy2(REPOSITORY_SOURCE, scripts / REPOSITORY_SOURCE.name)
        shutil.copy2(POLICY_SOURCE, scripts / POLICY_SOURCE.name)
        shutil.copy2(STATE_SOURCE, scripts / STATE_SOURCE.name)
        (scripts / CLEANUP_SOURCE.name).chmod(0o755)
        (scripts / REPOSITORY_SOURCE.name).chmod(0o755)
        (scripts / POLICY_SOURCE.name).chmod(0o755)
        (scripts / STATE_SOURCE.name).chmod(0o755)
        _run("git", "add", ".", cwd=self.context_root)
        _run("git", "commit", "-m", "add cleanup", cwd=self.context_root)
        _run("git", "push", "origin", "main", cwd=self.context_root)

    def _initialize_repository(self, relative_path: str) -> None:
        repository = self.suite_root / relative_path
        repository.mkdir(parents=True, exist_ok=True)
        remote = self.remotes / (relative_path.replace("/", "-") + ".git")
        _run("git", "init", "--bare", str(remote), cwd=self.root)
        _run("git", "init", "-b", "main", cwd=repository)
        _run("git", "config", "user.email", "tests@example.com", cwd=repository)
        _run("git", "config", "user.name", "Cleanup Tests", cwd=repository)
        (repository / "tracked.txt").write_text(relative_path + "\n", encoding="utf-8")
        _run("git", "add", ".", cwd=repository)
        _run("git", "commit", "-m", "initial", cwd=repository)
        _run("git", "remote", "add", "origin", str(remote), cwd=repository)
        _run("git", "push", "-u", "origin", "main", cwd=repository)

    def _write_project_context(self) -> None:
        rows = []
        for index, repository in enumerate(self.repositories, start=1):
            logical = repository.lower() if repository != "context" else repository
            main_context = "context/PROJECT_CONTEXT.md" if logical == "context" else f"{logical}/context/PROJECT_CONTEXT.md"
            rows.append(
                f"| P{index} | purpose | Not defined | Not defined | N/A | `{main_context}` | N/A | N/A |"
            )
        content = (
            "# PROJECT_CONTEXT.md\n\n"
            "## 3. Active objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n\n"
            "## 4. Pending objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n\n"
            "## 6. Project objective summaries\n\n"
            "| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |\n"
            "|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n## 7. Boundary\n"
        )
        (self.context_root / "PROJECT_CONTEXT.md").write_text(content, encoding="utf-8")

    def _write_completed_objectives(self) -> None:
        content = (
            "# COMPLETED_OBJECTIVES.md\n\n"
            "## 1. Completed objectives by project\n\n"
            "### TEST\n\n"
            "| Objective ID | Project | Objective | Final status | Priority | Branch | Started | Completed | Summary | Validation | Documentation | Proposed commit |\n"
            "|---|---|---|---|---:|---|---|---|---|---|---|---|\n"
            "| OBJ-CLEAN-001 | TEST | Cleanup | completed | 5 | FEATURE-clean-me | N/A | 2026-08-14 | done | passed | docs/cleanup.md | N/A |\n\n"
            "## 2. Document boundary\n"
        )
        (self.context_root / "COMPLETED_OBJECTIVES.md").write_text(content, encoding="utf-8")

    def prepare_merged_branches(self) -> None:
        for relative_path in self.repositories:
            repository = self.suite_root / relative_path
            _run("git", "checkout", "-b", "FEATURE-clean-me", "main", cwd=repository)
            (repository / "branch.txt").write_text("branch\n", encoding="utf-8")
            _run("git", "add", ".", cwd=repository)
            _run("git", "commit", "-m", "branch work", cwd=repository)
            _run("git", "push", "-u", "origin", "FEATURE-clean-me", cwd=repository)
            _run("git", "checkout", "main", cwd=repository)
            _run("git", "merge", "--no-ff", "FEATURE-clean-me", "-m", "merge branch", cwd=repository)
            _run("git", "push", "origin", "main", cwd=repository)

    def cleanup(self) -> subprocess.CompletedProcess[str]:
        return _run(
            str(self.context_root / "scripts" / "objective-git-cleanup.sh"),
            "OBJ-CLEAN-001",
            "FEATURE-clean-me",
            cwd=self.context_root,
            check=False,
        )


class ObjectiveGitCleanupTests(unittest.TestCase):
    def test_cleanup_deletes_local_and_remote_branches_after_global_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = CleanupEnvironment(Path(directory))
            env.prepare_merged_branches()

            result = env.cleanup()

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative_path in env.repositories:
                repository = env.suite_root / relative_path
                self.assertEqual(_run("git", "branch", "--show-current", cwd=repository).stdout.strip(), "main")
                self.assertNotEqual(
                    _run("git", "show-ref", "--verify", "--quiet", "refs/heads/FEATURE-clean-me", cwd=repository, check=False).returncode,
                    0,
                )
                self.assertNotEqual(
                    _run("git", "ls-remote", "--exit-code", "origin", "refs/heads/FEATURE-clean-me", cwd=repository, check=False).returncode,
                    0,
                )

    def test_wrong_branch_aborts_before_deleting_any_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = CleanupEnvironment(Path(directory))
            env.prepare_merged_branches()
            _run("git", "checkout", "FEATURE-clean-me", cwd=env.suite_root / "SBM/SBM-API")

            result = env.cleanup()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("branch actual no es main", result.stderr)
            for relative_path in env.repositories:
                repository = env.suite_root / relative_path
                self.assertEqual(
                    _run("git", "show-ref", "--verify", "--quiet", "refs/heads/FEATURE-clean-me", cwd=repository, check=False).returncode,
                    0,
                )

    def test_unmerged_branch_aborts_before_deleting_any_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = CleanupEnvironment(Path(directory))
            env.prepare_merged_branches()
            repository = env.suite_root / "DP/DP-API"
            _run("git", "checkout", "FEATURE-clean-me", cwd=repository)
            (repository / "unmerged.txt").write_text("unmerged\n", encoding="utf-8")
            _run("git", "add", ".", cwd=repository)
            _run("git", "commit", "-m", "unmerged", cwd=repository)
            _run("git", "push", "origin", "FEATURE-clean-me", cwd=repository)
            _run("git", "checkout", "main", cwd=repository)

            result = env.cleanup()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no está integrada en main", result.stderr)
            self.assertEqual(
                _run("git", "show-ref", "--verify", "--quiet", "refs/heads/FEATURE-clean-me", cwd=env.suite_root / "context", check=False).returncode,
                0,
            )


if __name__ == "__main__":
    unittest.main()
