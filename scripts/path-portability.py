#!/usr/bin/env python3
from __future__ import annotations

import argparse
import posixpath
import re


WINDOWS_DRIVE = re.compile(r"^([A-Za-z]):(?:/(.*))?$")
MSYS_DRIVE = re.compile(r"^/([A-Za-z])(?:/(.*))?$")


def canonical_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    match = WINDOWS_DRIVE.fullmatch(normalized) or MSYS_DRIVE.fullmatch(normalized)
    if match is not None:
        drive = match.group(1).lower()
        remainder = posixpath.normpath("/" + (match.group(2) or "")).lstrip("/")
        return f"windows:{drive}:/{remainder}".casefold()
    if normalized.startswith("//"):
        return "windows-unc:" + posixpath.normpath(normalized).casefold()
    return "posix:" + posixpath.normpath(normalized)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    canonical = subparsers.add_parser("canonical")
    canonical.add_argument("path")
    equivalent = subparsers.add_parser("equivalent")
    equivalent.add_argument("left")
    equivalent.add_argument("right")
    args = parser.parse_args()

    if args.command == "canonical":
        print(canonical_path(args.path))
        return 0
    return 0 if canonical_path(args.left) == canonical_path(args.right) else 1


if __name__ == "__main__":
    raise SystemExit(main())
