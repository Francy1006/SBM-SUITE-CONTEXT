from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = CONTEXT_ROOT / "scripts" / "cleanup-exchange.sh"


def _run(mode: str, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (str(SCRIPT), mode, str(root)),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class ExchangeCleanupTests(unittest.TestCase):
    def _prepare(self, root: Path, mode: str, *, response: bool = True) -> tuple[Path, Path, str]:
        if mode == "context":
            input_dir = root / "input"
            output_dir = root / "output"
            response_name = "context-upgrade-response.json"
        else:
            input_dir = root / "documentation" / "input"
            output_dir = root / "documentation" / "output"
            response_name = "documentation-upgrade-response.json"

        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)
        (input_dir / ".gitkeep").write_text("", encoding="utf-8")
        (input_dir / "upgrade.zip").write_text("zip", encoding="utf-8")
        (output_dir / ".gitkeep").write_text("", encoding="utf-8")
        (output_dir / "old-package.zip").write_text("old", encoding="utf-8")
        nested = output_dir / "old-dir"
        nested.mkdir()
        (nested / "artifact.txt").write_text("old", encoding="utf-8")
        if response:
            (output_dir / response_name).write_text("{}\n", encoding="utf-8")
        return input_dir, output_dir, response_name

    def test_context_success_leaves_only_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_dir, output_dir, response_name = self._prepare(root, "context")

            result = _run("context", root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(input_dir.iterdir()), [])
            self.assertEqual([path.name for path in output_dir.iterdir()], [response_name])

    def test_documentation_success_leaves_only_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_dir, output_dir, response_name = self._prepare(root, "documentation")

            result = _run("documentation", root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(input_dir.iterdir()), [])
            self.assertEqual([path.name for path in output_dir.iterdir()], [response_name])

    def test_missing_response_preserves_failure_evidence(self) -> None:
        for mode in ("context", "documentation"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                input_dir, output_dir, _ = self._prepare(root, mode, response=False)
                before_input = sorted(path.name for path in input_dir.iterdir())
                before_output = sorted(path.name for path in output_dir.iterdir())

                result = _run(mode, root)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(sorted(path.name for path in input_dir.iterdir()), before_input)
                self.assertEqual(sorted(path.name for path in output_dir.iterdir()), before_output)

    def test_upgrade_scripts_invoke_cleanup_only_on_success_path(self) -> None:
        context_script = (CONTEXT_ROOT / "scripts" / "context-upgrade.sh").read_text(encoding="utf-8")
        documentation_script = (CONTEXT_ROOT / "scripts" / "documentation-upgrade.sh").read_text(encoding="utf-8")

        context_call = '"${SCRIPT_DIR}/cleanup-exchange.sh" context "${CONTEXT_ROOT}"'
        documentation_call = '"${SCRIPT_DIR}/cleanup-exchange.sh" documentation "${CONTEXT_ROOT}"'
        self.assertIn(context_call, context_script)
        self.assertIn(documentation_call, documentation_script)
        self.assertGreater(context_script.index(context_call), context_script.index('response.workflow no coincide'))
        self.assertGreater(documentation_script.index(documentation_call), documentation_script.index('La respuesta no corresponde a documentation-upgrade'))


if __name__ == "__main__":
    unittest.main()
