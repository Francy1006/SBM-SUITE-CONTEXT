#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path, PurePosixPath


MAX_UNTRACKED_FILE_BYTES = 1024 * 1024
EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".runtime",
    ".tox",
    ".venv",
    "__pycache__",
    "backup",
    "backups",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "output",
    "outputs",
    "runtime",
    "target",
    "temp",
    "tmp",
    "venv",
}
EXCLUDED_SUFFIXES = {
    ".7z", ".a", ".avi", ".bin", ".bmp", ".class", ".dll", ".dylib",
    ".exe", ".gif", ".gz", ".ico", ".jar", ".jpeg", ".jpg", ".key",
    ".mov", ".mp3", ".mp4", ".o", ".p12", ".pdf", ".pem", ".pfx",
    ".png", ".pyc", ".so", ".tar", ".tgz", ".wav", ".webp", ".zip",
}
SENSITIVE_NAMES = {
    ".env",
    "credentials",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
    "secrets",
    "secrets.json",
}
SENSITIVE_STEMS = {"credential", "credentials", "secret", "secrets"}
GENERATED_NAMES = {
    ".coverage",
    ".ds_store",
    "coverage.xml",
    "junit.xml",
    "qa-results.md",
    "test-results.xml",
}


def _git(root: Path, *arguments: str, check: bool = True) -> bytes:
    return subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _paths(output: bytes) -> list[str]:
    return [value.decode("utf-8") for value in output.split(b"\0") if value]


def exclusion_reason(relative: str) -> str | None:
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return "path-outside-scope"
    if any(ord(character) < 32 for character in relative):
        return "unsupported-path"
    lowered_parts = [part.casefold() for part in path.parts]
    if any(part in EXCLUDED_DIRECTORIES for part in lowered_parts[:-1]):
        return "runtime-or-generated-directory"
    name = lowered_parts[-1]
    if (
        name in SENSITIVE_NAMES
        or name.startswith(".env.")
        or PurePosixPath(name).stem in SENSITIVE_STEMS
    ):
        return "sensitive-path"
    if name in GENERATED_NAMES:
        return "generated-artifact"
    if path.suffix.casefold() in EXCLUDED_SUFFIXES:
        return "binary-or-archive-extension"
    return None


def _tracked_binary(root: Path, relative: str, cached: bool) -> bool:
    arguments = ["diff", "--numstat", "--no-ext-diff"]
    if cached:
        arguments.append("--cached")
    arguments.extend(("--", relative))
    output = _git(root, *arguments).decode("utf-8", errors="replace")
    return any(line.startswith("-\t-\t") for line in output.splitlines())


def _tracked_diff(root: Path, relative: str, cached: bool) -> str:
    arguments = ["diff", "--no-ext-diff"]
    if cached:
        arguments.append("--cached")
    arguments.extend(("--", relative))
    return _git(root, *arguments).decode("utf-8")


def _new_file_diff(relative: str, text: str) -> str:
    lines = text.splitlines()
    rendered = [
        f"diff --git a/{relative} b/{relative}",
        "new file mode 100644",
        "--- /dev/null",
        f"+++ b/{relative}",
    ]
    if lines:
        count = len(lines)
        destination = "+1" if count == 1 else f"+1,{count}"
        rendered.append(f"@@ -0,0 {destination} @@")
        rendered.extend("+" + line for line in lines)
        if not text.endswith("\n"):
            rendered.append("\\ No newline at end of file")
    return "\n".join(rendered) + "\n"


def collect_evidence(root: Path) -> tuple[list[str], str, list[tuple[str, str]]]:
    repository = root.resolve(strict=True)
    unstaged = _paths(_git(repository, "diff", "--name-only", "-z", "--", "."))
    staged = _paths(
        _git(repository, "diff", "--cached", "--name-only", "-z", "--", ".")
    )
    untracked = _paths(
        _git(repository, "ls-files", "--others", "--exclude-standard", "-z")
    )

    changed: set[str] = set()
    omitted: dict[str, str] = {}
    patches: list[str] = []
    for cached, paths in ((False, unstaged), (True, staged)):
        for relative in sorted(set(paths)):
            reason = exclusion_reason(relative)
            if reason is None and _tracked_binary(repository, relative, cached):
                reason = "binary-content"
            if reason is not None:
                omitted.setdefault(relative, reason)
                continue
            patch = _tracked_diff(repository, relative, cached)
            if patch:
                patches.append(patch)
                changed.add(relative)

    for relative in sorted(set(untracked)):
        reason = exclusion_reason(relative)
        candidate = repository / Path(*PurePosixPath(relative).parts)
        if reason is None:
            try:
                resolved = candidate.resolve(strict=True)
                if repository != resolved and repository not in resolved.parents:
                    reason = "path-outside-scope"
                elif candidate.is_symlink() or not candidate.is_file():
                    reason = "non-regular-file"
                elif candidate.stat().st_size > MAX_UNTRACKED_FILE_BYTES:
                    reason = f"file-too-large>{MAX_UNTRACKED_FILE_BYTES}"
            except OSError:
                reason = "unreadable-file"
        if reason is None:
            try:
                content = candidate.read_bytes()
                if b"\0" in content:
                    reason = "binary-content"
                else:
                    text = content.decode("utf-8")
            except (OSError, UnicodeDecodeError):
                reason = "binary-or-non-utf8-content"
        if reason is not None:
            omitted.setdefault(relative, reason)
            continue
        patches.append(_new_file_diff(relative, text))
        changed.add(relative)

    canonical_patch = "".join(patch if patch.endswith("\n") else patch + "\n" for patch in patches)
    return sorted(changed), canonical_patch, sorted(omitted.items())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--diff-output", required=True)
    parser.add_argument("--changed-output", required=True)
    parser.add_argument("--omissions-output", required=True)
    args = parser.parse_args()
    changed, patch, omitted = collect_evidence(Path(args.project_root))
    Path(args.diff_output).write_text(patch, encoding="utf-8", newline="\n")
    Path(args.changed_output).write_text(
        "".join(f"{path}\n" for path in changed), encoding="utf-8", newline="\n"
    )
    Path(args.omissions_output).write_text(
        "".join(f"{path}\t{reason}\n" for path, reason in omitted),
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
