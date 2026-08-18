#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def resolve_upgrade_input(input_dir: Path, prefix: str, canonical_name: str) -> tuple[Path, Path]:
    if not input_dir.is_dir():
        raise ValueError(f"No existe {input_dir}")

    zip_files = sorted(
        path for path in input_dir.iterdir() if path.is_file() and path.name.endswith(".zip")
    )
    if len(zip_files) != 1:
        raise ValueError(f"Debe existir exactamente un ZIP en {input_dir}")

    candidate = zip_files[0]
    if not candidate.name.startswith(prefix) or not candidate.name.endswith(".zip"):
        raise ValueError(
            f"El ZIP debe comenzar con {prefix} y terminar en .zip: {candidate.name}"
        )

    canonical = input_dir / canonical_name
    original = candidate
    if candidate != canonical:
        if canonical.exists():
            raise ValueError(f"Ya existe el nombre canónico {canonical}")
        candidate.rename(canonical)

    return original, canonical


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("prefix")
    parser.add_argument("canonical_name")
    args = parser.parse_args()

    try:
        original, canonical = resolve_upgrade_input(
            args.input_dir,
            args.prefix,
            args.canonical_name,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"{original}\t{canonical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
