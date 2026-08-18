from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = CONTEXT_ROOT / "scripts/suite-artifacts.py"
SPEC = importlib.util.spec_from_file_location("suite_artifacts", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
suite_artifacts = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = suite_artifacts
SPEC.loader.exec_module(suite_artifacts)


class SuiteArtifactsTests(unittest.TestCase):
    def test_plan_creates_only_declared_managed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            repository_root = root / "SBM/PROJECT"
            (context / "shared").mkdir(parents=True)
            repository_root.mkdir(parents=True)
            source = context / "shared/common.md"
            source.write_text(
                "<!-- managed-by: SBM-SUITE/context/scripts/suite-artifacts.py -->\ncommon\n",
                encoding="utf-8",
            )
            repository = suite_artifacts.Repository(
                "PROJECT", "SBM/PROJECT", repository_root
            )
            plan, skipped, errors = suite_artifacts.build_plan(
                context,
                [repository],
                [{"source": "shared/common.md", "target": "context/common.md"}],
            )
            self.assertEqual(errors, [])
            self.assertEqual(skipped, [])
            self.assertEqual(plan[0].state, "created")
            suite_artifacts.apply_plan(plan)
            self.assertEqual(
                (repository_root / "context/common.md").read_text(encoding="utf-8"),
                source.read_text(encoding="utf-8"),
            )

    def test_unmanaged_project_content_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = root / "context"
            repository_root = root / "SBM/PROJECT"
            (context / "shared").mkdir(parents=True)
            (repository_root / "context").mkdir(parents=True)
            (context / "shared/common.md").write_text("managed\n", encoding="utf-8")
            (repository_root / "context/common.md").write_text(
                "project-specific\n", encoding="utf-8"
            )
            repository = suite_artifacts.Repository(
                "PROJECT", "SBM/PROJECT", repository_root
            )
            _, _, errors = suite_artifacts.build_plan(
                context,
                [repository],
                [{"source": "shared/common.md", "target": "context/common.md"}],
            )
            self.assertIn("contenido no administrado", errors[0])


if __name__ == "__main__":
    unittest.main()
