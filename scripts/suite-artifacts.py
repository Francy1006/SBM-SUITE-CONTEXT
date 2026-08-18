#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import NoReturn


MANAGED_MARKER = "managed-by: SBM-SUITE/context/scripts/suite-artifacts.py"


@dataclass(frozen=True)
class Repository:
    project: str
    relative_path: str
    root: Path


@dataclass(frozen=True)
class PlannedWrite:
    repository: Repository
    source: Path
    target: Path
    state: str


def fail(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")


def safe_relative(value: object, field: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        fail(f"{field} debe ser una ruta relativa no vacía")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        fail(f"{field} contiene una ruta no portable: {value}")
    return path


def inventory(script_dir: Path, suite_root: Path) -> list[Repository]:
    result = subprocess.run(
        ["python3", str(script_dir / "suite-repositories.py"), "list"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    repositories = []
    for line in result.stdout.splitlines():
        project, relative_path = line.split("\t", maxsplit=1)
        root = (suite_root / Path(*PurePosixPath(relative_path).parts)).resolve(
            strict=True
        )
        if os.path.commonpath((suite_root, root)) != str(suite_root):
            fail(f"repositorio escapa de SBM-SUITE: {relative_path}")
        repositories.append(Repository(project, relative_path, root))
    return repositories


def select(repositories: list[Repository], selectors: list[str]) -> list[Repository]:
    if selectors == ["all"]:
        return repositories
    if "all" in selectors:
        fail("all no puede combinarse con otros selectores")
    selected = []
    for selector in selectors:
        normalized = selector.casefold()
        matches = [
            repository
            for repository in repositories
            if normalized
            in {repository.project.casefold(), repository.relative_path.casefold()}
        ]
        if not matches:
            fail(f"proyecto no encontrado: {selector}")
        if len(matches) != 1:
            fail(f"selector ambiguo: {selector}")
        if matches[0] not in selected:
            selected.append(matches[0])
    return selected


def load_artifacts(context_root: Path) -> list[dict[str, object]]:
    manifest_path = context_root / "shared/artifacts.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or not isinstance(payload.get("artifacts"), list):
        fail("shared/artifacts.json tiene un contrato inválido")
    return payload["artifacts"]


def content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_plan(
    context_root: Path,
    repositories: list[Repository],
    artifacts: list[dict[str, object]],
) -> tuple[list[PlannedWrite], list[str], list[str]]:
    plan: list[PlannedWrite] = []
    skipped: list[str] = []
    errors: list[str] = []
    targets: set[Path] = set()
    for index, artifact in enumerate(artifacts, start=1):
        source_relative = safe_relative(artifact.get("source"), f"artifacts[{index}].source")
        target_relative = safe_relative(artifact.get("target"), f"artifacts[{index}].target")
        excluded = artifact.get("exclude_projects", [])
        if not isinstance(excluded, list) or not all(isinstance(item, str) for item in excluded):
            fail(f"artifacts[{index}].exclude_projects debe ser un array de strings")
        source = context_root / Path(*source_relative.parts)
        if source.is_symlink() or not source.is_file():
            fail(f"artefacto fuente inválido: {source_relative}")
        source_hash = content_hash(source)
        for repository in repositories:
            label = f"{repository.relative_path}:{target_relative}"
            if repository.project in excluded:
                skipped.append(label)
                continue
            repository_root = repository.root.resolve(strict=True)
            target = repository_root / Path(*target_relative.parts)
            resolved_target = target.resolve(strict=False)
            if os.path.commonpath((repository_root, resolved_target)) != str(
                repository_root
            ):
                errors.append(f"{label}: target escapa del repositorio")
                continue
            if target in targets:
                errors.append(f"{label}: target duplicado")
                continue
            targets.add(target)
            if target.is_symlink():
                errors.append(f"{label}: symlinks no permitidos")
                continue
            if not target.exists():
                state = "created"
            elif not target.is_file():
                errors.append(f"{label}: target no es un archivo")
                continue
            elif content_hash(target) == source_hash:
                state = "same"
            else:
                try:
                    existing = target.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    errors.append(f"{label}: archivo existente no administrable")
                    continue
                if MANAGED_MARKER not in existing:
                    errors.append(f"{label}: se rechaza sobrescribir contenido no administrado")
                    continue
                state = "updated"
            plan.append(PlannedWrite(repository, source, target, state))
    return plan, skipped, errors


def ensure_clean_targets(plan: list[PlannedWrite]) -> list[str]:
    errors = []
    repositories = {item.repository for item in plan if item.state != "same"}
    for repository in repositories:
        result = subprocess.run(
            ["git", "-C", str(repository.root), "status", "--porcelain"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        if result.stdout:
            errors.append(
                f"{repository.relative_path}: working tree sucio; apply podría sobrescribir cambios locales"
            )
    return errors


def apply_plan(plan: list[PlannedWrite]) -> None:
    staged: list[tuple[PlannedWrite, Path]] = []
    try:
        for item in plan:
            if item.state == "same":
                continue
            item.target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                dir=item.target.parent, prefix=f".{item.target.name}.", delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(item.source.read_bytes())
            source_mode = stat.S_IMODE(item.source.stat().st_mode)
            temporary_path.chmod(source_mode)
            staged.append((item, temporary_path))
        for item, temporary_path in staged:
            os.replace(temporary_path, item.target)
    finally:
        for _, temporary_path in staged:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("check", "apply"))
    parser.add_argument("selectors", nargs="+", metavar="PROJECT|PATH|all")
    arguments = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    context_root = script_dir.parent
    suite_root = context_root.parent.resolve(strict=True)
    repositories = select(
        inventory(script_dir, suite_root), arguments.selectors
    )
    plan, skipped, errors = build_plan(
        context_root, repositories, load_artifacts(context_root)
    )
    if arguments.mode == "apply" and not errors:
        errors.extend(ensure_clean_targets(plan))

    print("Targets:")
    for repository in repositories:
        print(f"- {repository.project}: {repository.relative_path}")
    for state in ("same", "created", "updated"):
        print(f"{state.capitalize()}:")
        values = [
            f"{item.repository.relative_path}:{item.target.relative_to(item.repository.root).as_posix()}"
            for item in plan
            if item.state == state
        ]
        print("\n".join(f"- {value}" for value in values) or "- none")
    print("Skipped:")
    print("\n".join(f"- {value}" for value in skipped) or "- none")
    print("Errors:")
    print("\n".join(f"- {value}" for value in errors) or "- none")
    if errors:
        return 2
    differences = any(item.state != "same" for item in plan)
    if arguments.mode == "check":
        return 1 if differences else 0
    apply_plan(plan)
    print("Apply completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
