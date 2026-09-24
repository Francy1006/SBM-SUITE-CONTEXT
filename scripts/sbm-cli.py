#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from objective_lifecycle import (
    ACTIVE_HEADING,
    GIT_FLOW_BRANCH_PATTERN,
    ObjectiveLifecycleError,
    _read_markdown,
    _rows_by_id,
)


def active_objective(
    context_file: Path, requested_objective_id: str | None = None
) -> tuple[str, str]:
    rows = _rows_by_id(_read_markdown(context_file), ACTIVE_HEADING)
    applicable = [
        row
        for row in rows.values()
        if row.get("Status") == "active"
    ]
    if not applicable:
        raise ObjectiveLifecycleError("no existe un objetivo activo")
    if requested_objective_id is not None:
        row = rows.get(requested_objective_id)
        if row is None or row.get("Status") != "active":
            raise ObjectiveLifecycleError(
                f"objetivo activo no encontrado: {requested_objective_id}"
            )
    elif len(applicable) != 1:
        available_ids = sorted(row["ID"] for row in applicable)
        ids = ", ".join(available_ids)
        raise ObjectiveLifecycleError(
            f"objetivo activo ambiguo: {ids}. Ejemplo: sbm qa {available_ids[0]}"
        )
    else:
        row = applicable[0]
    objective_id = row.get("ID", "")
    branch = row.get("Branch", "")
    if not objective_id:
        raise ObjectiveLifecycleError("el objetivo activo no tiene ID")
    if GIT_FLOW_BRANCH_PATTERN.fullmatch(branch) is None:
        raise ObjectiveLifecycleError("el objetivo activo no tiene branch lifecycle válida")
    return objective_id, branch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-context", required=True)
    parser.add_argument("--objective-id")
    args = parser.parse_args()
    try:
        objective_id, branch = active_objective(
            Path(args.project_context), args.objective_id
        )
    except ObjectiveLifecycleError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    objectives = json.dumps(
        [{"objective_id": objective_id}],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    sys.stdout.write(f"{objective_id}\t{branch}\t{objectives}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
