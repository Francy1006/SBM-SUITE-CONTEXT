#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "subprocess failed"
        raise SystemExit(message)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--project-context", default="PROJECT_CONTEXT.md")
    parser.add_argument("--completed-objectives", default="COMPLETED_OBJECTIVES.md")
    parser.add_argument("--documentation-root")
    parser.add_argument("--project-tree")
    parser.add_argument("--reconciliation-helper")
    parser.add_argument("--repository-helper")
    parser.add_argument("--output", default="documentation/output/finalization-gate.json")
    parser.add_argument("objective_ids", nargs="+")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_context = Path(args.project_context).resolve(strict=True)
    completed_objectives = Path(args.completed_objectives).resolve(strict=True)
    context_root = project_context.parent
    suite_root = context_root.parent
    documentation_root = (
        Path(args.documentation_root).resolve(strict=True)
        if args.documentation_root
        else context_root / "documentation"
    )
    project_tree = (
        Path(args.project_tree).resolve(strict=True)
        if args.project_tree
        else context_root / "project-tree.txt"
    )
    reconciliation_helper = (
        Path(args.reconciliation_helper).resolve(strict=True)
        if args.reconciliation_helper
        else script_dir / "documentation_reconciliation.py"
    )
    repository_helper = (
        Path(args.repository_helper).resolve(strict=True)
        if args.repository_helper
        else script_dir / "suite-repositories.py"
    )

    run(
        sys.executable,
        str(script_dir / "objective-git-state.py"),
        "--branch",
        args.branch,
        "--project-context",
        str(project_context),
        "--completed-objectives",
        str(completed_objectives),
        *args.objective_ids,
        cwd=context_root,
    )

    for label, source in (
        ("reconciliation helper", reconciliation_helper),
        ("repository helper", repository_helper),
    ):
        if source.is_symlink() or not source.is_file():
            raise SystemExit(f"ERROR: {label} inexistente: {source}")
    if documentation_root.is_symlink() or not documentation_root.is_dir():
        raise SystemExit(f"ERROR: documentation root inválido: {documentation_root}")
    if project_tree.is_symlink() or not project_tree.is_file():
        raise SystemExit(f"ERROR: project-tree inválido: {project_tree}")

    with tempfile.NamedTemporaryFile(
        prefix="documentation-reconciliation-", suffix=".json", delete=False
    ) as temporary:
        reconciliation_output = Path(temporary.name)
    try:
        result = run(
            sys.executable,
            str(reconciliation_helper),
            "--project-context",
            str(project_context),
            "--completed-context",
            str(completed_objectives),
            "--documentation-root",
            str(documentation_root),
            "--project-tree",
            str(project_tree),
            "--output",
            str(reconciliation_output),
            cwd=context_root,
        )
        try:
            reconciliation = json.loads(
                reconciliation_output.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SystemExit("ERROR: reconciliation output inválido") from exc
        if reconciliation.get("synchronized") is not True:
            summary = (
                reconciliation.get("summary")
                or result.stdout.strip()
                or "Documentation desincronizada"
            )
            raise SystemExit(f"ERROR: Documentation no está sincronizada: {summary}")
    finally:
        reconciliation_output.unlink(missing_ok=True)

    state_sha256 = run(
        sys.executable,
        str(script_dir / "workflow-state.py"),
        "--suite-root",
        str(suite_root),
        "--repository-helper",
        str(repository_helper),
        "--scope",
        "documentation",
        cwd=context_root,
    ).stdout.strip()

    output = Path(args.output)
    if not output.is_absolute():
        output = context_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "branch": args.branch,
                "status": "updated",
                "objectives": args.objective_ids,
                "state_sha256": state_sha256,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Documentation gate registrado para {args.branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
