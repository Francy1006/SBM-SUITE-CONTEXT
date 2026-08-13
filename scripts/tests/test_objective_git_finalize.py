from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
FINALIZE_SOURCE = CONTEXT_ROOT / "scripts" / "objective-git-finalize.sh"
BRANCH_SOURCE = CONTEXT_ROOT / "scripts" / "objective-branches.sh"


def _run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class FinalizeEnvironment:
    repositories = ("context", "dp/DP-API", "sbm/SBM-API")

    def __init__(self, root: Path):
        self.root = root
        self.suite_root = root / "SBM-SUITE"
        self.context_root = self.suite_root / "context"
        self.remotes = root / "remotes"
        self.remotes.mkdir(parents=True)

        for repository in self.repositories:
            self._initialize_repository(repository)

        self._write_project_context()
        scripts = self.context_root / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FINALIZE_SOURCE, scripts / FINALIZE_SOURCE.name)
        shutil.copy2(BRANCH_SOURCE, scripts / BRANCH_SOURCE.name)
        (scripts / FINALIZE_SOURCE.name).chmod(0o755)
        (scripts / BRANCH_SOURCE.name).chmod(0o755)
        _run("git", "add", ".", cwd=self.context_root)
        _run("git", "commit", "-m", "add lifecycle scripts", cwd=self.context_root)
        _run("git", "push", "origin", "main", cwd=self.context_root)

    def _initialize_repository(self, relative_path: str) -> None:
        repository = self.suite_root / relative_path
        repository.mkdir(parents=True, exist_ok=True)
        remote = self.remotes / (relative_path.replace("/", "-") + ".git")
        _run("git", "init", "--bare", str(remote), cwd=self.root)
        _run("git", "init", "-b", "main", cwd=repository)
        _run("git", "config", "user.email", "tests@example.com", cwd=repository)
        _run("git", "config", "user.name", "Finalize Tests", cwd=repository)
        (repository / "tracked.txt").write_text(relative_path + "\n", encoding="utf-8")
        _run("git", "add", ".", cwd=repository)
        _run("git", "commit", "-m", "initial", cwd=repository)
        _run("git", "remote", "add", "origin", str(remote), cwd=repository)
        _run("git", "push", "-u", "origin", "main", cwd=repository)

    def _write_project_context(self) -> None:
        rows = []
        for index, repository in enumerate(self.repositories, start=1):
            main_context = (
                "context/PROJECT_CONTEXT.md"
                if repository == "context"
                else f"{repository}/context/PROJECT_CONTEXT.md"
            )
            rows.append(
                f"| P{index} | purpose | active | pending | `FEATURE-old` | "
                f"`{main_context}` | N/A | N/A |"
            )
        content = (
            "# PROJECT_CONTEXT.md\n\n"
            "## 6. Project objective summaries\n\n"
            "| Project | Purpose | Active objective | Pending objectives | Branch | "
            "Main context | QA context | Documentation |\n"
            "|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n## 7. Boundary\n"
        )
        (self.context_root / "PROJECT_CONTEXT.md").write_text(content, encoding="utf-8")

    def repository(self, relative_path: str) -> Path:
        return self.suite_root / relative_path

    def prepare_branch(self, branch: str) -> None:
        for relative_path in self.repositories:
            repository = self.repository(relative_path)
            _run("git", "checkout", "-b", branch, cwd=repository)

    def finalize(self, branch: str, message: str) -> subprocess.CompletedProcess[str]:
        return _run(
            str(self.context_root / "scripts" / "objective-git-finalize.sh"),
            branch,
            message,
            cwd=self.context_root,
            check=False,
        )


class ObjectiveGitFinalizeTests(unittest.TestCase):
    def test_changed_repositories_commit_push_merge_and_unchanged_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            branch = "FEATURE-finalize-objective"
            env.prepare_branch(branch)
            changed = ("context", "dp/DP-API")
            unchanged = "sbm/SBM-API"

            for relative_path in changed:
                with (env.repository(relative_path) / "tracked.txt").open("a", encoding="utf-8") as handle:
                    handle.write("changed\n")

            unchanged_before = _run(
                "git", "rev-list", "--count", "HEAD", cwd=env.repository(unchanged)
            ).stdout.strip()

            result = env.finalize(branch, "feat: finalize objective")

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative_path in changed:
                repository = env.repository(relative_path)
                self.assertEqual(
                    _run("git", "branch", "--show-current", cwd=repository).stdout.strip(),
                    "main",
                )
                self.assertEqual(_run("git", "status", "--porcelain", cwd=repository).stdout, "")
                self.assertEqual(
                    _run(
                        "git", "merge-base", "--is-ancestor", branch, "main", cwd=repository, check=False
                    ).returncode,
                    0,
                )
                self.assertEqual(
                    _run(
                        "git", "ls-remote", "--heads", "origin", branch, cwd=repository
                    ).stdout.strip() != "",
                    True,
                )

            self.assertEqual(
                _run("git", "branch", "--show-current", cwd=env.repository(unchanged)).stdout.strip(),
                branch,
            )
            self.assertEqual(
                _run("git", "rev-list", "--count", "HEAD", cwd=env.repository(unchanged)).stdout.strip(),
                unchanged_before,
            )

    def test_global_branch_verification_failure_aborts_before_any_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            branch = "FEATURE-must-abort"
            env.prepare_branch(branch)
            changed_repo = env.repository("dp/DP-API")
            (changed_repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            before = _run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip()
            _run("git", "checkout", "main", cwd=env.repository("sbm/SBM-API"))

            result = env.finalize(branch, "feat: should not commit")

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(_run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip(), before)
            self.assertNotEqual(_run("git", "status", "--porcelain", cwd=changed_repo).stdout, "")

    def test_no_changes_is_successful_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            branch = "FEATURE-no-changes"
            env.prepare_branch(branch)

            result = env.finalize(branch, "feat: no changes")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Sin repositorios con cambios", result.stdout)

    def test_agent_contract_offers_transversal_finalization_after_progress_or_closure(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        section = contract.split(
            "#### Optional transversal Git finalization for progress and closure", maxsplit=1
        )[1].split("### Option 6 — Documentación", maxsplit=1)[0]

        self.assertIn("implementation-progress", section)
        self.assertIn("implementation-closure", section)
        self.assertIn("objective-git-finalize.sh", section)
        self.assertIn("offer", section.lower())
        self.assertIn("git add .", section)
        self.assertIn("merge", section)
        self.assertIn("omit repositories with no changes", section)


if __name__ == "__main__":
    unittest.main()
