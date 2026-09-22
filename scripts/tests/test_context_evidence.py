from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests._git_bash import bash_command


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
HELPER = CONTEXT_ROOT / "scripts" / "context-evidence.py"


def run(*arguments: str | Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(value) for value in arguments],
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class ContextEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces"
        self.root.mkdir()
        run("git", "init", "-b", "main", cwd=self.root)
        run("git", "config", "user.email", "tests@example.com", cwd=self.root)
        run("git", "config", "user.name", "Tests", cwd=self.root)
        (self.root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (self.root / "tracked.txt").write_text("before\n", encoding="utf-8")
        run("git", "add", ".", cwd=self.root)
        run("git", "commit", "-m", "initial", cwd=self.root)

        (self.root / "tracked.txt").write_text("after\n", encoding="utf-8")
        (self.root / "new file.txt").write_text("new text with spaces\n", encoding="utf-8")
        (self.root / "ignored.txt").write_text("ignored secret\n", encoding="utf-8")
        (self.root / "binary.bin").write_bytes(b"\x00\x01binary")
        (self.root / "binary-data.dat").write_bytes(b"text-prefix\x00binary")
        (self.root / "archive.zip").write_bytes(b"PK\x03\x04")
        (self.root / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
        (self.root / "credentials.txt").write_text("password=secret\n", encoding="utf-8")
        (self.root / "coverage.xml").write_text("<coverage/>\n", encoding="utf-8")
        runtime = self.root / "node_modules"
        runtime.mkdir()
        (runtime / "runtime.js").write_text("generated\n", encoding="utf-8")
        (self.root / "huge.txt").write_bytes(b"x" * (1024 * 1024 + 1))

        fixtures = {
            "sbm": "#!/usr/bin/env bash\necho sbm\n",
            "sbm.cmd": "@echo off\r\necho sbm\r\n",
            "scripts/sbm-cli.py": "print('cli behavior')\n",
            "scripts/path-portability.py": "print('path behavior')\n",
        }
        for relative, content in fixtures.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")

        self.diff = Path(self.temp.name) / "git-diff.patch"
        self.changed = Path(self.temp.name) / "changed-files.txt"
        self.omissions = Path(self.temp.name) / "omissions.tsv"

    def execute_helper(self) -> None:
        runner = Path(self.temp.name) / "run-evidence.sh"
        runner.write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\npython3 \"$@\"\n",
            encoding="utf-8",
            newline="\n",
        )
        runner.chmod(0o755)
        environment = os.environ.copy()
        result = subprocess.run(
            bash_command(
                runner,
                HELPER,
                "--project-root",
                self.root,
                "--diff-output",
                self.diff,
                "--changed-output",
                self.changed,
                "--omissions-output",
                self.omissions,
            ),
            cwd=self.root,
            env=environment,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_combines_tracked_and_safe_untracked_evidence_portably(self) -> None:
        self.execute_helper()
        patch = self.diff.read_text(encoding="utf-8")
        changed = self.changed.read_text(encoding="utf-8").splitlines()
        omissions = dict(
            line.split("\t", 1)
            for line in self.omissions.read_text(encoding="utf-8").splitlines()
        )

        self.assertIn("diff --git a/tracked.txt b/tracked.txt", patch)
        self.assertIn("+after", patch)
        self.assertIn("diff --git a/new file.txt b/new file.txt", patch)
        self.assertIn("new file mode 100644", patch)
        self.assertIn("+new text with spaces", patch)

        expected_new = {
            "sbm": "echo sbm",
            "sbm.cmd": "echo sbm",
            "scripts/sbm-cli.py": "cli behavior",
            "scripts/path-portability.py": "path behavior",
        }
        for relative, evidence in expected_new.items():
            with self.subTest(relative=relative):
                self.assertIn(f"diff --git a/{relative} b/{relative}", patch)
                self.assertIn(evidence, patch)
                self.assertIn(relative, changed)

        for excluded in (
            "ignored.txt",
            "binary.bin",
            "binary-data.dat",
            "archive.zip",
            ".env",
            "credentials.txt",
            "coverage.xml",
            "node_modules/runtime.js",
            "huge.txt",
        ):
            with self.subTest(excluded=excluded):
                self.assertNotIn(excluded, patch)
                self.assertNotIn(excluded, changed)

        self.assertNotIn("ignored.txt", omissions)
        self.assertEqual(omissions["binary.bin"], "binary-or-archive-extension")
        self.assertEqual(omissions["binary-data.dat"], "binary-content")
        self.assertEqual(omissions["archive.zip"], "binary-or-archive-extension")
        self.assertEqual(omissions[".env"], "sensitive-path")
        self.assertEqual(omissions["credentials.txt"], "sensitive-path")
        self.assertEqual(omissions["coverage.xml"], "generated-artifact")
        self.assertEqual(
            omissions["node_modules/runtime.js"], "runtime-or-generated-directory"
        )
        self.assertEqual(omissions["huge.txt"], "file-too-large>1048576")

    def test_context_deploy_uses_file_based_canonical_evidence(self) -> None:
        source = (CONTEXT_ROOT / "scripts" / "context-deploy.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("context-evidence.py", source)
        self.assertIn('Path(git_diff_path).read_text(encoding="utf-8")', source)
        self.assertNotIn('GIT_DIFF="${GIT_DIFF}"', source)


if __name__ == "__main__":
    unittest.main()
