#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any


ACTIVE_HEADING = "## 3. Active objectives"
PENDING_HEADING = "## 4. Pending objectives"
REQUIRED_ACTIVATION_FIELDS = {
    "objective_id",
    "objective",
    "status",
    "priority",
    "target_date",
    "branch",
}
LIFECYCLE_ROUTES = {
    "planning-activation": "planning-activation",
    "objective-activation": "objective-activation",
    "implementation-progress": "implementation-progress",
    "implementation-closure": "implementation-closure",
}


class ObjectiveLifecycleError(ValueError):
    pass


def lifecycle_route(lifecycle_phase: str) -> str:
    """Return the exact lifecycle route; never infer one phase from another."""
    try:
        return LIFECYCLE_ROUTES[lifecycle_phase]
    except KeyError as exc:
        raise ObjectiveLifecycleError(
            f"unsupported lifecycle phase: {lifecycle_phase}"
        ) from exc


def lifecycle_patch_policy(
    lifecycle_phase: str, project_name: str
) -> tuple[set[str], set[str]]:
    route = lifecycle_route(lifecycle_phase)
    required = {"patches/global-project-context.json"}
    if project_name != "sbm-suite-context":
        required.add("patches/project-context.json")
    forbidden: set[str] = set()
    if route == "implementation-closure":
        required |= {
            "patches/completed-objectives.json",
            "patches/global-qa-context.json",
        }
        if project_name != "sbm-suite-context":
            required.add("patches/project-qa-context.json")
    else:
        forbidden.add("patches/completed-objectives.json")
    return required, forbidden


def _read_markdown(source: Path) -> str:
    if source.is_symlink() or not source.is_file():
        raise ObjectiveLifecycleError(
            f"required lifecycle source is not a regular file: {source}"
        )
    try:
        return source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ObjectiveLifecycleError(
            f"required lifecycle source is not readable UTF-8: {source}"
        ) from exc


def _section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ObjectiveLifecycleError(f"missing lifecycle section: {heading}")
    return match.group(0)


def _table_rows(section: str) -> list[dict[str, str]]:
    lines = section.splitlines()[1:]
    table_start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("|") and line.strip().endswith("|")
        ),
        None,
    )
    if table_start is None:
        raise ObjectiveLifecycleError("lifecycle section has no table")

    table_lines: list[str] = []
    for line in lines[table_start:]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            break
        table_lines.append(stripped)
    if len(table_lines) < 2:
        raise ObjectiveLifecycleError("lifecycle section has no complete table")

    detached_rows = [
        line
        for line in lines[table_start + len(table_lines) :]
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if detached_rows:
        raise ObjectiveLifecycleError(
            "lifecycle table is split by a blank line or non-table content"
        )

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line[1:-1].split("|")]

    headers = cells(table_lines[0])
    if "ID" not in headers or "Status" not in headers:
        raise ObjectiveLifecycleError("lifecycle table has invalid columns")
    separator = cells(table_lines[1])
    if len(separator) != len(headers) or not all(
        re.fullmatch(r":?-+:?", value) for value in separator
    ):
        raise ObjectiveLifecycleError("lifecycle table has an invalid separator")

    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        values = cells(line)
        if len(values) != len(headers):
            raise ObjectiveLifecycleError("lifecycle table contains a malformed row")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def _rows_by_id(markdown: str, heading: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in _table_rows(_section(markdown, heading)):
        objective_id = row["ID"]
        if objective_id in result:
            raise ObjectiveLifecycleError(
                f"duplicate objective ID in {heading}: {objective_id}"
            )
        result[objective_id] = row
    return result


def _completed_ids(markdown: str) -> set[str]:
    completed: set[str] = set()
    current_headers: list[str] | None = None
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            current_headers = None
            continue
        values = [cell.strip() for cell in line[1:-1].split("|")]
        if "Objective ID" in values:
            current_headers = values
            continue
        if current_headers is None or all(re.fullmatch(r":?-+:?", value) for value in values):
            continue
        if len(values) != len(current_headers):
            raise ObjectiveLifecycleError("completed-objectives table contains a malformed row")
        row = dict(zip(current_headers, values, strict=True))
        objective_id = row.get("Objective ID")
        if objective_id:
            if objective_id in completed:
                raise ObjectiveLifecycleError(
                    f"duplicate completed objective ID: {objective_id}"
                )
            completed.add(objective_id)
    return completed


def _activation_objective(raw_objectives: Any) -> dict[str, Any]:
    if not isinstance(raw_objectives, list) or len(raw_objectives) != 1:
        raise ObjectiveLifecycleError(
            "objective-activation requires exactly one objectives[] item"
        )
    objective = raw_objectives[0]
    if not isinstance(objective, dict):
        raise ObjectiveLifecycleError("objective-activation item must be an object")
    missing = sorted(REQUIRED_ACTIVATION_FIELDS - set(objective))
    if missing:
        raise ObjectiveLifecycleError(
            "objective-activation item is missing: " + ", ".join(missing)
        )
    if objective.get("status") != "active":
        raise ObjectiveLifecycleError(
            "objective-activation desired status must be active"
        )
    return objective


def validate_activation(
    raw_objectives: Any,
    operational_contexts: list[Path],
    completed_context: Path,
) -> None:
    objective = _activation_objective(raw_objectives)
    objective_id = objective["objective_id"]

    completed = _completed_ids(_read_markdown(completed_context))
    if objective_id in completed:
        raise ObjectiveLifecycleError(
            f"cannot activate completed objective: {objective_id}"
        )

    expected_literal = {
        "Objective": objective["objective"],
        "Priority": str(objective["priority"]),
        "Target date": objective["target_date"],
        "Branch": objective["branch"],
    }

    seen_contexts: set[Path] = set()
    for source in operational_contexts:
        resolved = source.resolve(strict=True)
        if resolved in seen_contexts:
            continue
        seen_contexts.add(resolved)
        markdown = _read_markdown(resolved)
        active = _rows_by_id(markdown, ACTIVE_HEADING)
        pending = _rows_by_id(markdown, PENDING_HEADING)

        if objective_id in active:
            raise ObjectiveLifecycleError(
                f"objective is already active in {source}: {objective_id}"
            )
        current = pending.get(objective_id)
        if current is None:
            raise ObjectiveLifecycleError(
                f"pending objective does not exist in {source}: {objective_id}"
            )
        if current.get("Status") != "pending":
            raise ObjectiveLifecycleError(
                f"objective current status is not pending in {source}: {objective_id}"
            )
        for column, desired_value in expected_literal.items():
            if current.get(column) != desired_value:
                raise ObjectiveLifecycleError(
                    f"objective-activation must preserve {column} literally for "
                    f"{objective_id}"
                )


def validate_existing_objective(
    raw_objectives: Any,
    lifecycle_phase: str,
    operational_contexts: list[Path],
    completed_context: Path,
) -> None:
    route = lifecycle_route(lifecycle_phase)
    if route not in {"implementation-progress", "implementation-closure"}:
        raise ObjectiveLifecycleError(
            "existing-objective validation requires implementation-progress "
            "or implementation-closure"
        )
    if not isinstance(raw_objectives, list) or len(raw_objectives) != 1:
        raise ObjectiveLifecycleError(
            f"{route} requires exactly one objectives[] item"
        )
    objective = raw_objectives[0]
    if not isinstance(objective, dict):
        raise ObjectiveLifecycleError(f"{route} item must be an object")
    objective_id = objective.get("objective_id")
    if not isinstance(objective_id, str) or not objective_id:
        raise ObjectiveLifecycleError(f"{route} requires objective_id")

    completed = _completed_ids(_read_markdown(completed_context))
    if objective_id in completed:
        raise ObjectiveLifecycleError(
            f"cannot route completed objective through {route}: {objective_id}"
        )

    seen_contexts: set[Path] = set()
    for source in operational_contexts:
        resolved = source.resolve(strict=True)
        if resolved in seen_contexts:
            continue
        seen_contexts.add(resolved)
        markdown = _read_markdown(resolved)
        active = _rows_by_id(markdown, ACTIVE_HEADING)
        pending = _rows_by_id(markdown, PENDING_HEADING)
        if objective_id in active and objective_id in pending:
            raise ObjectiveLifecycleError(
                f"objective exists in active and pending sections in {source}: "
                f"{objective_id}"
            )
        if route == "implementation-closure":
            if (
                objective_id not in active
                or active[objective_id].get("Status") != "active"
            ):
                raise ObjectiveLifecycleError(
                    f"implementation-closure requires an active objective in "
                    f"{source}: {objective_id}"
                )
        elif objective_id in active:
            if active[objective_id].get("Status") != "active":
                raise ObjectiveLifecycleError(
                    f"implementation-progress found invalid active status in "
                    f"{source}: {objective_id}"
                )
        elif objective_id in pending:
            if pending[objective_id].get("Status") != "pending":
                raise ObjectiveLifecycleError(
                    f"implementation-progress found invalid pending status in "
                    f"{source}: {objective_id}"
                )
        else:
            raise ObjectiveLifecycleError(
                f"objective does not exist in operational context {source}: "
                f"{objective_id}"
            )


def resolve_project_root(suite_root: Path, canonical_path: str) -> Path:
    resolved_suite = suite_root.resolve(strict=True)
    canonical = PurePosixPath(canonical_path)
    if canonical.is_absolute() or ".." in canonical.parts:
        raise ObjectiveLifecycleError("canonical_project_path is unsafe")
    if not canonical.parts or canonical.parts[0] != resolved_suite.name:
        raise ObjectiveLifecycleError(
            "canonical_project_path does not belong to SBM-SUITE"
        )
    candidate = (resolved_suite.parent / Path(*canonical.parts)).resolve(strict=True)
    if os.path.commonpath((resolved_suite, candidate)) != str(resolved_suite):
        raise ObjectiveLifecycleError("resolved project root escapes SBM-SUITE")
    if not candidate.is_dir():
        raise ObjectiveLifecycleError("resolved project root is not a directory")
    return candidate


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lifecycle-phase", required=True, choices=LIFECYCLE_ROUTES)
    parser.add_argument("--objectives-json", required=True)
    parser.add_argument("--operational-context", action="append", required=True)
    parser.add_argument("--completed-context", required=True)
    arguments = parser.parse_args()
    try:
        objectives = json.loads(arguments.objectives_json)
        route = lifecycle_route(arguments.lifecycle_phase)
        contexts = [Path(value) for value in arguments.operational_context]
        completed = Path(arguments.completed_context)
        if route == "objective-activation":
            validate_activation(objectives, contexts, completed)
        elif route in {"implementation-progress", "implementation-closure"}:
            validate_existing_objective(objectives, route, contexts, completed)
        else:
            raise ObjectiveLifecycleError(
                "planning-activation does not use existing-objective preflight"
            )
    except (json.JSONDecodeError, ObjectiveLifecycleError, OSError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(f"{route} preflight validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
