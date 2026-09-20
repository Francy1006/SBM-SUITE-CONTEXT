from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]


def bash_executable() -> str:
    if os.name != "nt":
        return shutil.which("bash") or "bash"
    git = Path(shutil.which("git") or "git")
    candidate = git.parent.parent / "bin" / "bash.exe"
    if not candidate.is_file():
        raise RuntimeError("Git Bash no está disponible para ejecutar repos-pull.sh")
    return str(candidate)


BASH = bash_executable()


def run(*args, cwd=None, check=True):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=check,
    )


class PullEnvironment:
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
            repository = self.repository(relative)
            repository.mkdir(parents=True)
            remote = self.remote(relative)
            run("git", "init", "--bare", remote, cwd=root)
            run("git", "init", "-b", "main", cwd=repository)
            self.configure(repository)
            (repository / "tracked.txt").write_text(relative + "\n", encoding="utf-8")
            run("git", "add", ".", cwd=repository)
            run("git", "commit", "-m", "initial", cwd=repository)
            run("git", "remote", "add", "origin", remote, cwd=repository)
            run("git", "push", "-u", "origin", "main", cwd=repository)

        scripts = self.context / "scripts"
        scripts.mkdir(exist_ok=True)
        for name in ("repos-pull.sh", "suite-repositories.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
            (scripts / name).chmod(0o755)
        (scripts / "suite-repositories.json").write_text(
            json.dumps(self.repositories), encoding="utf-8"
        )
        run("git", "add", ".", cwd=self.context)
        run("git", "commit", "-m", "add scripts", cwd=self.context)
        run("git", "push", "origin", "main", cwd=self.context)

    def repository(self, relative: str) -> Path:
        return self.suite / relative

    def remote(self, relative: str) -> Path:
        return self.remotes / f"{relative.replace('/', '-')}.git"

    @staticmethod
    def configure(repository: Path) -> None:
        run("git", "config", "user.email", "tests@example.com", cwd=repository)
        run("git", "config", "user.name", "Tests", cwd=repository)

    def execute(self):
        return run(
            BASH,
            "./scripts/repos-pull.sh",
            cwd=self.context,
            check=False,
        )

    def branch(self, relative: str) -> str:
        return run(
            "git", "branch", "--show-current", cwd=self.repository(relative)
        ).stdout.strip()

    def head(self, relative: str) -> str:
        return run("git", "rev-parse", "HEAD", cwd=self.repository(relative)).stdout.strip()

    def checkout_branch(self, relative: str, branch: str, *, publish: bool = True) -> None:
        repository = self.repository(relative)
        run("git", "checkout", "-b", branch, cwd=repository)
        if publish:
            run("git", "push", "-u", "origin", branch, cwd=repository)

    def commit_local(self, relative: str, text: str = "local") -> str:
        repository = self.repository(relative)
        with (repository / "tracked.txt").open("a", encoding="utf-8") as stream:
            stream.write(text + "\n")
        run("git", "add", "tracked.txt", cwd=repository)
        run("git", "commit", "-m", text, cwd=repository)
        return self.head(relative)

    def advance_remote(self, relative: str, branch: str | None = None) -> str:
        branch = branch or self.branch(relative)
        publisher = self.publishers / f"{relative.replace('/', '-')}-{len(list(self.publishers.iterdir()))}"
        run("git", "clone", self.remote(relative), publisher, cwd=self.root)
        self.configure(publisher)
        run("git", "checkout", branch, cwd=publisher)
        with (publisher / "tracked.txt").open("a", encoding="utf-8") as stream:
            stream.write("remote\n")
        run("git", "add", "tracked.txt", cwd=publisher)
        run("git", "commit", "-m", "remote advance", cwd=publisher)
        run("git", "push", "origin", branch, cwd=publisher)
        return run("git", "rev-parse", "HEAD", cwd=publisher).stdout.strip()


class ReposPullTests(unittest.TestCase):
    def test_multiple_repositories_keep_distinct_current_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            env.checkout_branch("DP/DP-API", "FEATURE-one")
            env.checkout_branch("SBM/SBM-API", "RELEASE-two")

            result = env.execute()

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.branch("context"), "main")
            self.assertEqual(env.branch("DP/DP-API"), "FEATURE-one")
            self.assertEqual(env.branch("SBM/SBM-API"), "RELEASE-two")
            self.assertIn("FEATURE-one", result.stdout)
            self.assertIn("RELEASE-two", result.stdout)

    def test_clean_up_to_date_repositories_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))

            result = env.execute()

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("up-to-date", result.stdout)
            self.assertIn("Ya actualizados: 3", result.stdout)

    def test_fast_forward_is_applied_from_fetched_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            expected = env.advance_remote("DP/DP-API")

            result = env.execute()

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.head("DP/DP-API"), expected)
            self.assertIn("fast-forward", result.stdout)
            self.assertIn("Sincronizados mediante fast-forward: 1", result.stdout)

    def test_dirty_tracked_file_fails_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            (env.repository("DP/DP-API") / "tracked.txt").write_text(
                "dirty\n", encoding="utf-8"
            )

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("DP/DP-API", result.stderr)
            self.assertIn("working tree", result.stderr)

    def test_untracked_file_fails_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            (env.repository("SBM/SBM-API") / "untracked.txt").write_text(
                "dirty\n", encoding="utf-8"
            )

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SBM/SBM-API", result.stderr)
            self.assertIn("tracked o untracked", result.stderr)

    def test_detached_head_fails_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            run("git", "checkout", "--detach", cwd=env.repository("DP/DP-API"))

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("detached HEAD", result.stderr)

    def test_missing_remote_branch_fails_before_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            env.checkout_branch("DP/DP-API", "BUGFIX-local-only", publish=False)
            before = env.head("context")

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("origin/BUGFIX-local-only inexistente", result.stderr)
            self.assertEqual(env.head("context"), before)

    def test_diverged_branch_aborts_before_any_working_tree_update(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            fast_forward_before = env.head("DP/DP-API")
            env.advance_remote("DP/DP-API")
            env.commit_local("SBM/SBM-API", "local divergence")
            env.advance_remote("SBM/SBM-API")

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("divergida", result.stderr)
            self.assertEqual(env.head("DP/DP-API"), fast_forward_before)

    def test_local_ahead_is_accepted_without_modification(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            expected = env.commit_local("DP/DP-API")

            result = env.execute()

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(env.head("DP/DP-API"), expected)
            self.assertIn("local-ahead", result.stdout)
            self.assertIn("Local-ahead: 1", result.stdout)

    def test_preflight_error_prevents_fetch_and_updates_everywhere(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            repository = env.repository("DP/DP-API")
            tracking_before = run(
                "git", "rev-parse", "origin/main", cwd=repository
            ).stdout.strip()
            env.advance_remote("DP/DP-API")
            (env.repository("SBM/SBM-API") / "untracked.txt").write_text(
                "blocks all phases\n", encoding="utf-8"
            )
            head_before = env.head("DP/DP-API")

            result = env.execute()

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no se ejecutó fetch", result.stderr)
            self.assertEqual(env.head("DP/DP-API"), head_before)
            tracking_after = run(
                "git", "rev-parse", "origin/main", cwd=repository
            ).stdout.strip()
            self.assertEqual(tracking_after, tracking_before)

    def test_rejects_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            env = PullEnvironment(Path(directory))
            result = run(
                BASH,
                "./scripts/repos-pull.sh",
                "main",
                cwd=env.context,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("./scripts/repos-pull.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
