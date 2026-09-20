#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path, PurePosixPath
import json
import sys
from typing import NoReturn


def fail(message: str) -> NoReturn:
    raise SystemExit(f"ERROR: {message}")


def discover_repositories() -> list[tuple[str, str]]:
    script_dir = Path(__file__).resolve().parent
    inventory_file = script_dir / "suite-repositories.json"
    if not inventory_file.is_file():
        fail("No existe scripts/suite-repositories.json")
    try:
        inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail(f"No se pudo leer scripts/suite-repositories.json: {error}")
    if not isinstance(inventory, list) or not inventory:
        fail("suite-repositories.json debe ser un array no vacío")

    repositories: list[str] = []
    by_casefold: dict[str, list[str]] = {}
    for repository in inventory:
        if not isinstance(repository, str):
            fail("suite-repositories.json contiene un repositorio no textual")
        path = PurePosixPath(repository)
        if (
            not repository
            or path.is_absolute()
            or any(part in {"", ".", ".."} for part in path.parts)
            or str(path) != repository
            or "\\" in repository
        ):
            fail(f"Repositorio no canónico en suite-repositories.json: {repository}")
        repositories.append(repository)
        by_casefold.setdefault(repository.casefold(), []).append(repository)
    for matches in by_casefold.values():
        if len(matches) > 1:
            fail("Repositorios ambiguos por casing: " + ", ".join(sorted(matches)))

    ordered = sorted(
        repositories,
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
