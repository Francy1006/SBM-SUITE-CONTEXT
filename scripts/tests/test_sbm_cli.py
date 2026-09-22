from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.tests._git_bash import bash_command


CONTEXT_ROOT = Path(__file__).resolve().parents[2]


class SbmCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.context = Path(self.temp.name) / "context"
        (self.context / "scripts").mkdir(parents=True)
        (self.context / "QA").mkdir()
        self.sbm = self.context / "sbm"
        shutil.copy2(CONTEXT_ROOT / "sbm", self.sbm)
        self.sbm.chmod(0o755)
        self._install_context_python()
        for name in ("sbm-cli.py", "objective_lifecycle.py"):
            shutil.copy2(CONTEXT_ROOT / "scripts" / name, self.context / "scripts" / name)
        for relative in (
            "QA/qa-full.sh",
            "scripts/context-deploy.sh",
            "scripts/context-upgrade.sh",
            "scripts/documentation-deploy.sh",
            "scripts/documentation-upgrade.sh",
            "scripts/objective-git-finalize.sh",
            "scripts/objective-git-publish.sh",
            "scripts/objective-git-pull.sh",
        ):
            self._write_stub(relative)
        self.log = self.context / "dispatch.log"
        self.write_active(("OBJ-TEST-001", "FEATURE-tests-short-cli"))

    def _install_context_python(self) -> None:
        if os.name == "nt":
            scripts = self.context / ".venv" / "Scripts"
            scripts.mkdir(parents=True)
            shutil.copy2(CONTEXT_ROOT / ".venv" / "Scripts" / "python.exe", scripts)
            shutil.copy2(
                CONTEXT_ROOT / ".venv" / "pyvenv.cfg",
                self.context / ".venv" / "pyvenv.cfg",
            )
            return
        binary = self.context / ".venv" / "bin" / "python3"
        binary.parent.mkdir(parents=True)
        binary.write_text(
            "#!/usr/bin/env bash\nexec python3 \"$@\"\n",
            encoding="utf-8",
            newline="\n",
        )
        binary.chmod(0o755)

    def _write_stub(self, relative: str) -> None:
        target = self.context / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "printf '%s\\0' \"${BASH_SOURCE[0]}\" \"$@\" >> \"${SBM_TEST_LOG}\"\n",
            encoding="utf-8",
            newline="\n",
        )
        target.chmod(0o755)

    def write_active(self, *items: tuple[str, str]) -> None:
        rows = "\n".join(
            f"| {objective_id} | TEST | Objective | active | 5 | N/A | {branch} | N/A |"
            for objective_id, branch in items
        )
        (self.context / "PROJECT_CONTEXT.md").write_text(
            "# PROJECT_CONTEXT.md\n\n"
            "## 3. Active objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n"
            f"{rows}\n\n"
            "## 4. Pending objectives\n\n"
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |\n"
            "|---|---|---|---|---:|---|---|---|\n",
            encoding="utf-8",
        )

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment.update(
            SBM_TEST_LOG=str(self.log),
        )
        return subprocess.run(
            bash_command(self.sbm, *arguments),
            cwd=self.context,
            env=environment,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def invocation(self) -> list[str]:
        values = self.log.read_bytes().decode("utf-8").split("\0")
        return values[:-1]

    def test_single_active_objective_is_selected_automatically(self) -> None:
        cases = (
            (
                ("qa",),
                "qa-full.sh",
                [
                    "--branch", "FEATURE-tests-short-cli",
                    "--objectives-json", '[{"objective_id":"OBJ-TEST-001"}]',
                    "--sonarqube-ready",
                ],
            ),
            (
                ("context", "deploy"),
                "context-deploy.sh",
                ["implementation-progress", '[{"objective_id":"OBJ-TEST-001"}]'],
            ),
            (
                ("git", "finalize"),
                "objective-git-finalize.sh",
                ["OBJ-TEST-001", "FEATURE-tests-short-cli"],
            ),
            (
                ("git", "publish"),
                "objective-git-publish.sh",
                ["OBJ-TEST-001"],
            ),
            (
                ("git", "pull"),
                "objective-git-pull.sh",
                ["OBJ-TEST-001"],
            ),
        )
        for arguments, script_name, expected_args in cases:
            with self.subTest(arguments=arguments):
                self.log.unlink(missing_ok=True)
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                invocation = self.invocation()
                self.assertEqual(Path(invocation[0]).name, script_name)
                self.assertEqual(invocation[1:], expected_args)
                self.assertFalse(any("\r" in value for value in invocation))

    def test_explicit_objective_selects_from_multiple_active_objectives(self) -> None:
        self.write_active(
            ("OBJ-TEST-001", "FEATURE-tests-short-cli"),
            ("OBJ-TEST-002", "BUGFIX-fixes-short-cli"),
        )
        cases = (
            (
                ("qa", "OBJ-TEST-002"),
                "qa-full.sh",
                [
                    "--branch", "BUGFIX-fixes-short-cli",
                    "--objectives-json", '[{"objective_id":"OBJ-TEST-002"}]',
                    "--sonarqube-ready",
                ],
            ),
            (
                ("context", "deploy", "OBJ-TEST-002"),
                "context-deploy.sh",
                ["implementation-progress", '[{"objective_id":"OBJ-TEST-002"}]'],
            ),
            (
                ("git", "finalize", "OBJ-TEST-002"),
                "objective-git-finalize.sh",
                ["OBJ-TEST-002", "BUGFIX-fixes-short-cli"],
            ),
            (
                ("git", "publish", "OBJ-TEST-002"),
                "objective-git-publish.sh",
                ["OBJ-TEST-002"],
            ),
            (
                ("git", "pull", "OBJ-TEST-002"),
                "objective-git-pull.sh",
                ["OBJ-TEST-002"],
            ),
        )
        for arguments, script_name, expected_args in cases:
            with self.subTest(arguments=arguments):
                self.log.unlink(missing_ok=True)
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                invocation = self.invocation()
                self.assertEqual(Path(invocation[0]).name, script_name)
                self.assertEqual(invocation[1:], expected_args)

    def test_commands_without_lifecycle_payload_dispatch_directly(self) -> None:
        cases = (
            (("context", "upgrade"), "context-upgrade.sh"),
            (("documentation", "deploy"), "documentation-deploy.sh"),
            (("documentation", "upgrade"), "documentation-upgrade.sh"),
        )
        for arguments, script_name in cases:
            with self.subTest(arguments=arguments):
                self.log.unlink(missing_ok=True)
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                invocation = self.invocation()
                self.assertEqual(Path(invocation[0]).name, script_name)
                self.assertEqual(invocation[1:], [])

    def test_ambiguous_active_objective_fails_without_dispatch(self) -> None:
        self.write_active(
            ("OBJ-TEST-001", "FEATURE-tests-short-cli"),
            ("OBJ-TEST-002", "FEATURE-tests-short-cli"),
        )
        result = self.run_cli("qa")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("objetivo activo ambiguo: OBJ-TEST-001, OBJ-TEST-002", result.stderr)
        self.assertIn("sbm qa OBJ-TEST-001", result.stderr)
        self.assertFalse(self.log.exists())

    def test_unknown_objective_is_rejected_without_dispatch(self) -> None:
        result = self.run_cli("qa", "OBJ-NOT-FOUND")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("objetivo activo no encontrado: OBJ-NOT-FOUND", result.stderr)
        self.assertFalse(self.log.exists())

    def test_user_facing_cli_does_not_accept_branch_argument(self) -> None:
        for arguments in (
            ("qa", "OBJ-TEST-001", "FEATURE-manual-branch"),
            ("git", "publish", "OBJ-TEST-001", "FEATURE-manual-branch"),
            ("git", "pull", "OBJ-TEST-001", "FEATURE-manual-branch"),
        ):
            with self.subTest(arguments=arguments):
                self.log.unlink(missing_ok=True)
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.log.exists())

    def test_windows_cmd_wrapper_uses_git_for_windows_not_wsl(self) -> None:
        source = (CONTEXT_ROOT / "sbm.cmd").read_text(encoding="utf-8")
        self.assertIn("where git.exe", source)
        self.assertIn("\\Windows\\System32\\", source)
        self.assertNotIn("E:\\Programs Files\\Git", source)
        if os.name == "nt":
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", str(CONTEXT_ROOT / "sbm.cmd"), "--help"],
                cwd=CONTEXT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sbm git pull", result.stdout)
            self.assertIn("sbm git publish", result.stdout)
            self.assertIn("sbm git finalize", result.stdout)


if __name__ == "__main__":
    unittest.main()
