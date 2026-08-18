#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path, PurePosixPath

COMMON_EXCLUDED_PREFIXES = (
    "QA/output/",
    "input/",
    "output/",
)

def run(repository: Path, *args: str) -> bytes:
    return subprocess.run(
        ("git", "-C", str(repository), *args),
        check=True,
        stdout=subprocess.PIPE,
    ).stdout

def excluded(path: str, scope: str) -> bool:
    normalized = PurePosixPath(path).as_posix()
    prefixes = COMMON_EXCLUDED_PREFIXES
    if scope == "qa":
        prefixes = (*prefixes, "documentation/")
    else:
        prefixes = (*prefixes, "documentation/output/", "documentation/input/")
    return any(normalized.startswith(prefix) for prefix in prefixes)

def digest(suite_root: Path, repository_paths: list[str], scope: str = "qa") -> str:
    root = suite_root.resolve(strict=True)
    state = hashlib.sha256()
    for relative in repository_paths:
        repository = (root / relative).resolve(strict=True)
        if repository.parent != root and root not in repository.parents:
            raise SystemExit(f"ERROR: repository escapes suite root: {relative}")
        state.update(relative.encode("utf-8") + b"\0")
        state.update(run(repository, "rev-parse", "HEAD"))
        changed = run(
            repository,
            "status",
            "--porcelain",
            "--untracked-files=all",
            "-z",
        ).split(b"\0")
        paths = sorted(
            {
                item[3:].decode("utf-8")
                for item in changed
                if item and len(item) > 3 and not excluded(item[3:].decode("utf-8"), scope)
            }
        )
        for path in paths:
            state.update(path.encode("utf-8") + b"\0")
            candidate = repository / path
            if candidate.is_file() and not candidate.is_symlink():
                state.update(candidate.read_bytes())
            else:
                state.update(b"<missing-or-nonregular>")
    return state.hexdigest()

def repository_paths(helper: Path) -> list[str]:
    output = subprocess.run(
        ("python3", str(helper), "list-paths"),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    return [line for line in output.splitlines() if line]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", required=True)
    parser.add_argument("--repository-helper", required=True)
    parser.add_argument("--expect")
    parser.add_argument("--scope", choices=("qa", "documentation"), default="qa")
    args = parser.parse_args()
    value = digest(
        Path(args.suite_root),
        repository_paths(Path(args.repository_helper)),
        args.scope,
    )
    if args.expect is not None and value != args.expect:
        raise SystemExit("ERROR: QA gate no corresponde al estado actual de la branch")
    print(value)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
