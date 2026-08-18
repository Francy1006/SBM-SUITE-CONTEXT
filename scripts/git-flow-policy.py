#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import NoReturn

BRANCH_PATTERN = re.compile(r"^(FEATURE|BUGFIX|HOTFIX|RELEASE)-[a-z0-9]+(?:-[a-z0-9]+){0,3}$")

@dataclass(frozen=True)
class BranchPolicy:
    branch_type: str
    base_branch: str = "main"
    integration_branch: str = "main"
    final_branch: str = "main"
    requires_qa_gate: bool = True
    requires_documentation: bool = True

def fail(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")

def policy_for(branch: str) -> BranchPolicy:
    match = BRANCH_PATTERN.fullmatch(branch)
    if match is None:
        fail("branch inválida; use FEATURE|BUGFIX|HOTFIX|RELEASE y un slug de máximo cuatro palabras minúsculas")
    return BranchPolicy(match.group(1))

def load_gate(path: Path, branch: str, status: str, objective_ids: list[str]) -> None:
    if path.is_symlink() or not path.is_file():
        fail(f"gate requerido inexistente: {path.as_posix()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"gate inválido: {path.as_posix()}: {exc}")
    if not isinstance(payload, dict):
        fail(f"gate debe ser un objeto JSON: {path.as_posix()}")
    if payload.get("branch") != branch:
        fail(f"gate no corresponde a {branch}: {path.as_posix()}")
    if payload.get("status") != status:
        fail(f"gate {path.as_posix()} requiere status={status}; recibido={payload.get('status', 'N/A')}")
    if payload.get("objectives") != objective_ids:
        fail(f"gate {path.as_posix()} no corresponde al batch solicitado: " + ", ".join(objective_ids))

def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    describe = subparsers.add_parser("describe")
    describe.add_argument("branch")
    describe.add_argument("--format", choices=("json", "tsv"), default="json")
    gates = subparsers.add_parser("verify-finalization-gates")
    gates.add_argument("branch")
    gates.add_argument("--qa", required=True)
    gates.add_argument("--documentation", required=True)
    gates.add_argument("objective_ids", nargs="+")
    arguments = parser.parse_args()
    policy = policy_for(arguments.branch)
    if arguments.command == "describe":
        values = asdict(policy)
        if arguments.format == "json":
            print(json.dumps(values, separators=(",", ":")))
        else:
            print("\t".join(str(value).lower() if isinstance(value, bool) else str(value) for value in values.values()))
        return 0
    load_gate(Path(arguments.qa), arguments.branch, "passed", arguments.objective_ids)
    load_gate(Path(arguments.documentation), arguments.branch, "updated", arguments.objective_ids)
    print(f"Gates QA completo y Documentation verificados para {arguments.branch}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
