#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

FINAL_STATES = {"completed", "registered", "cancelled", "deleted"}
OPERATIONAL_STATES = {"active", "pending"}

def cells(line: str) -> list[str]:
    return [value.strip() for value in line[1:-1].split("|")]

def table_records(text: str):
    headers = None
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            headers = None
            continue
        values = cells(line)
        if values and all(re.fullmatch(r":?-{3,}:?", value) for value in values):
            continue
        if "Objective ID" in values or "ID" in values:
            headers = values
            continue
        if headers is not None and len(values) == len(headers):
            yield dict(zip(headers, values, strict=True))

def validate_batch(objective_ids: Sequence[str], branch: str, project_path: Path, completed_path: Path) -> None:
    if not objective_ids or any(not value.strip() for value in objective_ids):
        raise SystemExit("ERROR: se requiere al menos un objective-id no vacío")
    duplicates = sorted({value for value in objective_ids if objective_ids.count(value) > 1})
    if duplicates:
        raise SystemExit("ERROR: objective-id duplicado en la solicitud: " + ", ".join(duplicates))
    project_records = list(table_records(project_path.read_text(encoding="utf-8")))
    completed_records = list(table_records(completed_path.read_text(encoding="utf-8")))
    for objective_id in objective_ids:
        matches = []
        for row in project_records:
            if row.get("ID") == objective_id and row.get("Status") in OPERATIONAL_STATES:
                matches.append((row, row["Status"]))
        for row in completed_records:
            if row.get("Objective ID") == objective_id and row.get("Final status") in FINAL_STATES:
                matches.append((row, row["Final status"]))
        if len(matches) != 1:
            raise SystemExit(f"ERROR: {objective_id} debe existir exactamente una vez con estado lifecycle válido")
        row, _ = matches[0]
        recorded_branch = row.get("Branch", "").strip("`")
        if recorded_branch != branch:
            raise SystemExit(f"ERROR: Branch lifecycle para {objective_id} es '{recorded_branch or 'N/A'}', no '{branch}'")

def main() -> int:
    arguments = sys.argv[1:]
    if len(arguments) == 4 and not any(value.startswith("--") for value in arguments):
        objective_ids, branch, project, completed = [arguments[0]], arguments[1], arguments[2], arguments[3]
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--branch", required=True)
        parser.add_argument("--project-context", required=True)
        parser.add_argument("--completed-objectives", required=True)
        parser.add_argument("objective_ids", nargs="+")
        parsed = parser.parse_args(arguments)
        objective_ids, branch = parsed.objective_ids, parsed.branch
        project, completed = parsed.project_context, parsed.completed_objectives
    validate_batch(objective_ids, branch, Path(project), Path(completed))
    print("Lifecycle batch validado: " + ", ".join(objective_ids) + f" / {branch}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
