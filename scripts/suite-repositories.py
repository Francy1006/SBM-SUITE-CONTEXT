#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path, PurePosixPath
import os
import re
import sys


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"ERROR: {message}")


def cells(line: str) -> list[str]:
    return [value.strip() for value in line[1:-1].split("|")]


def load_repositories() -> list[tuple[str, str]]:
    script_dir = Path(__file__).resolve().parent
    context_root = script_dir.parent
    suite_root = context_root.parent.resolve(strict=True)
    project_context = context_root / "PROJECT_CONTEXT.md"
    if not project_context.is_file():
        fail("No existe context/PROJECT_CONTEXT.md")

    source = project_context.read_text(encoding="utf-8")
    match = re.search(
        r"^## 6\. Project objective summaries\s*$"
        r"(.*?)(?=^##\s+|\Z)",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        fail("PROJECT_CONTEXT.md no contiene Project objective summaries")

    table_lines = [
        line.strip()
        for line in match.group(1).splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(table_lines) < 2:
        fail("Project objective summaries no contiene una tabla")

    headers = cells(table_lines[0])
    try:
        project_index = headers.index("Project")
        main_context_index = headers.index("Main context")
    except ValueError as exc:
        fail("Project objective summaries requiere Project y Main context")

    registered: list[tuple[str, str]] = []
    for line in table_lines[2:]:
        values = cells(line)
        if len(values) != len(headers):
            fail("Project objective summaries contiene una fila inválida")
        project = values[project_index]
        main_context = values[main_context_index].strip("`")
        suffix = "/context/PROJECT_CONTEXT.md"
        if main_context == "context/PROJECT_CONTEXT.md":
            repository = "context"
        elif main_context.endswith(suffix):
            repository = main_context[: -len(suffix)]
        else:
            fail(f"Main context no resuelve un repositorio canónico: {main_context}")

        path = PurePosixPath(repository)
        if path.is_absolute() or ".." in path.parts or str(path) != repository or not path.parts:
            fail(f"Repositorio no canónico en Project objective summaries: {repository}")
        registered.append((project, repository))

    physical: list[str] = []
    for current_root, directory_names, file_names in os.walk(suite_root):
        if ".git" not in directory_names and ".git" not in file_names:
            continue
        repository = Path(current_root).relative_to(suite_root).as_posix()
        if repository == ".":
            fail("SBM-SUITE no debe ser un repositorio Git raíz")
        physical.append(repository)
        directory_names[:] = []

    physical_by_casefold: dict[str, list[str]] = {}
    for repository in physical:
        physical_by_casefold.setdefault(repository.casefold(), []).append(repository)
    for matches in physical_by_casefold.values():
        if len(matches) > 1:
            fail("Repositorios Git ambiguos por casing: " + ", ".join(matches))

    resolved: list[tuple[str, str]] = []
    seen: set[str] = set()
    for project, repository in registered:
        matches = physical_by_casefold.get(repository.casefold(), [])
        physical_path = matches[0] if matches else repository
        key = physical_path.casefold()
        if key in seen:
            continue
        seen.add(key)
        resolved.append((project, physical_path))

    for repository in physical:
        key = repository.casefold()
        if key in seen:
            continue
        seen.add(key)
        resolved.append((PurePosixPath(repository).name, repository))

    if not resolved:
        fail("No se resolvieron repositorios SBM")
    return resolved


def main() -> int:
    if len(sys.argv) < 2:
        fail("Uso: suite-repositories.py list|list-paths|resolve [selector]")
    mode = sys.argv[1]
    repositories = load_repositories()

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
        selector = sys.argv[2].strip().casefold()
        matches = [
            path
            for project, path in repositories
            if selector in {project.casefold(), path.casefold()}
        ]
        unique = list(dict.fromkeys(path.casefold() for path in matches))
        if not matches:
            fail(f"Proyecto no encontrado: {sys.argv[2]}")
        if len(unique) != 1:
            fail(f"Selector ambiguo: {sys.argv[2]}")
        print(matches[0])
        return 0

    fail(f"Modo no soportado: {mode}")


if __name__ == "__main__":
    raise SystemExit(main())
