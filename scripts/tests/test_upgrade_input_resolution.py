from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
RESOLVER = CONTEXT_ROOT / "scripts" / "resolve-upgrade-input.py"


def _load_resolver():
    spec = importlib.util.spec_from_file_location("resolve_upgrade_input", RESOLVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load resolve-upgrade-input.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resolver = _load_resolver()


class UpgradeInputResolutionTests(unittest.TestCase):
    def test_canonical_context_name_is_accepted_without_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            source = input_dir / "context-upgrade.zip"
            source.write_bytes(b"zip")

            original, canonical = resolver.resolve_upgrade_input(
                input_dir, "context-upgrade", "context-upgrade.zip"
            )

            self.assertEqual(original, source)
            self.assertEqual(canonical, source)
            self.assertTrue(source.exists())

    def test_context_download_suffix_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            source = input_dir / "context-upgrade(32).zip"
            source.write_bytes(b"zip")

            original, canonical = resolver.resolve_upgrade_input(
                input_dir, "context-upgrade", "context-upgrade.zip"
            )

            self.assertEqual(original.name, "context-upgrade(32).zip")
            self.assertEqual(canonical.name, "context-upgrade.zip")
            self.assertFalse(source.exists())
            self.assertEqual(canonical.read_bytes(), b"zip")

    def test_documentation_suffix_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            source = input_dir / "documentation-upgrade-final.zip"
            source.write_bytes(b"zip")

            _, canonical = resolver.resolve_upgrade_input(
                input_dir,
                "documentation-upgrade",
                "documentation-upgrade.zip",
            )

            self.assertEqual(canonical.name, "documentation-upgrade.zip")
            self.assertTrue(canonical.exists())

    def test_wrong_prefix_is_rejected_without_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            source = input_dir / "upgrade.zip"
            source.write_bytes(b"zip")

            with self.assertRaisesRegex(ValueError, "debe comenzar con context-upgrade"):
                resolver.resolve_upgrade_input(
                    input_dir, "context-upgrade", "context-upgrade.zip"
                )

            self.assertTrue(source.exists())

    def test_multiple_zip_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            (input_dir / "context-upgrade.zip").write_bytes(b"one")
            (input_dir / "context-upgrade(1).zip").write_bytes(b"two")

            with self.assertRaisesRegex(ValueError, "exactamente un ZIP"):
                resolver.resolve_upgrade_input(
                    input_dir, "context-upgrade", "context-upgrade.zip"
                )

    def test_upgrade_scripts_use_shared_resolver(self) -> None:
        context_script = (CONTEXT_ROOT / "scripts/context-upgrade.sh").read_text(
            encoding="utf-8"
        )
        documentation_script = (
            CONTEXT_ROOT / "scripts/documentation-upgrade.sh"
        ).read_text(encoding="utf-8")

        self.assertIn('resolve-upgrade-input.py', context_script)
        self.assertIn('"context-upgrade"', context_script)
        self.assertIn('resolve-upgrade-input.py', documentation_script)
        self.assertIn('"documentation-upgrade"', documentation_script)
        self.assertNotIn('UPGRADE_ZIP="${INPUT_DIR}/context-upgrade.zip"', context_script)
        self.assertNotIn(
            'UPGRADE_ZIP="${INPUT_DIR}/documentation-upgrade.zip"',
            documentation_script,
        )

    def test_cli_rejects_non_matching_single_zip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory)
            (input_dir / "other.zip").write_bytes(b"zip")
            result = subprocess.run(
                [
                    "python3",
                    str(RESOLVER),
                    str(input_dir),
                    "context-upgrade",
                    "context-upgrade.zip",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("debe comenzar con context-upgrade", result.stderr)


if __name__ == "__main__":
    unittest.main()
