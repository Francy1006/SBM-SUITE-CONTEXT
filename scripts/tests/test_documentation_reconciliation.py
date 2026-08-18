from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


CONTEXT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CONTEXT_ROOT / "scripts"))

from documentation_reconciliation import (  # noqa: E402
    DocumentationReconciliationError,
    build_reconciliation,
)


def _operational_rows(rows: list[tuple[str, str, str]]) -> str:
    rendered = "\n".join(
        f"| {objective_id} | {project} | Objective | {status} | N/A |"
        for objective_id, project, status in rows
    )
    return rendered


def _project_context(
    active: list[tuple[str, str, str]] | None = None,
    pending: list[tuple[str, str, str]] | None = None,
) -> str:
    return f"""# Project context

## 3. Active objectives

| ID | Project | Objective | Status | Documentation |
|---|---|---|---|---|
{_operational_rows(active or [])}

## 4. Pending objectives

| ID | Project | Objective | Status | Documentation |
|---|---|---|---|---|
{_operational_rows(pending or [])}

## 5. Boundary
"""


def _completed_context(rows: list[tuple[str, str, str]] | None = None) -> str:
    rendered = "\n".join(
        f"| {objective_id} | {project} | Objective | {status} | N/A |"
        for objective_id, project, status in (rows or [])
    )
    return f"""# Completed objectives

## 1. Completed objectives by project

### Test projects

| Objective ID | Project | Objective | Final status | Documentation |
|---|---|---|---|---|
{rendered}

## 2. Boundary
"""


def _documentation_table(rows: list[tuple[str, str, str]], narrative: str = "") -> str:
    rendered = "\n".join(
        f"| {objective_id} | {project} | {status} |"
        for objective_id, project, status in rows
    )
    return f"""# Roadmap

## 12. Roadmap

{narrative}

| Objective ID | Project | Status |
|---|---|---|
{rendered}
"""


class DocumentationReconciliationTests(unittest.TestCase):
    def _build(
        self,
        project_context: str,
        completed_context: str,
        pages: dict[str, str],
    ) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project_path = root / "PROJECT_CONTEXT.md"
            completed_path = root / "COMPLETED_OBJECTIVES.md"
            documentation_root = root / "documentation"
            pages_root = documentation_root / "pages"
            pages_root.mkdir(parents=True)
            project_path.write_text(project_context, encoding="utf-8")
            completed_path.write_text(completed_context, encoding="utf-8")
            for relative_path, content in pages.items():
                target = pages_root / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            return build_reconciliation(
                project_path,
                completed_path,
                documentation_root,
            )

    def test_completed_record_ignores_narrative_active_word(self) -> None:
        result = self._build(
            _project_context(),
            _completed_context([("DP-TEST-001", "DP-API", "completed")]),
            {
                "roadmap.md": _documentation_table(
                    [("DP-TEST-001", "DP-API", "completed")],
                    "DP-TEST-001 was removed from the active-objective section.",
                )
            },
        )
        self.assertTrue(result["synchronized"])
        self.assertEqual(result["differences"], [])

    def test_registered_and_deleted_terminal_states_are_reconciled(self) -> None:
        for status in ("registered", "deleted"):
            with self.subTest(status=status):
                result = self._build(
                    _project_context(),
                    _completed_context([("OBJ-T", "PROJECT-A", status)]),
                    {
                        "roadmap.md": _documentation_table(
                            [("OBJ-T", "PROJECT-A", status)]
                        )
                    },
                )
                self.assertTrue(result["synchronized"])
                self.assertEqual(result["differences"], [])

    def test_real_active_to_pending_difference_is_detected(self) -> None:
        result = self._build(
            _project_context(active=[("OBJ-A", "PROJECT-A", "active")]),
            _completed_context(),
            {"roadmap.md": _documentation_table([("OBJ-A", "PROJECT-A", "pending")])},
        )
        self.assertFalse(result["synchronized"])
        self.assertEqual(result["differences"][0]["documentation_states"], ["pending"])
        self.assertEqual(result["differences"][0]["difference"], "status-mismatch")

    def test_historical_narrative_does_not_create_canonical_states(self) -> None:
        result = self._build(
            _project_context(active=[("OBJ-A", "PROJECT-A", "active")]),
            _completed_context(),
            {
                "roadmap.md": _documentation_table(
                    [("OBJ-A", "PROJECT-A", "active")],
                    "OBJ-A was previously active and removed from active section.",
                )
            },
        )
        self.assertTrue(result["synchronized"])

    def test_fenced_example_table_does_not_create_a_second_state(self) -> None:
        page = _documentation_table([("OBJ-A", "PROJECT-A", "active")])
        page += """

```text
| Objective ID | Project | Status |
|---|---|---|
| OBJ-A | PROJECT-A | completed |
```
"""
        result = self._build(
            _project_context(active=[("OBJ-A", "PROJECT-A", "active")]),
            _completed_context(),
            {"roadmap.md": page},
        )
        self.assertTrue(result["synchronized"])

    def test_conflicting_canonical_records_raise_explicit_error(self) -> None:
        with self.assertRaisesRegex(
            DocumentationReconciliationError,
            "Duplicate canonical objective records with conflicting status: OBJ-A",
        ):
            self._build(
                _project_context(active=[("OBJ-A", "PROJECT-A", "active")]),
                _completed_context(),
                {
                    "active.md": _documentation_table(
                        [("OBJ-A", "PROJECT-A", "active")]
                    ),
                    "completed.md": _documentation_table(
                        [("OBJ-A", "PROJECT-A", "completed")]
                    ),
                },
            )

    def test_global_reconciliation_detects_multiple_projects(self) -> None:
        result = self._build(
            _project_context(
                active=[
                    ("OBJ-A", "PROJECT-A", "active"),
                    ("OBJ-B", "PROJECT-B", "active"),
                ]
            ),
            _completed_context(),
            {
                "roadmap.md": _documentation_table(
                    [
                        ("OBJ-A", "PROJECT-A", "pending"),
                        ("OBJ-B", "PROJECT-B", "pending"),
                    ]
                )
            },
        )
        self.assertFalse(result["synchronized"])
        self.assertEqual(
            {difference["project"] for difference in result["differences"]},
            {"PROJECT-A", "PROJECT-B"},
        )

    def test_fully_synchronized_has_no_targets(self) -> None:
        result = self._build(
            _project_context(active=[("OBJ-A", "PROJECT-A", "active")]),
            _completed_context(),
            {"roadmap.md": _documentation_table([("OBJ-A", "PROJECT-A", "active")])},
        )
        self.assertEqual(result["summary"], "Documentation already synchronized")
        self.assertEqual(result["documentation_targets"], [])
        self.assertEqual(result["differences"], [])

    def test_synchronized_active_objective_remains_active(self) -> None:
        result = self._build(
            _project_context(active=[("OBJ-CURRENT", "SBM-SUITE", "active")]),
            _completed_context(),
            {
                "roadmap.md": _documentation_table(
                    [("OBJ-CURRENT", "SBM-SUITE", "active")]
                )
            },
        )
        self.assertTrue(result["synchronized"])
        self.assertEqual(result["differences"], [])


if __name__ == "__main__":
    unittest.main()
