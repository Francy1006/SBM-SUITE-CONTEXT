from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
FINALIZE_SOURCE = CONTEXT_ROOT / "scripts" / "objective-git-finalize.sh"
BRANCH_SOURCE = CONTEXT_ROOT / "scripts" / "objective-branches.sh"
REPOSITORY_SOURCE = CONTEXT_ROOT / "scripts" / "suite-repositories.py"


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
        self._write_completed_objectives([])
        scripts = self.context_root / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FINALIZE_SOURCE, scripts / FINALIZE_SOURCE.name)
        shutil.copy2(BRANCH_SOURCE, scripts / BRANCH_SOURCE.name)
        shutil.copy2(REPOSITORY_SOURCE, scripts / REPOSITORY_SOURCE.name)
        (scripts / FINALIZE_SOURCE.name).chmod(0o755)
        (scripts / BRANCH_SOURCE.name).chmod(0o755)
        (scripts / REPOSITORY_SOURCE.name).chmod(0o755)
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

    def _write_project_context(
        self,
        active: tuple[tuple[str, str], ...] = (),
        pending: tuple[tuple[str, str], ...] = (),
    ) -> None:
        def objective_rows(items: tuple[tuple[str, str], ...], status: str) -> str:
            return "\n".join(
                f"| {objective_id} | TEST | Objective {objective_id} | {status} | 5 | N/A | {branch} | N/A |"
                for objective_id, branch in items
            )

        rows = []
        for index, repository in enumerate(self.repositories, start=1):
            main_context = (
                "context/PROJECT_CONTEXT.md"
                if repository == "context"
                else f"{repository}/context/PROJECT_CONTEXT.md"
            )
            rows.append(
                f"| P{index} | purpose | Not defined | Not defined | N/A | "
                f"`{main_context}` | N/A | N/A |"
            )
        content = (
            "# PROJECT_CONTEXT.md\n\n"
            "## 3. Active objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n"
            + objective_rows(active, "active")
            + "\n\n## 4. Pending objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n"
            + objective_rows(pending, "pending")
            + "\n\n## 6. Project objective summaries\n\n"
            "| Project | Purpose | Active objective | Pending objectives | Branch | "
            "Main context | QA context | Documentation |\n"
            "|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n## 7. Boundary\n"
        )
        (self.context_root / "PROJECT_CONTEXT.md").write_text(content, encoding="utf-8")

    def _write_completed_objectives(self, records: list[tuple[str, str, str]]) -> None:
        rows = "\n".join(
            f"| {objective_id} | TEST | Objective {objective_id} | {status} | 5 | {branch} | "
            "N/A | 2026-08-14 | done | QA passed | N/A | N/A |"
            for objective_id, branch, status in records
        )
        content = (
            "# COMPLETED_OBJECTIVES.md\n\n"
            "## 1. Completed objectives by project\n\n"
            "### TEST\n\n"
            "| Objective ID | Project | Objective | Final status | Priority | Branch | Started | "
            "Completed | Summary | Validation | Documentation | Proposed commit |\n"
            "|---|---|---|---|---:|---|---|---|---|---|---|---|\n"
            + rows
            + "\n\n## 2. Document boundary\n"
        )
        (self.context_root / "COMPLETED_OBJECTIVES.md").write_text(content, encoding="utf-8")

    def repository(self, relative_path: str) -> Path:
        return self.suite_root / relative_path

    def prepare_branch(self, branch: str) -> None:
        for relative_path in self.repositories:
            repository = self.repository(relative_path)
            _run("git", "checkout", "-b", branch, cwd=repository)

    def mark_completed(self, objective_id: str, branch: str, status: str = "completed") -> None:
        self._write_completed_objectives([(objective_id, branch, status)])

    def finalize(self, objective_id: str, branch: str) -> subprocess.CompletedProcess[str]:
        return _run(
            str(self.context_root / "scripts" / "objective-git-finalize.sh"),
            objective_id,
            branch,
            cwd=self.context_root,
            check=False,
        )


class ObjectiveGitFinalizeTests(unittest.TestCase):
    def test_completed_objective_commits_pushes_merges_and_uses_neutral_message(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-FINALIZE-001"
            branch = "FEATURE-finalize-objective"
            env.prepare_branch(branch)
            env.mark_completed(objective_id, branch)
            changed_repo = env.repository("dp/DP-API")
            with (changed_repo / "tracked.txt").open("a", encoding="utf-8") as handle:
                handle.write("changed\n")

            result = env.finalize(objective_id, branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative_path in ("context", "dp/DP-API"):
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
                    _run("git", "log", branch, "-1", "--pretty=%s", cwd=repository).stdout.strip(),
                    f"chore(objective): finalize {objective_id}",
                )

            unchanged = env.repository("sbm/SBM-API")
            self.assertEqual(_run("git", "branch", "--show-current", cwd=unchanged).stdout.strip(), "main")
            self.assertEqual(_run("git", "status", "--porcelain", cwd=unchanged).stdout, "")

    def test_not_completed_aborts_before_any_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-NOT-CLOSED"
            branch = "FEATURE-not-closed"
            env.prepare_branch(branch)
            changed_repo = env.repository("dp/DP-API")
            (changed_repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            before = _run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip()

            result = env.finalize(objective_id, branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no está completed", result.stderr)
            self.assertEqual(_run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip(), before)
            self.assertNotEqual(_run("git", "status", "--porcelain", cwd=changed_repo).stdout, "")

    def test_completed_branch_mismatch_aborts_before_any_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-BRANCH-MISMATCH"
            branch = "FEATURE-current-branch"
            env.prepare_branch(branch)
            env.mark_completed(objective_id, "FEATURE-other-branch")

            result = env.finalize(objective_id, branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Branch de cierre", result.stderr)

    def test_objective_still_active_aborts_even_if_completed_record_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-STILL-ACTIVE"
            branch = "FEATURE-still-active"
            env.prepare_branch(branch)
            env.mark_completed(objective_id, branch)
            env._write_project_context(active=((objective_id, branch),))

            result = env.finalize(objective_id, branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("todavía figura como active", result.stderr)

    def test_global_branch_verification_failure_aborts_before_any_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-MUST-ABORT"
            branch = "FEATURE-must-abort"
            env.prepare_branch(branch)
            env.mark_completed(objective_id, branch)
            changed_repo = env.repository("dp/DP-API")
            (changed_repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            before = _run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip()
            _run("git", "checkout", "main", cwd=env.repository("sbm/SBM-API"))

            result = env.finalize(objective_id, branch)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(_run("git", "rev-parse", "HEAD", cwd=changed_repo).stdout.strip(), before)
            self.assertNotEqual(_run("git", "status", "--porcelain", cwd=changed_repo).stdout, "")

    def test_completed_objective_with_clean_repositories_is_successful_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = FinalizeEnvironment(Path(directory))
            objective_id = "OBJ-NO-CHANGES"
            branch = "FEATURE-no-changes"
            env.prepare_branch(branch)
            env.mark_completed(objective_id, branch)
            _run("git", "add", "COMPLETED_OBJECTIVES.md", cwd=env.context_root)
            _run("git", "commit", "-m", "close objective", cwd=env.context_root)

            result = env.finalize(objective_id, branch)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Sin repositorios con cambios", result.stdout)
            for relative_path in env.repositories:
                self.assertEqual(
                    _run("git", "branch", "--show-current", cwd=env.repository(relative_path)).stdout.strip(),
                    "main",
                )

    def test_agent_contract_allows_finalization_only_after_closure(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        section = contract.split(
            "#### Transversal Git finalization after closure only", maxsplit=1
        )[1].split("### Option 6 — Documentación", maxsplit=1)[0]

        self.assertIn("implementation-closure", section)
        self.assertIn("implementation-progress", section)
        self.assertIn("must never offer or execute Git finalization", section)
        self.assertIn("COMPLETED_OBJECTIVES.md", section)
        self.assertIn('objective-git-finalize.sh "<objective-id>" "<objective-branch-from-context>"', section)
        self.assertIn("chore(objective): finalize <objective-id>", section)
        self.assertIn("all SBM repositories end on `main`", section)
        self.assertIn("objective-git-cleanup.sh", section)


if __name__ == "__main__":
    unittest.main()
