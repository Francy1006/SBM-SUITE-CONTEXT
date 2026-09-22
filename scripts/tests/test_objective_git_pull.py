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
    "objective-git-pull.sh",
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
        self.publishers = root / "publishers"
        self.remotes.mkdir()
        self.publishers.mkdir()

        for relative in self.repositories:
            repository = self.suite / relative
            repository.mkdir(parents=True)
            remote = self.remote(relative)
            run("git", "init", "--bare", str(remote), cwd=root)
            run("git", "init", "-b", "main", cwd=repository)
            run("git", "config", "user.email", "tests@example.com", cwd=repository)
            run("git", "config", "user.name", "Tests", cwd=repository)
            run("git", "config", "core.autocrlf", "false", cwd=repository)
            (repository / "tracked.txt").write_text(
                relative + "\n", encoding="utf-8", newline="\n"
            )
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

    def remote(self, relative: str) -> Path:
        return self.remotes / f"{relative.replace('/', '-')}.git"

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
        (self.context / "PROJECT_CONTEXT.md").write_text(text, encoding="utf-8", newline="\n")

    def publish_branch(self, branch: str) -> None:
        for relative in self.repositories:
            repository = self.repository(relative)
            run("git", "checkout", "-b", branch, "main", cwd=repository)
            run("git", "push", "-u", "origin", branch, cwd=repository)

    def advance_remote(self, relative: str, branch: str) -> str:
        publisher = self.publishers / f"{relative.replace('/', '-')}-{len(list(self.publishers.iterdir()))}"
        run("git", "clone", str(self.remote(relative)), str(publisher), cwd=self.root)
        run("git", "config", "user.email", "tests@example.com", cwd=publisher)
        run("git", "config", "user.name", "Tests", cwd=publisher)
        run("git", "checkout", branch, cwd=publisher)
        with (publisher / "tracked.txt").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("remote\n")
        run("git", "add", "tracked.txt", cwd=publisher)
        run("git", "commit", "-m", "remote advance", cwd=publisher)
        run("git", "push", "origin", branch, cwd=publisher)
        return run("git", "rev-parse", "HEAD", cwd=publisher).stdout.strip()

    def pull(self, objective_id: str, *extra: str):
        return run(
            str(self.context / "scripts/objective-git-pull.sh"),
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

    def tracking(self, relative: str, ref: str) -> str:
        return run("git", "rev-parse", ref, cwd=self.repository(relative)).stdout.strip()

    def local_branches(self, relative: str) -> str:
        return run("git", "branch", "--list", cwd=self.repository(relative)).stdout

    def porcelain(self, relative: str) -> str:
        return run("git", "status", "--porcelain", cwd=self.repository(relative)).stdout


class ObjectiveGitPullTests(unittest.TestCase):
    def test_local_remote_relationship_states(self) -> None:
        for behind, ahead in ((0, 0), (1, 0), (0, 1), (1, 1)):
            with self.subTest(behind=behind, ahead=ahead), tempfile.TemporaryDirectory() as directory:
                env = Environment(Path(directory))
                branch = "FEATURE-relationship-states"
                oid = "OBJ-PULL-007"
                env.write_context([(oid, branch)], [])
                run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
                run("git", "commit", "-m", "lifecycle", cwd=env.context)
                env.publish_branch(branch)
                if ahead:
                    (env.context / "local-only.txt").write_text("local\n", encoding="utf-8")
                    run("git", "add", "local-only.txt", cwd=env.context)
                    run("git", "commit", "-m", "local advance", cwd=env.context)
                remote_head = env.tracking("context", f"origin/{branch}")
                if behind:
                    remote_head = env.advance_remote("context", branch)
                # The script must fetch this remote head before evaluating the relationship.
                run("git", "checkout", "main", cwd=env.repository("DP/DP-API"))
                before = {
                    relative: (env.head(relative), env.current_branch(relative), env.porcelain(relative))
                    for relative in env.repositories
                }
                main_before = {relative: env.main_head(relative) for relative in env.repositories}
                lifecycle_before = (env.context / "PROJECT_CONTEXT.md").read_bytes()

                result = env.pull(oid)

                self.assertEqual(env.tracking("context", f"origin/{branch}"), remote_head)
                counts = run(
                    "git", "rev-list", "--left-right", "--count",
                    f"origin/{branch}...{before['context'][0]}", cwd=env.context,
                ).stdout.split()
                self.assertEqual(counts, [str(behind), str(ahead)])
                if behind and ahead:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("divergencia", result.stderr)
                    self.assertIn("no se modificó ningún working tree", result.stderr)
                    for relative in env.repositories:
                        self.assertEqual(
                            (env.head(relative), env.current_branch(relative), env.porcelain(relative)),
                            before[relative],
                        )
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(env.head("context"), before["context"][0] if ahead else remote_head)
                    for relative in env.repositories:
                        self.assertEqual(env.current_branch(relative), branch)
                        self.assertEqual(env.porcelain(relative), "")
                if ahead:
                    self.assertEqual((env.context / "local-only.txt").read_text(encoding="utf-8"), "local\n")
                for relative in env.repositories:
                    self.assertEqual(env.main_head(relative), main_before[relative])
                self.assertEqual((env.context / "PROJECT_CONTEXT.md").read_bytes(), lifecycle_before)

    def test_existing_local_branch_fast_forwards_from_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-pulls-existing"
            oid = "OBJ-PULL-001"
            env.publish_branch(branch)
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            run("git", "push", "origin", branch, cwd=env.context)
            expected = env.advance_remote("DP/DP-API", branch)
            main_before = {relative: env.main_head(relative) for relative in env.repositories}
            lifecycle_before = (env.context / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")

            result = env.pull(oid)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.head("DP/DP-API"), expected)
            for relative in env.repositories:
                self.assertEqual(env.current_branch(relative), branch)
                self.assertEqual(env.main_head(relative), main_before[relative])
            self.assertEqual(
                (env.context / "PROJECT_CONTEXT.md").read_text(encoding="utf-8"),
                lifecycle_before,
            )

    def test_missing_local_branch_is_created_tracking_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-pulls-tracking"
            oid = "OBJ-PULL-002"
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            run("git", "push", "origin", "main", cwd=env.context)
            env.publish_branch(branch)
            expected = {relative: env.head(relative) for relative in env.repositories}
            for relative in env.repositories:
                run("git", "checkout", "main", cwd=env.repository(relative))
                run("git", "branch", "-D", branch, cwd=env.repository(relative))
                self.assertNotIn(branch, env.local_branches(relative))

            result = env.pull(oid)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.current_branch(relative), branch)
                self.assertEqual(env.head(relative), expected[relative])
                self.assertIn(branch, env.local_branches(relative))
                self.assertEqual(
                    run(
                        "git",
                        "rev-parse",
                        "--abbrev-ref",
                        "@{upstream}",
                        cwd=env.repository(relative),
                    ).stdout.strip(),
                    f"origin/{branch}",
                )

    def test_fetch_discovers_remote_branch_missing_from_initial_clone(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-discovers-remote"
            oid = "OBJ-PULL-006"
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            run("git", "push", "origin", "main", cwd=env.context)
            expected = {}
            for relative in env.repositories:
                repository = env.repository(relative)
                publisher = env.publishers / relative.replace("/", "-")
                repository.rename(publisher)
                run("git", "clone", "--branch", "main", str(env.remote(relative)),
                    str(repository), cwd=env.root)
                run("git", "checkout", "-b", branch, cwd=publisher)
                (publisher / "remote-only.txt").write_text("discovered\n", encoding="utf-8")
                run("git", "add", "remote-only.txt", cwd=publisher)
                run("git", "commit", "-m", "publish objective", cwd=publisher)
                run("git", "push", "origin", branch, cwd=publisher)
                expected[relative] = run("git", "rev-parse", "HEAD", cwd=publisher).stdout.strip()
                self.assertNotEqual(run(
                    "git", "show-ref", "--verify", "--quiet",
                    f"refs/remotes/origin/{branch}", cwd=repository, check=False,
                ).returncode, 0)
                self.assertNotIn(branch, env.local_branches(relative))
            main_before = {relative: env.main_head(relative) for relative in env.repositories}
            lifecycle_before = (env.context / "PROJECT_CONTEXT.md").read_bytes()

            result = env.pull(oid)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.current_branch(relative), branch)
                self.assertEqual(env.head(relative), expected[relative])
                self.assertEqual(env.tracking(relative, f"origin/{branch}"), expected[relative])
                self.assertEqual(env.main_head(relative), main_before[relative])
                self.assertEqual(env.porcelain(relative), "")
                self.assertEqual(run(
                    "git", "rev-parse", "--abbrev-ref", "@{upstream}",
                    cwd=env.repository(relative),
                ).stdout.strip(), f"origin/{branch}")
                self.assertEqual(
                    (env.repository(relative) / "remote-only.txt").read_text(encoding="utf-8"),
                    "discovered\n",
                )
            self.assertEqual((env.context / "PROJECT_CONTEXT.md").read_bytes(), lifecycle_before)

    def test_missing_remote_branch_aborts_before_working_tree_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-missing-remote"
            oid = "OBJ-PULL-003"
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            for relative in env.repositories:
                run("git", "checkout", "-b", branch, "main", cwd=env.repository(relative))
            before = {relative: env.head(relative) for relative in env.repositories}
            current = {relative: env.current_branch(relative) for relative in env.repositories}

            result = env.pull(oid)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("origin/FEATURE-missing-remote inexistente", result.stderr)
            self.assertIn("no se modificó ningún working tree", result.stderr)
            for relative in env.repositories:
                self.assertEqual(env.head(relative), before[relative])
                self.assertEqual(env.current_branch(relative), current[relative])

    def test_dirty_repository_aborts_before_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-dirty-pull"
            oid = "OBJ-PULL-004"
            env.publish_branch(branch)
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            tracking_before = env.tracking("DP/DP-API", f"origin/{branch}")
            env.advance_remote("DP/DP-API", branch)
            (env.repository("SBM/SBM-API") / "tracked.txt").write_text(
                "dirty\n", encoding="utf-8", newline="\n"
            )
            before = {
                relative: (env.head(relative), env.current_branch(relative), env.porcelain(relative))
                for relative in env.repositories
            }

            result = env.pull(oid)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working tree contiene cambios locales", result.stderr)
            self.assertIn("no se ejecutó fetch", result.stderr)
            for relative in env.repositories:
                self.assertEqual(
                    (env.head(relative), env.current_branch(relative), env.porcelain(relative)),
                    before[relative],
                )
            self.assertEqual(env.tracking("DP/DP-API", f"origin/{branch}"), tracking_before)
            self.assertEqual(
                (env.repository("SBM/SBM-API") / "tracked.txt").read_text(encoding="utf-8"),
                "dirty\n",
            )

    def test_diverged_history_rejects_non_fast_forward(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-rejects-divergence"
            oid = "OBJ-PULL-005"
            env.publish_branch(branch)
            env.write_context([(oid, branch)], [])
            run("git", "add", "PROJECT_CONTEXT.md", cwd=env.context)
            run("git", "commit", "-m", "lifecycle", cwd=env.context)
            run("git", "push", "origin", branch, cwd=env.context)
            ff_before = env.head("DP/DP-API")
            env.advance_remote("DP/DP-API", branch)
            with (env.repository("SBM/SBM-API") / "tracked.txt").open(
                "a", encoding="utf-8", newline="\n"
            ) as stream:
                stream.write("local\n")
            run("git", "add", "tracked.txt", cwd=env.repository("SBM/SBM-API"))
            run("git", "commit", "-m", "local divergence", cwd=env.repository("SBM/SBM-API"))
            env.advance_remote("SBM/SBM-API", branch)
            current = {relative: env.current_branch(relative) for relative in env.repositories}

            result = env.pull(oid)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no admite fast-forward", result.stderr)
            self.assertEqual(env.head("DP/DP-API"), ff_before)
            for relative in env.repositories:
                self.assertEqual(env.current_branch(relative), current[relative])

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
        self.assertEqual(windows.returncode, 0, windows.stderr)
        self.assertEqual(posix.returncode, 0, posix.stderr)

    def test_cli_script_rejects_manual_branch_and_resolves_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env = Environment(Path(directory))
            branch = "FEATURE-rejects-manual"
            oid = "OBJ-PULL-006"
            env.write_context([(oid, branch)], [])
            result = env.pull(oid, branch)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Uso:", result.stderr)

        source = (CONTEXT_ROOT / "scripts/objective-git-pull.sh").read_text(encoding="utf-8")
        dispatcher = (CONTEXT_ROOT / "sbm").read_text(encoding="utf-8")
        self.assertIn("sbm-cli.py", source)
        self.assertIn("path-portability.py", source)
        self.assertIn("suite-repositories.py", source)
        self.assertIn('pull --ff-only origin "${OBJECTIVE_BRANCH}"', source)
        self.assertIn('checkout --track "origin/${OBJECTIVE_BRANCH}"', source)
        self.assertNotIn("merge --no-ff", source)
        self.assertNotIn("checkout main", source)
        self.assertNotIn("git commit", source)
        self.assertNotIn("git push", source)
        self.assertIn('bash "${ROOT}/scripts/objective-git-pull.sh" "${OBJECTIVE_ID}"', dispatcher)
        self.assertIn("sbm git pull [objective_id]", dispatcher)


if __name__ == "__main__":
    unittest.main()
