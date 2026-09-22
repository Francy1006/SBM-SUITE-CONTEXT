import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from scripts.tests._git_bash import bash_command


SCRIPTS = Path(__file__).resolve().parents[1]


def run(*args, cwd=None, check=True):
    command = (
        bash_command(args[0], *args[1:])
        if str(args[0]).endswith(".sh")
        else [str(arg) for arg in args]
    )
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )


class ReposCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.suite = Path(self.temp.name) / "SBM SUITE"
        self.context = self.suite / "context"
        self.app = self.suite / "SBM" / "APP"
        self.remotes = Path(self.temp.name) / "remotes"
        scripts = self.context / "scripts"
        scripts.mkdir(parents=True)
        self.remotes.mkdir()

        for name in ("repos-check.sh", "path-portability.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
            (scripts / name).chmod(0o755)

        helper = scripts / "suite-repositories.py"
        helper.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "sys.stdout.reconfigure(newline='\\n')\n"
            "assert sys.argv[1] == 'list-paths'\n"
            "sys.stdout.write('context\\nSBM/APP\\n')\n",
            encoding="utf-8",
            newline="\n",
        )
        helper.chmod(0o755)

        self._init_repo(self.context, "context.git")
        self._init_repo(self.app, "app.git")

    def tearDown(self):
        self.temp.cleanup()

    def _init_repo(self, path, remote_name):
        remote = self.remotes / remote_name
        run("git", "init", "--bare", "-q", remote)
        path.mkdir(parents=True, exist_ok=True)
        run("git", "init", "-q", "-b", "main", path)
        run("git", "-C", path, "config", "user.email", "test@example.com")
        run("git", "-C", path, "config", "user.name", "Test")
        marker = path / ".marker"
        marker.write_text("base\n", encoding="utf-8", newline="\n")
        run("git", "-C", path, "add", "-A")
        run("git", "-C", path, "commit", "-qm", "base")
        run("git", "-C", path, "remote", "add", "origin", remote)
        run("git", "-C", path, "push", "-qu", "origin", "main")

    def _check(self, check=True):
        return run(self.context / "scripts" / "repos-check.sh", check=check)

    def test_all_clean_repositories_report_branch_upstream_and_counts(self):
        result = self._check()
        self.assertIn(
            "context | branch=main | estado=limpio | upstream=origin/main | "
            "ahead=0 behind=0",
            result.stdout,
        )
        self.assertIn(
            "SBM/APP | branch=main | estado=limpio | upstream=origin/main | "
            "ahead=0 behind=0",
            result.stdout,
        )
        self.assertTrue(
            result.stdout.rstrip().endswith("Check transversal completado correctamente.")
        )

    def test_dirty_repository_is_reported_without_being_an_error(self):
        (self.app / "new file.txt").write_text(
            "dirty\n", encoding="utf-8", newline="\n"
        )
        result = self._check()
        self.assertEqual(result.returncode, 0)
        self.assertIn("SBM/APP | branch=main | estado=con cambios", result.stdout)

    def test_distinct_branch_and_repository_without_upstream(self):
        run("git", "-C", self.app, "checkout", "-qb", "FEATURE-independent")
        result = self._check()
        self.assertIn("context | branch=main", result.stdout)
        self.assertIn("SBM/APP | branch=FEATURE-independent", result.stdout)
        self.assertIn("upstream=sin upstream | ahead=- behind=-", result.stdout)

    def test_ahead_and_behind_are_calculated_from_local_upstream_refs(self):
        (self.context / ".marker").write_text(
            "local ahead\n", encoding="utf-8", newline="\n"
        )
        run("git", "-C", self.context, "commit", "-qam", "local ahead")

        contributor = Path(self.temp.name) / "contributor"
        run(
            "git", "clone", "-q", "--branch", "main",
            self.remotes / "app.git", contributor,
        )
        run("git", "-C", contributor, "config", "user.email", "test@example.com")
        run("git", "-C", contributor, "config", "user.name", "Test")
        (contributor / ".marker").write_text(
            "remote ahead\n", encoding="utf-8", newline="\n"
        )
        run("git", "-C", contributor, "commit", "-qam", "remote ahead")
        run("git", "-C", contributor, "push", "-q", "origin", "main")
        run("git", "-C", self.app, "fetch", "-q", "origin")

        result = self._check()
        self.assertRegex(result.stdout, r"context .* ahead=1 behind=0")
        self.assertRegex(result.stdout, r"SBM/APP .* ahead=0 behind=1")

    def test_missing_repository_is_reported_after_other_repositories(self):
        self.app.rename(self.app.with_name("APP-away"))
        result = self._check(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("context | branch=main", result.stdout)
        self.assertIn("SBM/APP | branch=- | estado=error", result.stdout)
        self.assertIn("repositorio inexistente", result.stdout)
        self.assertIn("Check transversal completado con errores", result.stderr)

    def test_non_git_directory_is_reported_without_stopping_the_check(self):
        (self.app / ".git").rename(self.app / ".git-away")
        result = self._check(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("context | branch=main", result.stdout)
        self.assertIn("SBM/APP | branch=- | estado=error", result.stdout)
        self.assertIn("no es un repositorio Git", result.stdout)

    def test_paths_with_spaces_work_on_native_windows_and_posix(self):
        result = self._check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SBM/APP | branch=main", result.stdout)
        if os.name == "nt":
            self.assertRegex(str(self.suite), r"^[A-Za-z]:\\")
        else:
            self.assertTrue(str(self.suite).startswith("/"))

    def test_check_is_read_only(self):
        before = {
            path: (
                run("git", "-C", path, "rev-parse", "HEAD").stdout,
                run("git", "-C", path, "for-each-ref", "--format=%(refname) %(objectname)").stdout,
                run("git", "-C", path, "status", "--porcelain").stdout,
            )
            for path in (self.context, self.app)
        }
        self._check()
        after = {
            path: (
                run("git", "-C", path, "rev-parse", "HEAD").stdout,
                run("git", "-C", path, "for-each-ref", "--format=%(refname) %(objectname)").stdout,
                run("git", "-C", path, "status", "--porcelain").stdout,
            )
            for path in (self.context, self.app)
        }
        self.assertEqual(after, before)

        source = (SCRIPTS / "repos-check.sh").read_text(encoding="utf-8")
        forbidden = r"\bgit\s+(?:-[^ ]+\s+)*?(checkout|fetch|pull|commit|push|reset|clean|switch|merge|rebase)\b"
        self.assertIsNone(re.search(forbidden, source))

    def test_rejects_arguments(self):
        result = run(
            self.context / "scripts" / "repos-check.sh",
            "main",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Uso: ./scripts/repos-check.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
