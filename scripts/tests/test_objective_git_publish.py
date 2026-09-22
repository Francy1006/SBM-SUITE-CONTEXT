from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.tests._git_bash import bash_command

CONTEXT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_NAMES = (
    "objective-git-publish.sh",
    "objective-branches.sh",
    "suite-repositories.py",
    "git-flow-policy.py",
    "path-portability.py",
    "sbm-cli.py",
    "objective_lifecycle.py",
)
SOURCES = tuple(CONTEXT_ROOT / "scripts" / name for name in SCRIPT_NAMES)


def run(*args: str, cwd: Path, check: bool = True):
    if args[0].endswith(".sh"):
        command = bash_command(args[0], *args[1:])
    elif args[0] == "python3":
        command = (sys.executable, *args[1:])
    else:
        command = args
    environment = os.environ.copy()
    environment.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "GIT_EDITOR": "true",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        env=environment,
        stdin=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
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
            run("git", "config", "core.autocrlf", "false", cwd=repository)
            (repository / "tracked.txt").write_text(relative + "\n", encoding="utf-8", newline="\n")
            run("git", "add", ".", cwd=repository)
            run("git", "commit", "-m", "initial", cwd=repository)
            run("git", "remote", "add", "origin", str(remote), cwd=repository)
            run("git", "push", "-u", "origin", "main", cwd=repository)

        scripts = self.context / "scripts"
        scripts.mkdir(exist_ok=True)
        for source in SOURCES:
            shutil.copy2(source, scripts / source.name)
            (scripts / source.name).chmod(0o755)
        (scripts / "suite-repositories.json").write_text(
            json.dumps(self.repositories), encoding="utf-8", newline="\n"
        )

        self.write_context([], [])
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
            "|---|---|---|---:|---|---|---|\n"
            + rows(pending, "pending")
            + "\n"
        )
        (self.context / "PROJECT_CONTEXT.md").write_text(text, encoding="utf-8", newline="\n")

    def prepare(self, branch: str) -> None:
        for relative in self.repositories:
            run("git", "checkout", "-b", branch, "main", cwd=self.repository(relative))

    def publish(self, objective_id: str, *extra: str):
        return run(
            str(self.context / "scripts/objective-git-publish.sh"),
            objective_id,
            *extra,
            cwd=self.context,
            check=False,
        )

    def current_branch(self, relative: str) -> str:
        return run("git", "branch", "--show-current", cwd=self.repository(relative)).stdout.strip()

    def head(self, relative: str) -> str:
        return run("git", "rev-parse", "HEAD", cwd=self.repository(relative)).stdout.strip()

    def main_head(self, relative: str) -> str:
        return run("git", "rev-parse", "main", cwd=self.repository(relative)).stdout.strip()

    def subject(self, relative: str) -> str:
        return run(
            "git", "log", "-1", "--pretty=%s", cwd=self.repository(relative)
        ).stdout.strip()

    def remote_branch(self, relative: str, branch: str) -> str:
        return run(
            "git", "ls-remote", "--heads", "origin", branch, cwd=self.repository(relative)
        ).stdout.strip()

    def local_branches(self, relative: str) -> str:
        return run("git", "branch", "--list", cwd=self.repository(relative)).stdout

    def upstream(self, relative: str) -> str:
        return run(
            "git",
            "rev-parse",
            "--abbrev-ref",
            "@{upstream}",
            cwd=self.repository(relative),
        ).stdout.strip()

    def porcelain(self, relative: str) -> str:
        return run("git", "status", "--porcelain", cwd=self.repository(relative)).stdout


class ObjectiveGitPublishTests(unittest.TestCase):
    def test_valid_objective_publishes_mixed_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-publishes-checkpoint"
            oid = "OBJ-PUBLISH-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            self.assertEqual(env.porcelain("context"), "")
            self.assertEqual(env.porcelain("SBM/SBM-API"), "")
            (env.repository("DP/DP-API") / "tracked.txt").write_text("changed\n", encoding="utf-8", newline="\n")
            before = {relative: env.head(relative) for relative in env.repositories}
            main_before = {relative: env.main_head(relative) for relative in env.repositories}
            lifecycle_before = (env.context / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")

            result = env.publish(oid)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.subject("DP/DP-API"), f"chore: checkpoint {oid}")
            self.assertNotEqual(env.head("DP/DP-API"), before["DP/DP-API"])
            self.assertEqual(env.head("context"), before["context"])
            self.assertEqual(env.head("SBM/SBM-API"), before["SBM/SBM-API"])
            self.assertEqual(env.subject("context"), "lifecycle")
            for relative in env.repositories:
                self.assertEqual(env.current_branch(relative), branch)
                self.assertIn(branch, env.local_branches(relative))
                self.assertNotEqual(env.remote_branch(relative, branch), "")
                self.assertEqual(env.upstream(relative), f"origin/{branch}")
                self.assertEqual(env.main_head(relative), main_before[relative])
                self.assertNotIn("main", env.current_branch(relative))
            self.assertEqual(
                (env.context / "PROJECT_CONTEXT.md").read_text(encoding="utf-8"),
                lifecycle_before,
            )
            self.assertIn("active", lifecycle_before)

    def test_missing_objective_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-missing-objective"
            env.prepare(branch)
            env.write_context([("OBJ-PRESENT-001", branch)], [])
            before = {relative: env.head(relative) for relative in env.repositories}
            result = env.publish("OBJ-NOT-FOUND")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("objetivo activo no encontrado: OBJ-NOT-FOUND", result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])
                self.assertEqual(env.current_branch(relative), branch)

    def test_objective_without_valid_branch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-invalid-recorded-branch"
            oid = "OBJ-INVALID-BRANCH"
            env.prepare(branch)
            env.write_context([(oid, "N/A")], [])
            before = {relative: env.head(relative) for relative in env.repositories}
            result = env.publish(oid)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("branch lifecycle válida", result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])

    def test_repository_branch_mismatch_aborts_before_any_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-atomic-publish"
            oid = "OBJ-MUST-ABORT"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            (env.repository("context") / "tracked.txt").write_text("dirty context\n", encoding="utf-8", newline="\n")
            (env.repository("DP/DP-API") / "tracked.txt").write_text("dirty api\n", encoding="utf-8", newline="\n")
            before = {relative: env.head(relative) for relative in env.repositories}
            porcelain_before = {relative: env.porcelain(relative) for relative in env.repositories}
            run("git", "checkout", "main", cwd=env.repository("SBM/SBM-API"))
            result = env.publish(oid)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Preflight transversal fallido", result.stderr)
            self.assertIn("no se ejecutó add/commit/push", result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])
                self.assertEqual(env.porcelain(relative), porcelain_before[relative])
                self.assertEqual(env.remote_branch(relative, branch), "")

    def test_windows_and_posix_paths_are_equivalent_for_git_roots(self) -> None:
        helper = CONTEXT_ROOT / "scripts" / "path-portability.py"
        windows = run(
            "python3",
            str(helper),
            "equivalent",
            "F:/DEV/SBM-SUITE/context",
            "/f/DEV/SBM-SUITE/context",
            cwd=CONTEXT_ROOT,
            check=False,
        )
        posix = run(
            "python3",
            str(helper),
            "equivalent",
            "/Users/example/SBM-SUITE/context",
            "/Users/example/SBM-SUITE/context",
            cwd=CONTEXT_ROOT,
            check=False,
        )
        mismatched = run(
            "python3",
            str(helper),
            "equivalent",
            "F:/DEV/SBM-SUITE/context",
            "/Users/example/SBM-SUITE/context",
            cwd=CONTEXT_ROOT,
            check=False,
        )
        self.assertEqual(windows.returncode, 0, windows.stderr)
        self.assertEqual(posix.returncode, 0, posix.stderr)
        self.assertNotEqual(mismatched.returncode, 0)

    def test_non_git_root_path_aborts_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-invalid-git-root"
            oid = "OBJ-ROOT-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            nested = env.repository("DP/DP-API") / "nested"
            nested.mkdir()
            (env.context / "scripts" / "suite-repositories.json").write_text(
                json.dumps(["context", "DP/DP-API/nested", "SBM/SBM-API"]),
                encoding="utf-8",
                newline="\n",
            )
            before = {relative: env.head(relative) for relative in env.repositories}
            result = env.publish(oid)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("raíz", result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])
                self.assertEqual(env.current_branch(relative), branch)

    def test_clean_repository_is_omitted_from_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-clean-publish"
            oid = "OBJ-CLEAN-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            before = env.head("SBM/SBM-API")
            result = env.publish(oid)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.head("SBM/SBM-API"), before)
            self.assertEqual(env.subject("SBM/SBM-API"), "initial")
            self.assertNotEqual(env.remote_branch("SBM/SBM-API", branch), "")

    def test_dirty_repository_creates_checkpoint_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-dirty-publish"
            oid = "OBJ-DIRTY-007"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            (env.repository("context") / "tracked.txt").write_text("context change\n", encoding="utf-8", newline="\n")
            result = env.publish(oid)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.subject("context"), f"chore: checkpoint {oid}")
            self.assertNotEqual(oid, "OBJ-CTX-002")
            self.assertEqual(env.porcelain("context"), "")

    def test_existing_remote_branch_is_updated_without_recreating_main_merge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-existing-remote"
            oid = "OBJ-REMOTE-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            first = env.publish(oid)
            self.assertEqual(first.returncode, 0, first.stderr)
            remote_before = env.remote_branch("DP/DP-API", branch)
            main_before = env.main_head("DP/DP-API")
            (env.repository("DP/DP-API") / "tracked.txt").write_text("second change\n", encoding="utf-8", newline="\n")
            second = env.publish(oid)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertNotEqual(env.remote_branch("DP/DP-API", branch), remote_before)
            self.assertEqual(env.subject("DP/DP-API"), f"chore: checkpoint {oid}")
            self.assertEqual(env.main_head("DP/DP-API"), main_before)
            self.assertEqual(env.current_branch("DP/DP-API"), branch)
            self.assertIn(branch, env.local_branches("DP/DP-API"))
            self.assertNotEqual(env.remote_branch("DP/DP-API", branch), "")

    def test_in_sync_remote_skips_unnecessary_push_and_keeps_upstream(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-skips-push"
            oid = "OBJ-SKIP-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            first = env.publish(oid)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {relative: env.head(relative) for relative in env.repositories}
            second = env.publish(oid)
            self.assertEqual(second.returncode, 0, second.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])
                self.assertEqual(env.current_branch(relative), branch)
                self.assertEqual(env.upstream(relative), f"origin/{branch}")

    def test_cli_script_rejects_manual_branch_argument(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-rejects-manual-branch"
            oid = "OBJ-MANUAL-001"
            env.prepare(branch)
            env.write_context([(oid, branch)], [])
            before = env.head("context")
            result = env.publish(oid, branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Uso:", result.stderr)
            self.assertEqual(env.head("context"), before)

    def test_source_stays_independent_from_finalize_and_resolves_lifecycle_branch(self) -> None:
        source = (CONTEXT_ROOT / "scripts/objective-git-publish.sh").read_text(encoding="utf-8")
        dispatcher = (CONTEXT_ROOT / "sbm").read_text(encoding="utf-8")
        self.assertIn("sbm-cli.py", source)
        self.assertIn("path-portability.py", source)
        self.assertIn("suite-repositories.py", source)
        self.assertIn("git-flow-policy.py", source)
        self.assertIn('COMMIT_MESSAGE="chore: checkpoint ${OBJECTIVE_ID}"', source)
        self.assertNotIn("OBJ-CTX-002", source)
        self.assertNotIn("checkout main", source)
        self.assertNotIn("merge --no-ff", source)
        self.assertNotIn("objective-git-cleanup.sh", source)
        self.assertNotIn("push origin main", source)
        self.assertNotIn("branch -d", source)
        self.assertNotIn("branch -D", source)
        self.assertNotIn("push origin --delete", source)
        self.assertIn('bash "${ROOT}/scripts/objective-git-publish.sh" "${OBJECTIVE_ID}"', dispatcher)
        self.assertIn("sbm git publish [objective_id]", dispatcher)


if __name__ == "__main__":
    unittest.main()
