#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path, PurePosixPath
import os
import sys
from typing import NoReturn


def fail(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")


def discover_repositories() -> list[tuple[str, str]]:
    script_dir = Path(__file__).resolve().parent
    context_root = script_dir.parent
    suite_root = context_root.parent.resolve(strict=True)

    physical: list[str] = []
    for current_root, directory_names, file_names in os.walk(suite_root):
        if ".git" not in directory_names and ".git" not in file_names:
            continue

        repository = Path(current_root).relative_to(suite_root).as_posix()
        if repository == ".":
            fail("SBM-SUITE no debe ser un repositorio Git raíz")

        path = PurePosixPath(repository)
        if path.is_absolute() or ".." in path.parts or str(path) != repository:
            fail(f"Repositorio Git no canónico: {repository}")

        physical.append(repository)
        # A repository is an inventory boundary. Do not traverse .git, backups,
        # worktrees or any nested content inside that repository.
        directory_names[:] = []

    if not physical:
        fail("No se encontraron repositorios Git bajo SBM-SUITE")

    physical_by_casefold: dict[str, list[str]] = {}
    for repository in physical:
        physical_by_casefold.setdefault(repository.casefold(), []).append(repository)
    for matches in physical_by_casefold.values():
        if len(matches) > 1:
            fail("Repositorios Git ambiguos por casing: " + ", ".join(sorted(matches)))

    ordered = sorted(
        physical,
        key=lambda value: (value.casefold() != "context", value.casefold()),
    )
    return [(PurePosixPath(path).name, path) for path in ordered]


def resolve_selector(
    repositories: list[tuple[str, str]], selector: str
) -> str:
    normalized = selector.strip().casefold()
    matches = [
        path
        for project, path in repositories
        if normalized in {project.casefold(), path.casefold()}
    ]
    unique = list(dict.fromkeys(path.casefold() for path in matches))
    if not matches:
        fail(f"Proyecto no encontrado: {selector}")
    if len(unique) != 1:
        fail(f"Selector ambiguo: {selector}")
    return matches[0]


def main() -> int:
    if len(sys.argv) < 2:
        fail("Uso: suite-repositories.py list|list-paths|resolve [selector]")

    mode = sys.argv[1]
    repositories = discover_repositories()

    if mode == "list":
        for project, path in repositories:
            print(f"{project}\t{path}")
        return 0

    if mode == "list-paths":
        for _, path in repositories:
            print(path)
        return 0

    if mode == "resolve":
        if len(sys.argv) != 3:
            fail("Uso: suite-repositories.py resolve <project-or-path>")
        print(resolve_selector(repositories, sys.argv[2]))
        return 0

    fail(f"Modo no soportado: {mode}")


if __name__ == "__main__":
    raise SystemExit(main())
