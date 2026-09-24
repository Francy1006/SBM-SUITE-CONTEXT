from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from scripts.tests._git_bash import bash_executable


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
def parse_args(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            bash_executable(),
            "-c",
            'source "$1"; shift; context_deploy_parse_args "$@" || exit $?; '
            'printf "%s\\n%s\\n%s\\n%s\\n" "$PROJECT_NAME" '
            '"$LIFECYCLE_PHASE" "$OBJECTIVES_SOURCE" "$USER_PROMPT"',
            "context-deploy-cli-test",
            "./scripts/context-deploy-args.sh",
            *args,
        ],
        cwd=CONTEXT_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


class ContextDeployCliTests(unittest.TestCase):
    def assert_parsed(self, args: tuple[str, ...], expected: list[str]) -> None:
        result = parse_args(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), expected)

    def test_short_syntax_defaults_to_context_with_optional_prompt(self) -> None:
        objectives = "objectives-json"
        self.assert_parsed(
            ("implementation-progress", objectives),
            ["sbm-suite-context", "implementation-progress", objectives, ""],
        )
        self.assert_parsed(
            ("implementation-progress", objectives, "continue implementation"),
            [
                "sbm-suite-context",
                "implementation-progress",
                objectives,
                "continue implementation",
            ],
        )

    def test_long_syntax_remains_compatible_with_optional_prompt(self) -> None:
        objectives = "objectives-json"
        self.assert_parsed(
            ("other-project", "implementation-progress", objectives),
            ["other-project", "implementation-progress", objectives, ""],
        )
        self.assert_parsed(
            ("other-project", "implementation-progress", objectives, "prompt"),
            ["other-project", "implementation-progress", objectives, "prompt"],
        )

    def test_other_project_cannot_use_short_syntax(self) -> None:
        result = parse_args("other-project", "[]")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_lifecycle_phase_is_rejected(self) -> None:
        result = subprocess.run(
            [
                bash_executable(),
                "-c",
                'source "$1"; context_deploy_is_lifecycle_phase "$2"',
                "context-deploy-cli-test",
                "./scripts/context-deploy-args.sh",
                "invalid-phase",
            ],
            cwd=CONTEXT_ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
