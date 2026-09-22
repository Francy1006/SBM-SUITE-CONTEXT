from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
HELPER_SOURCE = CONTEXT_ROOT / "scripts" / "suite-repositories.py"


class SuiteRepositoriesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.suite = Path(self.temp.name) / "SBM-SUITE"
        self.context = self.suite / "context"
        self.scripts = self.context / "scripts"
        self.scripts.mkdir(parents=True)
        self.helper = self.scripts / "suite-repositories.py"
        shutil.copy2(HELPER_SOURCE, self.helper)

    def write_inventory(self, repositories: list[object]) -> None:
        (self.scripts / "suite-repositories.json").write_text(
            json.dumps(repositories), encoding="utf-8"
        )

    def run_helper(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.helper), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def run_helper_raw(self, *arguments: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(self.helper), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_stdout_uses_only_lf_for_all_output_modes(self) -> None:
        self.write_inventory(["TEAM/ARBITRARY-REPOSITORY", "context"])
        expected = {
            ("list",): (
                b"context\tcontext\n"
                b"ARBITRARY-REPOSITORY\tTEAM/ARBITRARY-REPOSITORY\n"
            ),
            ("list-paths",): b"context\nTEAM/ARBITRARY-REPOSITORY\n",
            ("resolve", "arbitrary-repository"): b"TEAM/ARBITRARY-REPOSITORY\n",
        }

        for arguments, expected_stdout in expected.items():
            with self.subTest(arguments=arguments):
                result = self.run_helper_raw(*arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected_stdout)
                self.assertNotIn(b"\r", result.stdout)

    def test_inventory_is_independent_from_locally_cloned_repositories(self) -> None:
        repositories = [
            "context",
            "DP/DP-API",
            "DP/DP-STORE",
            "PC/PC-STORE",
            "TEAM/ARBITRARY-REPOSITORY",
        ]
        self.write_inventory(repositories)
        (self.suite / "DP/DP-API/.git").mkdir(parents=True)
        (self.suite / "context/.git").mkdir()

        first = self.run_helper("list-paths")
        (self.suite / "DP/DP-STORE/.git").mkdir(parents=True)
        (self.suite / "PC/PC-STORE").mkdir(parents=True)
        (self.suite / "PC/PC-STORE/.git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        second = self.run_helper("list-paths")

        expected = "\n".join(repositories) + "\n"
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, expected)
        self.assertEqual(second.stdout, expected)

    def test_list_and_resolve_derive_project_names_generically(self) -> None:
        self.write_inventory(["TEAM/ARBITRARY-REPOSITORY", "context"])

        listed = self.run_helper("list")
        resolved = self.run_helper("resolve", "arbitrary-repository")

        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(
            listed.stdout,
            "context\tcontext\nARBITRARY-REPOSITORY\tTEAM/ARBITRARY-REPOSITORY\n",
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertEqual(resolved.stdout, "TEAM/ARBITRARY-REPOSITORY\n")

    def test_rejects_noncanonical_and_case_ambiguous_inventory(self) -> None:
        for inventory in (
            ["context", "../OUTSIDE"],
            ["context", "TEAM\\PROJECT"],
            ["context", "TEAM/PROJECT", "team/project"],
            ["context", 42],
        ):
            with self.subTest(inventory=inventory):
                self.write_inventory(inventory)
                result = self.run_helper("list")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("ERROR:", result.stderr)


if __name__ == "__main__":
    unittest.main()
