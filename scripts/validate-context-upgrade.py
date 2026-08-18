#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile


class ValidationError(RuntimeError):
    pass


GLOBAL_PROJECT_CONTEXT = "SBM-SUITE/context/PROJECT_CONTEXT.md"
GLOBAL_QA_CONTEXT = "SBM-SUITE/context/QA_CONTEXT.md"
PROJECT_OBJECTIVE_SUMMARY_HEADER = (
    "| Project | Purpose | Active objective | Pending objectives | "
    "Branch | Main context | QA context | Documentation |"
)
SUMMARY_TABLE_HEADERS = {
    PROJECT_OBJECTIVE_SUMMARY_HEADER,
    "| Project | QA context | Test count | Passed | Failed | Coverage | "
    "SonarQube status | Last execution | Overall risk | Evidence |",
}
PROJECT_OBJECTIVE_SUMMARY_MUTABLE_COLUMNS = {
    PROJECT_OBJECTIVE_SUMMARY_HEADER: {
        "Active objective",
        "Pending objectives",
        "Branch",
    },
}
SOURCE_AUTHORITY_FIELDS = (
    "contract_version",
    "project_name",
    "execution_mode",
    "canonical_project_path",
    "lifecycle_phase",
    "objectives",
    "supported_patch_paths",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{label} no contiene JSON válido: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{label} debe contener un objeto JSON")
    return value


def _safe_zip_names(archive: ZipFile, label: str) -> list[str]:
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValidationError(f"{label} contiene rutas duplicadas")
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise ValidationError(f"{label} contiene ruta insegura: {name}")
    return names


def _load_source_package(deploy_package: Path) -> tuple[dict, dict[str, bytes]]:
    try:
        with ZipFile(deploy_package) as outer:
            _safe_zip_names(outer, "context-deploy-package.zip")
            nested_bytes = outer.read("context-package.zip")
    except (BadZipFile, KeyError) as exc:
        raise ValidationError(
            "output/context-deploy-package.zip inválido o sin context-package.zip"
        ) from exc

    try:
        with ZipFile(BytesIO(nested_bytes)) as inner:
            names = _safe_zip_names(inner, "context-package.zip")
            manifest = _read_json(inner.read("manifest.json"), "source manifest.json")
            entries = {
                name: inner.read(name)
                for name in names
                if not name.endswith("/")
            }
    except (BadZipFile, KeyError) as exc:
        raise ValidationError("context-package.zip inválido o sin manifest.json") from exc
    return manifest, entries


def _load_upgrade(upgrade_zip: Path) -> tuple[dict, dict[str, dict]]:
    try:
        with ZipFile(upgrade_zip) as archive:
            names = _safe_zip_names(archive, "context-upgrade.zip")
            manifest = _read_json(archive.read("manifest.json"), "upgrade manifest.json")
            patches: dict[str, dict] = {}
            for name in names:
                if name.startswith("patches/") and name.endswith(".json"):
                    patches[name] = _read_json(archive.read(name), name)
    except (BadZipFile, KeyError) as exc:
        raise ValidationError("context-upgrade.zip inválido o sin manifest.json") from exc
    return manifest, patches


def _validate_manifest_origin(source: dict, upgrade: dict) -> None:
    for field in SOURCE_AUTHORITY_FIELDS:
        if upgrade.get(field) != source.get(field):
            raise ValidationError(
                f"manifest.{field} diverge del context-deploy original; "
                "regenere desde context-deploy"
            )


def _resolve_casefold(base: Path, parts: tuple[str, ...]) -> Path:
    current = base
    for part in parts:
        exact = current / part
        if exact.exists():
            current = exact
            continue
        if not current.is_dir():
            raise ValidationError(f"No se puede resolver ruta local: {current / part}")
        matches = [child for child in current.iterdir() if child.name.casefold() == part.casefold()]
        if len(matches) != 1:
            raise ValidationError(f"Ruta local ambigua o inexistente: {current / part}")
        current = matches[0]
    return current


def _local_target(suite_root: Path, archive_target: str) -> Path:
    path = PurePosixPath(archive_target)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValidationError(f"target_file inseguro: {archive_target}")
    if path.parts[0] != "SBM-SUITE":
        raise ValidationError(f"target_file fuera de SBM-SUITE: {archive_target}")
    return _resolve_casefold(suite_root, tuple(path.parts[1:]))


def _heading_level(line: str) -> int | None:
    match = re.fullmatch(r"(#{1,6})\s+.+", line.strip())
    return len(match.group(1)) if match else None


def _section_bounds(markdown: str, heading: str) -> tuple[list[str], int, int]:
    lines = markdown.splitlines()
    matches = [index for index, line in enumerate(lines) if line.strip() == heading]
    if len(matches) != 1:
        raise ValidationError(
            f"Se esperaba exactamente una sección {heading!r}; encontradas {len(matches)}"
        )
    start = matches[0]
    level = _heading_level(lines[start])
    if level is None:
        raise ValidationError(f"Heading inválido: {heading}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        next_level = _heading_level(lines[index])
        if next_level is not None and next_level <= level:
            end = index
            break
    return lines, start, end


def _apply_operation(markdown: str, operation: dict, target: str) -> str:
    op = operation.get("operation")
    heading = operation.get("heading")
    content = operation.get("content")
    if op not in {"replace_section", "append_to_section"}:
        raise ValidationError(f"Operación inválida en {target}: {op!r}")
    if not isinstance(heading, str) or not heading.strip():
        raise ValidationError(f"heading inválido en {target}")
    if not isinstance(content, str) or not content.strip():
        raise ValidationError(f"content inválido en {target} {heading}")

    lines, start, end = _section_bounds(markdown, heading)
    content_lines = content.strip("\n").splitlines()

    if op == "replace_section":
        if not content_lines or content_lines[0].strip() != heading:
            raise ValidationError(
                f"replace_section debe comenzar con el heading exacto: {target} {heading}"
            )
        replacement = content_lines
        if end < len(lines) and replacement and replacement[-1].strip():
            replacement = replacement + [""]
        result = lines[:start] + replacement + lines[end:]
        return "\n".join(result).rstrip() + "\n"

    append_lines = content_lines
    insertion = end
    prefix = lines[:insertion]
    suffix = lines[insertion:]
    if prefix and prefix[-1].strip():
        prefix = prefix + [""]
    if append_lines and append_lines[-1].strip() and suffix:
        append_lines = append_lines + [""]
    return "\n".join(prefix + append_lines + suffix).rstrip() + "\n"


def _markdown_tables(markdown: str) -> dict[str, tuple[str, list[str]]]:
    tables: dict[str, tuple[str, list[str]]] = {}
    heading = ""
    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if re.fullmatch(r"#{1,3}\s+.+", line):
            heading = line
        if (
            line.startswith("|")
            and index + 1 < len(lines)
            and re.fullmatch(r"\|[\s|:-]+\|", lines[index + 1].strip())
        ):
            header = line
            rows: list[str] = []
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            tables[heading] = (header, rows)
            continue
        index += 1
    return tables


def _table_cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip()[1:-1].split("|")]


def _selected_project_summary_row(
    row: str,
    project_name: str,
    project_directory: str,
) -> bool:
    cells = _table_cells(row)
    if not cells:
        return False
    aliases = {project_name.casefold(), project_directory.casefold()}
    if project_name.casefold() == "sbm-suite-context":
        aliases |= {"sbm-suite", "sbm-suite/context"}
    return cells[0].strip("` ").casefold() in aliases


def _activation_summary_change_allowed(
    header: str,
    original_row: str,
    patched_rows: list[str],
    project_name: str,
    project_directory: str,
    objectives: list[dict],
) -> bool:
    if header not in PROJECT_OBJECTIVE_SUMMARY_MUTABLE_COLUMNS:
        return False
    if not _selected_project_summary_row(
        original_row, project_name, project_directory
    ):
        return False

    original_cells = _table_cells(original_row)
    matches = [
        row
        for row in patched_rows
        if _selected_project_summary_row(row, project_name, project_directory)
    ]
    if len(matches) != 1:
        return False
    patched_cells = _table_cells(matches[0])
    headers = _table_cells(header)
    if len(original_cells) != len(headers) or len(patched_cells) != len(headers):
        return False

    changed = {
        column
        for column, before, after in zip(
            headers, original_cells, patched_cells, strict=True
        )
        if before != after
    }
    if not changed <= PROJECT_OBJECTIVE_SUMMARY_MUTABLE_COLUMNS[header]:
        return False

    objective_ids = [objective["objective_id"] for objective in objectives]
    values = dict(zip(headers, patched_cells, strict=True))
    if "Active objective" in changed:
        active_value = values["Active objective"].replace("`", "")
        if any(objective_id not in active_value for objective_id in objective_ids):
            return False
    if "Branch" in changed:
        branches = {objective.get("branch") for objective in objectives}
        if len(branches) != 1 or values["Branch"].strip("` ") not in branches:
            return False
    if "Pending objectives" in changed:
        original_values = dict(zip(headers, original_cells, strict=True))
        if any(
            objective_id not in original_values["Pending objectives"]
            or objective_id in values["Pending objectives"]
            for objective_id in objective_ids
        ):
            return False
    return True


def _validate_preserved_tables(
    original: str,
    patched: str,
    archive_target: str,
    project_name: str,
    project_directory: str,
    lifecycle_phase: str,
    objectives: list[dict],
) -> None:
    objective_ids = [objective["objective_id"] for objective in objectives]
    original_tables = _markdown_tables(original)
    patched_tables = _markdown_tables(patched)

    for heading, (header, rows) in original_tables.items():
        if heading not in patched_tables:
            raise ValidationError(
                f"Patch removes a required table: {archive_target} {heading}"
            )
        patched_header, patched_rows = patched_tables[heading]
        if patched_header != header:
            raise ValidationError(
                f"Patch changes a table header: {archive_target} {heading}"
            )

        project_objective_summary = (
            archive_target == GLOBAL_PROJECT_CONTEXT
            and heading == "## 6. Project objective summaries"
        )
        if project_objective_summary and header != PROJECT_OBJECTIVE_SUMMARY_HEADER:
            raise ValidationError(
                "PROJECT_CONTEXT project objective summary must use canonical table schema"
            )

        for row in rows:
            requested_objective_row = any(
                objective_id in row for objective_id in objective_ids
            )
            if lifecycle_phase == "objective-activation" and project_objective_summary:
                requested_objective_row = False
            current_project_summary = (
                archive_target in {GLOBAL_PROJECT_CONTEXT, GLOBAL_QA_CONTEXT}
                and header in SUMMARY_TABLE_HEADERS
                and any(
                    marker.casefold() in row.casefold()
                    for marker in (project_name, project_directory)
                )
            )
            activation_project_summary = (
                lifecycle_phase == "objective-activation"
                and archive_target == GLOBAL_PROJECT_CONTEXT
                and _activation_summary_change_allowed(
                    header,
                    row,
                    patched_rows,
                    project_name,
                    project_directory,
                    objectives,
                )
            )
            if (
                lifecycle_phase == "objective-activation"
                and archive_target == GLOBAL_PROJECT_CONTEXT
                and header in PROJECT_OBJECTIVE_SUMMARY_MUTABLE_COLUMNS
            ):
                current_project_summary = False
            if (
                not requested_objective_row
                and not current_project_summary
                and not activation_project_summary
            ):
                if row not in patched_rows:
                    raise ValidationError(
                        "Patch removes or changes an unrelated table row: "
                        f"{archive_target} {heading}"
                    )


def validate(
    upgrade_zip: Path,
    deploy_package: Path,
    suite_root: Path,
) -> None:
    source_manifest, source_entries = _load_source_package(deploy_package)
    upgrade_manifest, patches = _load_upgrade(upgrade_zip)
    _validate_manifest_origin(source_manifest, upgrade_manifest)

    project_name = upgrade_manifest.get("project_name")
    canonical_project_path = upgrade_manifest.get("canonical_project_path")
    objectives = upgrade_manifest.get("objectives")
    if not isinstance(project_name, str) or not project_name:
        raise ValidationError("manifest.project_name inválido")
    if not isinstance(canonical_project_path, str) or not canonical_project_path:
        raise ValidationError("manifest.canonical_project_path inválido")
    if not isinstance(objectives, list) or not objectives:
        raise ValidationError("manifest.objectives inválido")

    objective_ids = [
        item.get("objective_id")
        for item in objectives
        if isinstance(item, dict) and isinstance(item.get("objective_id"), str)
    ]
    if len(objective_ids) != len(objectives):
        raise ValidationError("manifest.objectives contiene objective_id inválido")

    project_directory = PurePosixPath(canonical_project_path.rstrip("/")).name
    target_hashes = source_manifest.get("target_content_hashes")
    if not isinstance(target_hashes, dict):
        raise ValidationError("source manifest.target_content_hashes inválido")

    staged_by_target: dict[str, str] = {}
    original_by_target: dict[str, str] = {}

    for patch_name, patch in sorted(patches.items()):
        target = patch.get("target_file")
        operations = patch.get("operations")
        if not isinstance(target, str) or not target:
            raise ValidationError(f"{patch_name}: target_file inválido")
        if not isinstance(operations, list) or not operations:
            raise ValidationError(f"{patch_name}: operations debe ser no vacío")
        if target not in source_entries:
            raise ValidationError(
                f"{patch_name}: source snapshot ausente para {target}; regenere context-deploy"
            )
        expected_hash = target_hashes.get(target)
        if not isinstance(expected_hash, str) or not expected_hash:
            raise ValidationError(
                f"{patch_name}: target_content_hash ausente para {target}"
            )
        source_bytes = source_entries[target]
        if _sha256(source_bytes) != expected_hash:
            raise ValidationError(
                f"{patch_name}: hash del source snapshot no coincide para {target}"
            )

        local_path = _local_target(suite_root, target)
        if not local_path.is_file():
            raise ValidationError(f"Target local inexistente: {local_path}")
        if _sha256(local_path.read_bytes()) != expected_hash:
            raise ValidationError(
                f"Source-of-truth cambió desde context-deploy: {target}; "
                "ejecute context-deploy nuevamente"
            )

        try:
            original = source_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Snapshot no UTF-8: {target}") from exc

        staged = staged_by_target.get(target, original)
        original_by_target.setdefault(target, original)
        seen_headings: set[str] = set()
        for operation in operations:
            if not isinstance(operation, dict):
                raise ValidationError(f"{patch_name}: operación inválida")
            heading = operation.get("heading")
            if isinstance(heading, str):
                if heading in seen_headings:
                    raise ValidationError(
                        f"{patch_name}: operación duplicada para {heading}"
                    )
                seen_headings.add(heading)
            staged = _apply_operation(staged, operation, target)
        staged_by_target[target] = staged

    for target, staged in staged_by_target.items():
        _validate_preserved_tables(
            original_by_target[target],
            staged,
            target,
            project_name,
            project_directory,
            upgrade_manifest.get("lifecycle_phase"),
            objectives,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("upgrade_zip", type=Path)
    parser.add_argument("deploy_package", type=Path)
    parser.add_argument("suite_root", type=Path)
    args = parser.parse_args()

    try:
        validate(
            args.upgrade_zip.resolve(),
            args.deploy_package.resolve(),
            args.suite_root.resolve(),
        )
    except ValidationError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc

    print("Preflight de fidelidad validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
