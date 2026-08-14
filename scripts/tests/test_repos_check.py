import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]


def run(*args, cwd=None, check=True):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=check,
    )


class ReposCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.suite = Path(self.temp.name) / "SBM-SUITE"
        self.context = self.suite / "context"
        scripts = self.context / "scripts"
        scripts.mkdir(parents=True)

        for name in (
            "repos-branches.sh",
            "repos-changes.sh",
            "repos-check.sh",
        ):
            shutil.copy2(SCRIPTS / name, scripts / name)
            (scripts / name).chmod(0o755)

        helper = scripts / "suite-repositories.py"
        helper.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "assert sys.argv[1] == 'list-paths'\n"
            "print('context')\n"
            "print('SBM/APP')\n",
            encoding="utf-8",
        )
        helper.chmod(0o755)

        self._init_repo(self.context)
        self._init_repo(self.suite / "SBM" / "APP")

    def tearDown(self):
        self.temp.cleanup()

    def _init_repo(self, path):
        path.mkdir(parents=True, exist_ok=True)
        run("git", "init", "-q", "-b", "main", path)
        run("git", "-C", path, "config", "user.email", "test@example.com")
        run("git", "-C", path, "config", "user.name", "Test")
        marker = path / ".marker"
        marker.write_text("base\n", encoding="utf-8")
        run("git", "-C", path, "add", "-A")
        run("git", "-C", path, "commit", "-qm", "base")

    def test_branches_includes_context_and_project(self):
        result = run(self.context / "scripts" / "repos-branches.sh")
        self.assertIn("context", result.stdout)
        self.assertIn("SBM/APP", result.stdout)
        self.assertGreaterEqual(result.stdout.count("main"), 2)

    def test_changes_reports_dirty_and_clean_repositories(self):
        (self.suite / "SBM" / "APP" / "new.txt").write_text("dirty\n", encoding="utf-8")
        result = run(self.context / "scripts" / "repos-changes.sh")
        self.assertIn("== context ==", result.stdout)
        self.assertIn("== SBM/APP ==", result.stdout)
        self.assertIn("?? new.txt", result.stdout)
        self.assertIn("CLEAN", result.stdout)

    def test_combined_check_lists_branches_and_changes(self):
        result = run(self.context / "scripts" / "repos-check.sh")
        self.assertIn("### 1/2 BRANCHES", result.stdout)
        self.assertIn("### 2/2 CAMBIOS", result.stdout)
        self.assertIn("context", result.stdout)
        self.assertIn("SBM/APP", result.stdout)
        self.assertNotIn("VERIFICACION", result.stdout)

    def test_combined_check_does_not_validate_expected_branch(self):
        run("git", "-C", self.suite / "SBM" / "APP", "checkout", "-qb", "feature")
        result = run(self.context / "scripts" / "repos-check.sh")
        self.assertEqual(result.returncode, 0)
        self.assertIn("feature", result.stdout)
        self.assertIn("### 2/2 CAMBIOS", result.stdout)

    def test_combined_check_rejects_arguments(self):
        result = run(
            self.context / "scripts" / "repos-check.sh",
            "main",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Uso: ./scripts/repos-check.sh", result.stderr)


if __name__ == "__main__":
    unittest.main()
