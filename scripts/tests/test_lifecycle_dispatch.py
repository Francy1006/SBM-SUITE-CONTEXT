from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTEXT_ROOT / "scripts"))

from objective_lifecycle import (  # noqa: E402
    LIFECYCLE_ROUTES,
    ObjectiveLifecycleError,
    lifecycle_patch_policy,
    lifecycle_route,
    validate_activation,
    validate_existing_objective,
    validate_planning_creation,
)


def _operational(
    *,
    active: list[tuple[str, str, int, str, str]] | None = None,
    pending: list[tuple[str, str, int, str, str]] | None = None,
) -> str:
    active = active or []
    pending = pending or []

    def section(heading: str, rows: list[tuple[str, str, int, str, str]], status: str) -> str:
        rendered = [
            heading,
            "",
            "| ID | Objective | Status | Priority | Target date | Branch | Documentation |",
            "|---|---|---|---:|---|---|---|",
        ]
        rendered.extend(
            f"| {objective_id} | {objective} | {status} | {priority} | {target_date} | {branch} | N/A |"
            for objective_id, objective, priority, target_date, branch in rows
        )
        return "\n".join(rendered)

    return (
        section("## 3. Active objectives", active, "active")
        + "\n\n"
        + section("## 4. Pending objectives", pending, "pending")
        + "\n"
    )


def _completed(ids: list[str] | None = None) -> str:
    ids = ids or []
    lines = [
        "# COMPLETED_OBJECTIVES.md",
        "",
        "## 1. Completed objectives by project",
        "",
        "### TEST",
        "",
        "| Objective ID | Project | Final status |",
        "|---|---|---|",
    ]
    lines.extend(f"| {objective_id} | TEST | completed |" for objective_id in ids)
    return "\n".join(lines) + "\n"


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

    def test_patch_policy_matches_each_lifecycle(self) -> None:
        suite_planning, _ = lifecycle_patch_policy(
            "planning-activation", "sbm-suite-context"
        )
        project_activation, _ = lifecycle_patch_policy(
            "objective-activation", "example-project"
        )
        suite_progress, progress_forbidden = lifecycle_patch_policy(
            "implementation-progress", "sbm-suite-context"
        )
        suite_closure, closure_forbidden = lifecycle_patch_policy(
            "implementation-closure", "sbm-suite-context"
        )
        project_closure, _ = lifecycle_patch_policy(
            "implementation-closure", "example-project"
        )

        self.assertEqual(suite_planning, {"patches/global-project-context.json"})
        self.assertEqual(
            project_activation,
            {
                "patches/global-project-context.json",
                "patches/project-context.json",
            },
        )
        self.assertEqual(suite_progress, set())
        self.assertIn("patches/completed-objectives.json", progress_forbidden)
        self.assertEqual(
            suite_closure,
            {
                "patches/completed-objectives.json",
                "patches/global-project-context.json",
                "patches/global-qa-context.json",
            },
        )
        self.assertEqual(
            project_closure,
            suite_closure
            | {
                "patches/project-context.json",
                "patches/project-qa-context.json",
            },
        )
        self.assertNotIn("patches/completed-objectives.json", closure_forbidden)

    def test_planning_rejects_current_and_historical_id_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    active=[("OBJ-A", "Active", 5, "N/A", "FEATURE-active")],
                    pending=[("OBJ-B", "Pending", 4, "N/A", "FEATURE-pending")],
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(["OBJ-C"]), encoding="utf-8")

            validate_planning_creation(
                [{"objective_id": "OBJ-D"}, {"objective_id": "OBJ-E"}],
                [operational],
                completed,
            )

            for objective_id in ("OBJ-A", "OBJ-B", "OBJ-C"):
                with self.subTest(objective_id=objective_id):
                    with self.assertRaises(ObjectiveLifecycleError):
                        validate_planning_creation(
                            [{"objective_id": objective_id}],
                            [operational],
                            completed,
                        )

    def test_activation_preserves_pending_lifecycle_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    pending=[
                        (
                            "OBJ-P",
                            "Pending objective",
                            5,
                            "N/A",
                            "FEATURE-pending-objective",
                        )
                    ]
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")
            before = operational.read_bytes()

            validate_activation(
                [
                    {
                        "objective_id": "OBJ-P",
                        "objective": "Pending objective",
                        "status": "active",
                        "priority": 5,
                        "target_date": "N/A",
                        "branch": "FEATURE-pending-objective",
                    }
                ],
                [operational],
                completed,
            )
            self.assertEqual(operational.read_bytes(), before)

            with self.assertRaises(ObjectiveLifecycleError):
                validate_activation(
                    [
                        {
                            "objective_id": "OBJ-P",
                            "objective": "Pending objective",
                            "status": "active",
                            "priority": 5,
                            "target_date": "N/A",
                            "branch": "FEATURE-wrong-branch",
                        }
                    ],
                    [operational],
                    completed,
                )

    def test_progress_accepts_active_or_pending_but_closure_requires_active(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    active=[("OBJ-A", "Active", 5, "N/A", "FEATURE-active")],
                    pending=[("OBJ-P", "Pending", 4, "N/A", "FEATURE-pending")],
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")
            before = operational.read_bytes()

            validate_existing_objective(
                [{"objective_id": "OBJ-A"}],
                "implementation-progress",
                [operational],
                completed,
            )
            validate_existing_objective(
                [{"objective_id": "OBJ-P"}],
                "implementation-progress",
                [operational],
                completed,
            )
            validate_existing_objective(
                [{"objective_id": "OBJ-A"}],
                "implementation-closure",
                [operational],
                completed,
            )
            with self.assertRaises(ObjectiveLifecycleError):
                validate_existing_objective(
                    [{"objective_id": "OBJ-P"}],
                    "implementation-closure",
                    [operational],
                    completed,
                )
            self.assertEqual(operational.read_bytes(), before)

    def test_conversation_contract_keeps_closure_ui_out_of_progress(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        progress_marker = "For `implementation-progress`, require the objective"
        closure_marker = "Exclusively for `implementation-closure`, require the objective"
        progress = contract.split(progress_marker, maxsplit=1)[1].split(
            closure_marker, maxsplit=1
        )[0]
        closure = contract.split(closure_marker, maxsplit=1)[1].split(
            "The branch must come from the selected objective record", maxsplit=1
        )[0]

        for closure_only_text in (
            "PREVISUALIZACIÓN DE CIERRE",
            "active → completed",
            "¿Confirma el cierre?",
        ):
            self.assertNotIn(closure_only_text, progress)
            self.assertIn(closure_only_text, closure)

    def test_strict_shell_options_are_scoped_in_user_visible_blocks(self) -> None:
        contract = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```bash\n(.*?)```", contract, flags=re.DOTALL)
        strict_blocks = [block for block in blocks if "set -euo pipefail" in block]
        self.assertTrue(strict_blocks)
        for block in strict_blocks:
            with self.subTest(block=block[:80]):
                lines = [line for line in block.splitlines() if line.strip()]
                set_index = lines.index("set -euo pipefail")
                self.assertIn("(", lines[: set_index + 1])
                self.assertEqual(lines[-1], ")")


if __name__ == "__main__":
    unittest.main()
