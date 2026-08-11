#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile


class DocumentationUpgradeValidationError(ValueError):
    pass


def _validate_archive_path(path: str, *, field: str) -> None:
    candidate = PurePosixPath(path)
    if (
        not path
        or path.endswith("/")
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in path
        or candidate.as_posix() != path
    ):
        raise DocumentationUpgradeValidationError(
            f"{field} contiene una ruta inválida: {path!r}"
        )


def validate_documentation_upgrade(zip_path: str) -> dict[str, object]:
    try:
        with ZipFile(zip_path) as archive:
            members = [info.filename for info in archive.infolist() if not info.is_dir()]
            if len(members) != len(set(members)):
                duplicates = sorted(
                    {path for path in members if members.count(path) > 1}
                )
                raise DocumentationUpgradeValidationError(
                    "el ZIP contiene rutas duplicadas: " + ", ".join(duplicates)
                )
            for path in members:
                _validate_archive_path(path, field="ZIP")
            if members.count("manifest.json") != 1:
                raise DocumentationUpgradeValidationError(
                    "el ZIP debe contener manifest.json exactamente una vez"
                )
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    except (BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DocumentationUpgradeValidationError(
            f"no se pudo leer documentation-upgrade.zip: {exc}"
        ) from exc

    if not isinstance(manifest, dict):
        raise DocumentationUpgradeValidationError("manifest.json debe ser un objeto")

    updated_files = manifest.get("updated_files")
    if not isinstance(updated_files, list) or not all(
        isinstance(path, str) for path in updated_files
    ):
        raise DocumentationUpgradeValidationError(
            "manifest.updated_files debe ser un array de rutas"
        )
    if len(updated_files) != len(set(updated_files)):
        duplicates = sorted(
            {path for path in updated_files if updated_files.count(path) > 1}
        )
        raise DocumentationUpgradeValidationError(
            "manifest.updated_files contiene rutas duplicadas: "
            + ", ".join(duplicates)
        )
    for path in updated_files:
        _validate_archive_path(path, field="manifest.updated_files")
    if "manifest.json" in updated_files:
        raise DocumentationUpgradeValidationError(
            "manifest.updated_files no debe contener manifest.json"
        )

    physical_files = set(members) - {"manifest.json"}
    declared_files = set(updated_files)
    missing_from_manifest = sorted(physical_files - declared_files)
    absent_from_zip = sorted(declared_files - physical_files)
    if missing_from_manifest or absent_from_zip:
        details = [
            "manifest.updated_files no coincide con los archivos físicos del ZIP"
        ]
        if missing_from_manifest:
            details.append(
                "archivos del ZIP faltantes en manifest.updated_files: "
                + ", ".join(missing_from_manifest)
            )
        if absent_from_zip:
            details.append(
                "archivos declarados pero ausentes del ZIP: "
                + ", ".join(absent_from_zip)
            )
        raise DocumentationUpgradeValidationError("; ".join(details))

    return manifest


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path")
    arguments = parser.parse_args()
    try:
        validate_documentation_upgrade(arguments.zip_path)
    except (DocumentationUpgradeValidationError, OSError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print("Preflight documentation-upgrade.zip validado")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
