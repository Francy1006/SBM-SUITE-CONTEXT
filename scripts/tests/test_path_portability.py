from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
HELPER = CONTEXT_ROOT / "scripts" / "path-portability.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("path_portability", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load path-portability.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


path_portability = _load_helper()


class PathPortabilityTests(unittest.TestCase):
    def test_windows_git_and_msys_paths_are_equivalent(self) -> None:
        variants = (
            "F:/DEV/SBM-SUITE/context",
            "F:\\DEV\\SBM-SUITE\\context",
            "/f/DEV/SBM-SUITE/context",
        )
        canonical = {path_portability.canonical_path(value) for value in variants}
        self.assertEqual(len(canonical), 1)

    def test_windows_comparison_is_case_insensitive(self) -> None:
        self.assertEqual(
            path_portability.canonical_path("F:/DEV/SBM-SUITE/context"),
            path_portability.canonical_path("/f/dev/sbm-suite/CONTEXT"),
        )

    def test_posix_path_remains_posix_and_case_sensitive(self) -> None:
        value = "/Users/example/SBM-SUITE/context"
        self.assertEqual(path_portability.canonical_path(value), "posix:" + value)
        self.assertNotEqual(
            path_portability.canonical_path(value),
            path_portability.canonical_path(value.lower()),
        )


if __name__ == "__main__":
    unittest.main()
