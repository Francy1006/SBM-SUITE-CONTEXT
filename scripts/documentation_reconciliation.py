#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACTIVE_HEADING = "## 3. Active objectives"
PENDING_HEADING = "## 4. Pending objectives"
COMPLETED_HEADING = "## 1. Completed objectives by project"
LIFECYCLE_STATUSES = {"active", "pending", "completed", "registered", "cancelled", "deleted"}
PLANNING_HEADINGS = {"## 11. Pending work", "## 12. Roadmap"}
CANONICAL_DOCUMENTATION_HEADINGS = {
    "## 3. Current state",
    "## 11. Pending work",
    "## 12. Roadmap",
}


class DocumentationReconciliationError(ValueError):
    pass


@dataclass(frozen=True)
class ObjectiveRecord:
    objective_id: str
    project: str
    status: str
    documentation: str


def _read_required(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise DocumentationReconciliationError(
            f"required reconciliation source is not a regular file: {path}"
        )
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DocumentationReconciliationError(
            f"required reconciliation source is not readable UTF-8: {path}"
        ) from exc


def _section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise DocumentationReconciliationError(
            f"missing required reconciliation section: {heading}"
        )
    return match.group(0).strip()


def _table_rows(section: str) -> list[dict[str, str]]:
    lines = section.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip().startswith("|") and line.strip().endswith("|")
        ),
        None,
    )
    if start is None:
        raise DocumentationReconciliationError("objective section has no table")
    table: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            break
        table.append(stripped)
    if len(table) < 2:
        raise DocumentationReconciliationError("objective table is incomplete")

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line[1:-1].split("|")]

    headers = cells(table[0])
    separator = cells(table[1])
    if len(separator) != len(headers) or not all(
        re.fullmatch(r":?-+:?", cell) for cell in separator
    ):
        raise DocumentationReconciliationError("objective table separator is invalid")
    rows: list[dict[str, str]] = []
    for line in table[2:]:
        values = cells(line)
        if len(values) != len(headers):
            raise DocumentationReconciliationError("objective table row is malformed")
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def _operational_objectives(markdown: str) -> list[ObjectiveRecord]:
    records: list[ObjectiveRecord] = []
    for heading, expected_status in (
        (ACTIVE_HEADING, "active"),
        (PENDING_HEADING, "pending"),
    ):
        for row in _table_rows(_section(markdown, heading)):
            objective_id = row.get("ID", "")
            status = row.get("Status", "")
            if not objective_id or status != expected_status:
                raise DocumentationReconciliationError(
                    f"invalid {expected_status} objective row: {objective_id or '<empty>'}"
                )
            records.append(
                ObjectiveRecord(
                    objective_id=objective_id,
                    project=row.get("Project", ""),
                    status=status,
                    documentation=row.get("Documentation", ""),
                )
            )
    return records


def _completed_objectives(markdown: str) -> list[ObjectiveRecord]:
    records: list[ObjectiveRecord] = []
    section = _section(markdown, COMPLETED_HEADING)
    headers: list[str] | None = None
    separator_pending = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            headers = None
            separator_pending = False
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if "Objective ID" in cells and "Final status" in cells:
            headers = cells
            separator_pending = True
            continue
        if headers is None:
            continue
        if separator_pending:
            if len(cells) != len(headers) or not all(
                re.fullmatch(r":?-+:?", cell) for cell in cells
            ):
                raise DocumentationReconciliationError(
                    "completed objective table separator is invalid"
                )
            separator_pending = False
            continue
        if len(cells) != len(headers):
            raise DocumentationReconciliationError(
                "completed objective table row is malformed"
            )
        row = dict(zip(headers, cells, strict=True))
        objective_id = row.get("Objective ID", "")
        status = row.get("Final status", "")
        if not objective_id or status not in {"completed", "registered", "cancelled", "deleted"}:
            continue
        records.append(
            ObjectiveRecord(
                objective_id=objective_id,
                project=row.get("Project", ""),
                status=status,
                documentation=row.get("Documentation", ""),
            )
        )
    return records


def _archive_path(path: Path, documentation_root: Path) -> str:
    return "documentation/" + path.relative_to(documentation_root).as_posix()


def _objective_pattern(objective_id: str) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9_.-]){re.escape(objective_id)}(?![A-Za-z0-9_.-])"
    )


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip()[1:-1].split("|")]


def _unfenced_lines(markdown: str) -> list[str]:
    result: list[str] = []
    fence: str | None = None
    for line in markdown.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)[0]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            result.append("")
            continue
        result.append(
            ""
            if fence is not None or line.startswith(("    ", "\t"))
            else line
        )
    return result


def _canonical_documentation_records(
    pages: dict[str, str],
) -> dict[str, ObjectiveRecord]:
    records: dict[str, list[ObjectiveRecord]] = {}
    for archive_path, markdown in pages.items():
        lines = _unfenced_lines(markdown)
        index = 0
        current_heading = ""
        while index < len(lines):
            line = lines[index].strip()
            if re.match(r"^##(?!#)\s+", line):
                current_heading = line
            if not (line.startswith("|") and line.endswith("|")):
                index += 1
                continue

            table: list[str] = []
            while index < len(lines):
                candidate = lines[index].strip()
                if not (candidate.startswith("|") and candidate.endswith("|")):
                    break
                table.append(candidate)
                index += 1
            if len(table) < 2:
                continue

            headers = _table_cells(table[0])
            if (
                current_heading not in CANONICAL_DOCUMENTATION_HEADINGS
                or "Objective ID" not in headers
                or "Status" not in headers
            ):
                continue
            separator = _table_cells(table[1])
            if len(separator) != len(headers) or not all(
                re.fullmatch(r":?-+:?", cell) for cell in separator
            ):
                raise DocumentationReconciliationError(
                    f"canonical objective table separator is invalid: {archive_path}"
                )

            for raw_row in table[2:]:
                values = _table_cells(raw_row)
                if len(values) != len(headers):
                    raise DocumentationReconciliationError(
                        f"canonical objective table row is malformed: {archive_path}"
                    )
                row = dict(zip(headers, values, strict=True))
                objective_id = row.get("Objective ID", "")
                status = row.get("Status", "").casefold()
                if not objective_id:
                    raise DocumentationReconciliationError(
                        f"canonical objective record has empty Objective ID: {archive_path}"
                    )
                if status not in LIFECYCLE_STATUSES:
                    raise DocumentationReconciliationError(
                        "canonical objective record has invalid status: "
                        f"{objective_id} ({row.get('Status', '')}) in {archive_path}"
                    )
                records.setdefault(objective_id, []).append(
                    ObjectiveRecord(
                        objective_id=objective_id,
                        project=row.get("Project", ""),
                        status=status,
                        documentation=archive_path,
                    )
                )

    effective: dict[str, ObjectiveRecord] = {}
    for objective_id, objective_records in records.items():
        statuses = {record.status for record in objective_records}
        if len(statuses) != 1:
            raise DocumentationReconciliationError(
                "Duplicate canonical objective records with conflicting status: "
                f"{objective_id} ({', '.join(sorted(statuses))})"
            )
        effective[objective_id] = objective_records[0]
    return effective


def _explicit_targets(documentation: str, available: set[str]) -> set[str]:
    candidates: set[str] = set()
    for match in re.finditer(
        r"(?:SBM-SUITE/)?context/documentation/(pages/[^`,;|]+?\.md)|"
        r"(?<!context/)documentation/(pages/[^`,;|]+?\.md)",
        documentation,
    ):
        suffix = match.group(1) or match.group(2)
        candidate = "documentation/" + suffix.strip()
        if candidate in available:
            candidates.add(candidate)
    return candidates


def _context_chunk(
    archive_path: str,
    section: str,
    content: str,
    score: float,
) -> dict[str, Any]:
    point_id = hashlib.sha256(
        f"{archive_path}\0{section}\0{content}".encode("utf-8")
    ).hexdigest()
    return {
        "point_id": point_id,
        "source_path": archive_path,
        "archive_path": archive_path,
        "section": section,
        "score": score,
        "content": content,
    }


def build_reconciliation(
    project_context_path: Path,
    completed_context_path: Path,
    documentation_root: Path,
    project_tree_path: Path | None = None,
) -> dict[str, Any]:
    project_context = _read_required(project_context_path)
    completed_context = _read_required(completed_context_path)
    objectives = _operational_objectives(project_context)
    objectives.extend(_completed_objectives(completed_context))
    context_records: dict[str, list[ObjectiveRecord]] = {}
    for record in objectives:
        context_records.setdefault(record.objective_id, []).append(record)
    for objective_id, records in context_records.items():
        if len(records) <= 1:
            continue
        statuses = {record.status for record in records}
        if len(statuses) > 1:
            raise DocumentationReconciliationError(
                "Duplicate canonical objective records with conflicting status "
                f"in Context: {objective_id} ({', '.join(sorted(statuses))})"
            )
        raise DocumentationReconciliationError(
            f"Duplicate canonical objective records in Context: {objective_id}"
        )

    page_paths = sorted(
        documentation_root.joinpath("pages").rglob("*.md"),
        key=lambda path: path.as_posix().casefold(),
    )
    pages = {
        _archive_path(path, documentation_root): _read_required(path)
        for path in page_paths
    }
    if not pages:
        raise DocumentationReconciliationError(
            "no functional Documentation pages were discovered"
        )
    available = set(pages)
    planning_pages = {
        archive_path
        for archive_path, markdown in pages.items()
        if any(
            re.search(rf"^{re.escape(heading)}\s*$", markdown, re.MULTILINE)
            for heading in PLANNING_HEADINGS
        )
    }
    if not planning_pages:
        raise DocumentationReconciliationError(
            "no authorized planning or roadmap Documentation page was discovered"
        )

    documentation_records = _canonical_documentation_records(pages)

    differences: list[dict[str, Any]] = []
    targets: set[str] = set()
    for record in objectives:
        pattern = _objective_pattern(record.objective_id)
        occurrence_paths: set[str] = set()
        for archive_path, markdown in pages.items():
            if pattern.search(markdown):
                occurrence_paths.add(archive_path)

        documented_record = documentation_records.get(record.objective_id)
        documented_states = (
            {documented_record.status} if documented_record is not None else set()
        )

        if documented_record is not None and documented_record.status == record.status:
            continue

        if documented_record is None and not occurrence_paths:
            difference_type = "missing-objective"
        elif documented_record is None:
            difference_type = "status-unresolved"
        else:
            difference_type = "status-mismatch"

        candidates = set(occurrence_paths)
        candidates.update(_explicit_targets(record.documentation, available))
        if not candidates:
            project_pattern = re.compile(re.escape(record.project), re.IGNORECASE)
            candidates.update(
                path
                for path in planning_pages
                if project_pattern.search(pages[path])
            )
        if not candidates:
            candidates.update(planning_pages)

        targets.update(candidates)
        differences.append(
            {
                "objective_id": record.objective_id,
                "project": record.project,
                "context_status": record.status,
                "documentation_states": sorted(documented_states),
                "difference": difference_type,
                "candidate_paths": sorted(candidates),
            }
        )

    evidence_sections = [
        (
            "SBM-SUITE/context/PROJECT_CONTEXT.md",
            ACTIVE_HEADING,
            _section(project_context, ACTIVE_HEADING),
        ),
        (
            "SBM-SUITE/context/PROJECT_CONTEXT.md",
            PENDING_HEADING,
            _section(project_context, PENDING_HEADING),
        ),
        (
            "SBM-SUITE/context/COMPLETED_OBJECTIVES.md",
            COMPLETED_HEADING,
            _section(completed_context, COMPLETED_HEADING),
        ),
    ]
    if project_tree_path is not None:
        project_tree = _read_required(project_tree_path).strip()
        if project_tree:
            evidence_sections.append(
                (
                    "SBM-SUITE/context/project-tree.txt",
                    "Global project tree",
                    project_tree,
                )
            )

    chunks = [
        _context_chunk(path, section, content, 1.0 - index * 0.001)
        for index, (path, section, content) in enumerate(evidence_sections)
    ]
    summary = (
        "Documentation already synchronized"
        if not differences
        else (
            "Global Context → Documentation reconciliation found "
            f"{len(differences)} lifecycle difference(s) across "
            f"{len({item['project'] for item in differences})} project(s). "
            "Context is the source of truth. Required functional targets: "
            + ", ".join(sorted(targets))
            + ". Differences: "
            + json.dumps(differences, ensure_ascii=False, separators=(",", ":"))
        )
    )
    return {
        "synchronized": not differences,
        "summary": summary,
        "differences": differences,
        "documentation_targets": sorted(targets),
        "retrieved_context_chunks": chunks,
    }


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-context", required=True)
    parser.add_argument("--completed-context", required=True)
    parser.add_argument("--documentation-root", required=True)
    parser.add_argument("--project-tree")
    parser.add_argument("--output")
    arguments = parser.parse_args()
    try:
        result = build_reconciliation(
            Path(arguments.project_context),
            Path(arguments.completed_context),
            Path(arguments.documentation_root),
            Path(arguments.project_tree) if arguments.project_tree else None,
        )
    except (DocumentationReconciliationError, OSError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if arguments.output:
        Path(arguments.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
