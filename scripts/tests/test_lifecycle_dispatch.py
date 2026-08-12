from __future__ import annotations

import sys
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTEXT_ROOT / "scripts"))

from objective_lifecycle import (  # noqa: E402
    LIFECYCLE_ROUTES,
    ObjectiveLifecycleError,
    lifecycle_patch_policy,
    lifecycle_route,
    validate_existing_objective,
)


class LifecycleDispatchTests(unittest.TestCase):
    def test_all_routes_are_exact_and_distinct(self) -> None:
        phases = (
            "planning-activation",
            "objective-activation",
            "implementation-progress",
            "implementation-closure",
        )
        self.assertEqual(set(phases), set(LIFECYCLE_ROUTES))
        self.assertEqual([lifecycle_route(phase) for phase in phases], list(phases))
        self.assertEqual(len(set(LIFECYCLE_ROUTES.values())), len(phases))

    def test_substrings_and_near_matches_are_rejected(self) -> None:
        for phase in (
            "progress",
            "closure",
            "implementation-progress-extra",
            "prefix-implementation-closure",
            "implementation",
        ):
            with self.subTest(phase=phase):
                with self.assertRaises(ObjectiveLifecycleError):
                    lifecycle_route(phase)

    def test_obj_ctx_013_active_routes_as_progress_without_mutation(self) -> None:
        project_context = CONTEXT_ROOT / "PROJECT_CONTEXT.md"
        before = project_context.read_bytes()

        validate_existing_objective(
            [{"objective_id": "OBJ-CTX-013"}],
            "implementation-progress",
            [project_context],
            CONTEXT_ROOT / "COMPLETED_OBJECTIVES.md",
        )

        self.assertEqual(project_context.read_bytes(), before)

    def test_obj_ctx_013_active_remains_valid_for_explicit_closure(self) -> None:
        validate_existing_objective(
            [{"objective_id": "OBJ-CTX-013"}],
            "implementation-closure",
            [CONTEXT_ROOT / "PROJECT_CONTEXT.md"],
            CONTEXT_ROOT / "COMPLETED_OBJECTIVES.md",
        )

    def test_progress_and_closure_routes_cannot_alias(self) -> None:
        progress = lifecycle_route("implementation-progress")
        closure = lifecycle_route("implementation-closure")
        self.assertNotEqual(progress, closure)
        self.assertEqual(progress, "implementation-progress")
        self.assertEqual(closure, "implementation-closure")

    def test_completed_patch_is_forbidden_for_progress_and_required_for_closure(
        self,
    ) -> None:
        progress_required, progress_forbidden = lifecycle_patch_policy(
            "implementation-progress", "sbm-suite-context"
        )
        closure_required, closure_forbidden = lifecycle_patch_policy(
            "implementation-closure", "sbm-suite-context"
        )

        completed_patch = "patches/completed-objectives.json"
        self.assertNotIn(completed_patch, progress_required)
        self.assertIn(completed_patch, progress_forbidden)
        self.assertIn(completed_patch, closure_required)
        self.assertNotIn(completed_patch, closure_forbidden)

    def test_conversation_contract_keeps_closure_ui_out_of_progress(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        progress = contract.split(
            "16. For `implementation-progress`", maxsplit=1
        )[1].split("17. Exclusively for `implementation-closure`", maxsplit=1)[0]
        closure = contract.split(
            "17. Exclusively for `implementation-closure`", maxsplit=1
        )[1].split("18. The branch", maxsplit=1)[0]

        for closure_only_text in (
            "PREVISUALIZACIÓN DE CIERRE",
            "active → completed",
            "¿Confirma el cierre?",
        ):
            self.assertNotIn(closure_only_text, progress)
            self.assertIn(closure_only_text, closure)


if __name__ == "__main__":
    unittest.main()
