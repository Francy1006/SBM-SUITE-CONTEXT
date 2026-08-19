from __future__ import annotations

import re
import sys
import tempfile
import base64
import gzip
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTEXT_ROOT / "scripts"))

from objective_payload import COMPACT_MARKER, ObjectivePayloadError, decode_payload_bytes

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


def _global_operational(
    *,
    active: list[tuple[str, str, str, int, str, str, str]] | None = None,
    pending: list[tuple[str, str, str, int, str, str, str]] | None = None,
) -> str:
    active = active or []
    pending = pending or []

    def section(heading, rows, status):
        lines = [
            heading,
            "",
            "| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |",
            "|---|---|---|---|---:|---|---|---|",
        ]
        lines.extend(
            f"| {oid} | {project} | {objective} | {status} | {priority} | {target} | {branch} | {documentation} |"
            for oid, project, objective, priority, target, branch, documentation in rows
        )
        return "\n".join(lines)

    return section("## 3. Active objectives", active, "active") + "\n\n" + section(
        "## 4. Pending objectives", pending, "pending"
    ) + "\n"


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
            "objective-registration",
            "objective-completion",
            "objective-deletion",
            "objective-update",
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
        project_completion, _ = lifecycle_patch_policy(
            "objective-completion", "example-project"
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
        self.assertEqual(
            project_completion,
            {
                "patches/completed-objectives.json",
                "patches/global-project-context.json",
                "patches/project-context.json",
            },
        )

    def test_context_deploy_accepts_suite_display_alias_in_multiproject_batches(self) -> None:
        deploy = (CONTEXT_ROOT / "scripts" / "context-deploy.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn('{"sbm-suite", "sbm-suite/context"}', deploy)
        self.assertIn("un batch multiproyecto debe ejecutarse desde sbm-suite-context", deploy)

    def test_context_deploy_supports_compact_stdin_objective_transport(self) -> None:
        deploy = (CONTEXT_ROOT / "scripts" / "context-deploy.sh").read_text(
            encoding="utf-8"
        )
        init_context = (CONTEXT_ROOT / "INIT_CONTEXT.md").read_text(encoding="utf-8")
        readme = (CONTEXT_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn('OBJECTIVES_SOURCE="$3"', deploy)
        self.assertIn('cat > "${OBJECTIVES_RAW_FILE}"', deploy)
        self.assertIn('OBJECTIVE_PAYLOAD_HELPER=', deploy)
        self.assertIn('decode \\', deploy)
        self.assertIn('--objectives-file "${NORMALIZED_OBJECTIVES_FILE}"', deploy)
        self.assertIn('--data-binary "@${PAYLOAD_FILE}"', deploy)
        self.assertIn("<<'OBJECTIVES_PAYLOAD'", init_context)
        self.assertIn("SBM-GZIP-BASE64-V1", init_context)
        self.assertIn("SBM-GZIP-BASE64-V1", readme)
        self.assertNotIn("@input/objectives-batch.json", deploy)
        self.assertNotIn("input/objectives-batch.json", init_context)
        self.assertNotIn("input/objectives-batch.json", readme)

    def test_compact_objective_payload_round_trip_and_corruption_detection(self) -> None:
        raw = (
            '[{"objective_id":"OBJ-CTX-046","objective":"anti-spoofing/replay",'
            '"status":"pending","priority":5,"target_date":"N/A",'
            '"branch":"FEATURE-adds-suite-objectives"}]'
        ).encode("utf-8")
        encoded = base64.b64encode(gzip.compress(raw, compresslevel=9, mtime=0))
        envelope = COMPACT_MARKER + encoded + b"\n"

        self.assertEqual(decode_payload_bytes(envelope), raw)
        self.assertEqual(decode_payload_bytes(raw), raw)

        corrupted = envelope[:-8] + b"AAAAAAAA"
        with self.assertRaises(ObjectivePayloadError):
            decode_payload_bytes(corrupted)

    def test_objective_lifecycle_cli_accepts_objectives_file(self) -> None:
        lifecycle = (CONTEXT_ROOT / "scripts" / "objective_lifecycle.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('objective_source.add_argument("--objectives-file")', lifecycle)
        self.assertIn('source.read_text(encoding="utf-8")', lifecycle)

    def test_suite_format_contract_matches_current_suite_context(self) -> None:
        suite = (CONTEXT_ROOT / "SUITE_CONTEXT.md").read_text(encoding="utf-8")
        format_contract = (CONTEXT_ROOT / "FORMAT_CONTEXT.md").read_text(encoding="utf-8")
        suite_contract = format_contract.split(
            "## 4. Global `SUITE_CONTEXT.md`", maxsplit=1
        )[1].split("\n---\n", maxsplit=1)[0]

        actual_headings = re.findall(r"^## \d+\. .+$", suite, flags=re.MULTILINE)
        contract_headings = re.findall(
            r"^## \d+\. .+$", suite_contract, flags=re.MULTILINE
        )
        self.assertEqual(contract_headings, actual_headings)
        self.assertIn(
            "| Brand | Project | Application or service | Type | Description | Runtime state |",
            suite_contract,
        )

    def test_planning_patch_policy_supports_direct_completed_and_mixed_batches(self) -> None:
        pending_required, pending_forbidden = lifecycle_patch_policy(
            "planning-activation",
            "sbm-suite-context",
            [{"status": "pending"}],
        )
        completed_required, completed_forbidden = lifecycle_patch_policy(
            "planning-activation",
            "sbm-suite-context",
            [{"status": "completed"}],
        )
        mixed_required, mixed_forbidden = lifecycle_patch_policy(
            "planning-activation",
            "example-project",
            [{"status": "active"}, {"status": "completed"}],
        )
        update_required, update_forbidden = lifecycle_patch_policy(
            "objective-update",
            "example-project",
            [{"status": "active"}],
        )

        self.assertEqual(
            pending_required, {"patches/global-project-context.json"}
        )
        self.assertIn("patches/completed-objectives.json", pending_forbidden)
        self.assertEqual(
            completed_required, {"patches/completed-objectives.json"}
        )
        self.assertNotIn("patches/completed-objectives.json", completed_forbidden)
        self.assertEqual(
            mixed_required,
            {
                "patches/global-project-context.json",
                "patches/project-context.json",
                "patches/completed-objectives.json",
            },
        )
        self.assertNotIn("patches/completed-objectives.json", mixed_forbidden)
        self.assertEqual(
            update_required,
            {
                "patches/global-project-context.json",
                "patches/project-context.json",
            },
        )
        self.assertIn("patches/completed-objectives.json", update_forbidden)

    def test_batch_terminal_and_update_routes_validate_all_objectives(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    active=[("OBJ-A", "Active", 5, "N/A", "FEATURE-shared-work")],
                    pending=[("OBJ-P", "Pending", 4, "N/A", "FEATURE-shared-work")],
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")

            validate_existing_objective(
                [
                    {"objective_id": "OBJ-A", "status": "completed"},
                    {"objective_id": "OBJ-P", "status": "completed"},
                ],
                "objective-completion",
                [operational],
                completed,
            )
            validate_existing_objective(
                [
                    {"objective_id": "OBJ-A", "status": "pending"},
                    {"objective_id": "OBJ-P", "status": "active"},
                ],
                "objective-update",
                [operational],
                completed,
            )

            with self.assertRaisesRegex(ObjectiveLifecycleError, "OBJ-MISSING"):
                validate_existing_objective(
                    [
                        {"objective_id": "OBJ-A", "status": "registered"},
                        {"objective_id": "OBJ-MISSING", "status": "registered"},
                    ],
                    "objective-registration",
                    [operational],
                    completed,
                )
            with self.assertRaisesRegex(ObjectiveLifecycleError, "pending or active"):
                validate_existing_objective(
                    [{"objective_id": "OBJ-A", "status": "cancelled"}],
                    "objective-update",
                    [operational],
                    completed,
                )

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

    def test_creation_accepts_pending_active_and_completed_in_one_batch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(_operational(), encoding="utf-8")
            completed.write_text(_completed(), encoding="utf-8")
            validate_planning_creation(
                [
                    {"objective_id": "OBJ-P", "status": "pending", "project": "DP-API"},
                    {"objective_id": "OBJ-A", "status": "active", "project": "SBM-API"},
                    {"objective_id": "OBJ-C", "status": "completed", "project": "SBM-DB"},
                ],
                [operational],
                completed,
            )

    def test_multi_project_activation_validates_each_local_context_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            global_context = root / "PROJECT_CONTEXT.md"
            dp_context = root / "DP-API/context/PROJECT_CONTEXT.md"
            api_context = root / "SBM-API/context/PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            for path in (dp_context, api_context):
                path.parent.mkdir(parents=True)
            global_context.write_text(
                _global_operational(
                    pending=[
                        ("OBJ-DP", "DP-API", "DP work", 5, "N/A", "FEATURE-shared-work", "docs/dp.md"),
                        ("OBJ-API", "SBM-API", "API work", 4, "N/A", "FEATURE-shared-work", "docs/api.md"),
                    ]
                ), encoding="utf-8"
            )
            dp_context.write_text(_operational(pending=[("OBJ-DP", "DP work", 5, "N/A", "FEATURE-shared-work")]).replace("FEATURE-shared-work | N/A |", "FEATURE-shared-work | docs/dp.md |"), encoding="utf-8")
            api_context.write_text(_operational(pending=[("OBJ-API", "API work", 4, "N/A", "FEATURE-shared-work")]).replace("FEATURE-shared-work | N/A |", "FEATURE-shared-work | docs/api.md |"), encoding="utf-8")
            completed.write_text(_completed(), encoding="utf-8")
            validate_activation(
                [
                    {"objective_id": "OBJ-DP", "project": "DP-API", "objective": "DP work", "status": "active", "priority": 5, "target_date": "N/A", "branch": "FEATURE-shared-work", "documentation": "docs/dp.md"},
                    {"objective_id": "OBJ-API", "project": "SBM-API", "objective": "API work", "status": "active", "priority": 4, "target_date": "N/A", "branch": "FEATURE-shared-work", "documentation": "docs/api.md"},
                ],
                [global_context, dp_context, api_context],
                completed,
            )

    def test_activation_preserves_pending_lifecycle_fields_with_same_branch(self) -> None:
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

    def test_activation_can_explicitly_change_to_valid_git_flow_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    pending=[
                        (
                            "OBJ-CTX-038",
                            "Standardize suite governance",
                            5,
                            "N/A",
                            "FEATURE-enables-git-flow",
                        )
                    ]
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")

            validate_activation(
                [
                    {
                        "objective_id": "OBJ-CTX-038",
                        "objective": "Standardize suite governance",
                        "status": "active",
                        "priority": 5,
                        "target_date": "N/A",
                        "branch": "FEATURE-standardizes-suite-governance",
                    }
                ],
                [operational],
                completed,
            )

    def test_activation_rejects_invalid_branch(self) -> None:
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

            with self.assertRaisesRegex(ObjectiveLifecycleError, "Git Flow"):
                validate_activation(
                    [
                        {
                            "objective_id": "OBJ-P",
                            "objective": "Pending objective",
                            "status": "active",
                            "priority": 5,
                            "target_date": "N/A",
                            "branch": "feature-invalid-branch",
                        }
                    ],
                    [operational],
                    completed,
                )

    def test_activation_migration_must_preserve_other_lifecycle_fields(self) -> None:
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
                            "2026-09-01",
                            "FEATURE-original-branch",
                        )
                    ]
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")
            base_payload = {
                "objective_id": "OBJ-P",
                "objective": "Pending objective",
                "status": "active",
                "priority": 5,
                "target_date": "2026-09-01",
                "branch": "FEATURE-standardizes-suite-governance",
            }

            changed_values = {
                "objective": ("Changed objective", "Objective"),
                "priority": (4, "Priority"),
                "target_date": ("2026-09-02", "Target date"),
            }
            for field, (changed_value, column) in changed_values.items():
                with self.subTest(field=field):
                    payload = {**base_payload, field: changed_value}
                    with self.assertRaisesRegex(
                        ObjectiveLifecycleError, f"preserve {column} literally"
                    ):
                        validate_activation([payload], [operational], completed)

    def test_distinct_objectives_can_share_transversal_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            objective_ids = ("OBJ-CTX-038", "OBJ-CTX-012", "OBJ-CTX-002")
            operational.write_text(
                _operational(
                    pending=[
                        (
                            objective_id,
                            f"Objective {objective_id}",
                            5,
                            "N/A",
                            f"FEATURE-original-{index}",
                        )
                        for index, objective_id in enumerate(objective_ids, start=1)
                    ]
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")

            for objective_id in objective_ids:
                with self.subTest(objective_id=objective_id):
                    validate_activation(
                        [
                            {
                                "objective_id": objective_id,
                                "objective": f"Objective {objective_id}",
                                "status": "active",
                                "priority": 5,
                                "target_date": "N/A",
                                "branch": "FEATURE-standardizes-suite-governance",
                            }
                        ],
                        [operational],
                        completed,
                    )

    def test_activation_batch_moves_obj_ctx_012_and_002_to_shared_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            pending = [
                (
                    "OBJ-CTX-012",
                    "Create the SBM Agent bootstrap",
                    5,
                    "N/A",
                    "FEATURE-adds-sbm-agent-bootstrap",
                ),
                (
                    "OBJ-CTX-002",
                    "Enable transversal Context tooling",
                    5,
                    "N/A",
                    "FEATURE-automates-cross-project-flows",
                ),
            ]
            operational.write_text(_operational(pending=pending), encoding="utf-8")
            completed.write_text(_completed(), encoding="utf-8")

            validate_activation(
                [
                    {
                        "objective_id": objective_id,
                        "objective": objective,
                        "status": "active",
                        "priority": priority,
                        "target_date": target_date,
                        "branch": "FEATURE-standardizes-suite-governance",
                    }
                    for objective_id, objective, priority, target_date, _ in pending
                ],
                [operational],
                completed,
            )

    def test_activation_batch_rejects_duplicates_and_is_atomic_on_missing_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            operational = root / "PROJECT_CONTEXT.md"
            completed = root / "COMPLETED_OBJECTIVES.md"
            operational.write_text(
                _operational(
                    pending=[
                        (
                            "OBJ-CTX-012",
                            "Create the SBM Agent bootstrap",
                            5,
                            "N/A",
                            "FEATURE-adds-sbm-agent-bootstrap",
                        )
                    ]
                ),
                encoding="utf-8",
            )
            completed.write_text(_completed(), encoding="utf-8")
            before = operational.read_bytes()
            objective = {
                "objective_id": "OBJ-CTX-012",
                "objective": "Create the SBM Agent bootstrap",
                "status": "active",
                "priority": 5,
                "target_date": "N/A",
                "branch": "FEATURE-standardizes-suite-governance",
            }

            with self.assertRaisesRegex(ObjectiveLifecycleError, "duplicate"):
                validate_activation([objective, objective], [operational], completed)

            missing = {
                **objective,
                "objective_id": "OBJ-CTX-002",
                "objective": "Enable transversal Context tooling",
            }
            with self.assertRaisesRegex(ObjectiveLifecycleError, "OBJ-CTX-002"):
                validate_activation([objective, missing], [operational], completed)

            self.assertEqual(operational.read_bytes(), before)

    def test_activation_generator_contract_covers_obj_ctx_038_branch_migration(self) -> None:
        prompt = (CONTEXT_ROOT / "SYS_PROMPT.md").read_text(encoding="utf-8")
        format_contract = (CONTEXT_ROOT / "FORMAT_CONTEXT.md").read_text(
            encoding="utf-8"
        )
        activation = prompt.split("### objective-activation", maxsplit=1)[1].split(
            "### implementation-progress", maxsplit=1
        )[0]

        self.assertIn(
            "`branch` is the explicit desired branch and may differ from the "
            "pending row's current `Branch`",
            activation,
        )
        self.assertIn(
            "insert all activated rows as one contiguous block immediately after the "
            "last existing Active objectives data row and before the first blank line, "
            "`Rules:` block or other non-table content",
            activation,
        )
        self.assertIn(
            "remove only the selected pending rows without leaving a blank line "
            "inside the Pending objectives table",
            activation,
        )
        self.assertIn(
            "copy all unrelated table rows byte-for-byte and in their original order",
            activation,
        )
        self.assertIn(
            "update only the selected project's row in `## 6. Project objective "
            "summaries`",
            activation,
        )
        self.assertNotIn(
            "preserve `objective_id`, `objective`, `priority`, `target_date` and "
            "`branch` exactly from the pending row",
            activation,
        )
        self.assertIn(
            "The explicit validated manifest `branch` is the desired branch and may "
            "differ from the current pending branch",
            format_contract,
        )
        self.assertIn(
            "insert every selected active row as one contiguous block immediately "
            "after the last active data row and before the first blank line, `Rules:` "
            "block or other non-table content",
            format_contract,
        )
        self.assertNotIn(
            "preserve `objective_id`, `objective`, `priority`, `target_date` and "
            "`branch` literally from the existing pending row",
            format_contract,
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
