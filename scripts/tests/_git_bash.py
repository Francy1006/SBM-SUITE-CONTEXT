from __future__ import annotations

import os
import atexit
import shlex
import shutil
import sys
import tempfile
from functools import lru_cache
from pathlib import Path, PureWindowsPath


def _is_windows() -> bool:
    return os.name == "nt"


def _exists(path: PureWindowsPath) -> bool:
    return Path(str(path)).is_file()


def _is_system_bash(path: PureWindowsPath) -> bool:
    parts = tuple(part.lower() for part in path.parts)
    return any(
        parts[index:index + 2] in (("windows", "system32"), ("windows", "sysnative"))
        for index in range(len(parts) - 1)
    )


def _git_root_for_bash(path: PureWindowsPath) -> PureWindowsPath | None:
    if path.name.lower() != "bash.exe" or path.parent.name.lower() != "bin":
        return None
    root = path.parent.parent
    if root.name.lower() == "usr":
        root = root.parent
    return root


def _has_git_for_windows(root: PureWindowsPath) -> bool:
    return any(
        _exists(root / relative)
        for relative in (
            "cmd/git.exe",
            "bin/git.exe",
            "mingw64/bin/git.exe",
            "mingw32/bin/git.exe",
        )
    )


def _append_candidate(
    candidates: list[PureWindowsPath],
    seen: set[str],
    candidate: PureWindowsPath,
) -> None:
    key = str(candidate).casefold()
    if key not in seen:
        seen.add(key)
        candidates.append(candidate)


def bash_executable() -> str:
    if not _is_windows():
        return shutil.which("bash") or "bash"

    candidates: list[PureWindowsPath] = []
    seen: set[str] = set()
    in_git_bash = bool(os.environ.get("MSYSTEM"))

    for executable in ("bash.exe", "bash"):
        discovered = shutil.which(executable)
        if not discovered:
            continue
        candidate = PureWindowsPath(discovered)
        if _is_system_bash(candidate):
            continue
        root = _git_root_for_bash(candidate)
        if in_git_bash or (root is not None and _has_git_for_windows(root)):
            _append_candidate(candidates, seen, candidate)

    git = shutil.which("git.exe") or shutil.which("git")
    if git:
        git_path = PureWindowsPath(git)
        for root in git_path.parents:
            if root == PureWindowsPath(root.anchor):
                break
            for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
                _append_candidate(candidates, seen, root / relative)

    for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        program_files = os.environ.get(variable)
        if not program_files:
            continue
        root = PureWindowsPath(program_files) / "Git"
        for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
            _append_candidate(candidates, seen, root / relative)

    for candidate in candidates:
        if not _is_system_bash(candidate) and _exists(candidate):
            return str(candidate)
    raise RuntimeError("Git Bash no está disponible")


def bash_path(path: str | os.PathLike[str]) -> str:
    resolved = Path(path).resolve().as_posix()
    if _is_windows() and len(resolved) >= 3 and resolved[1:3] == ":/":
        return f"/{resolved[0].lower()}/{resolved[3:]}"
    return resolved


def _write_lf(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


@lru_cache(maxsize=1)
def _windows_python_shim() -> str:
    directory = Path(tempfile.mkdtemp(prefix="context-python-lf-"))
    atexit.register(shutil.rmtree, directory, ignore_errors=True)
    _write_lf(directory / "sitecustomize.py",
        "import sys\n"
        "for stream in (sys.stdout, sys.stderr):\n"
        "    if hasattr(stream, 'reconfigure'):\n"
        "        stream.reconfigure(newline='\\n')\n",
    )
    python3 = directory / "python3"
    _write_lf(python3,
        "#!/usr/bin/env bash\n"
        f"export PYTHONPATH={shlex.quote(str(directory))}\n"
        "export PYTHONUTF8=1\n"
        "export PYTHONIOENCODING=utf-8\n"
        f"exec {shlex.quote(bash_path(sys.executable))} \"$@\"\n",
    )
    python3.chmod(0o755)
    git_executable = shutil.which("git.exe") or shutil.which("git")
    if not git_executable:
        raise RuntimeError("Git no está disponible")
    git = directory / "git"
    _write_lf(git,
        "#!/usr/bin/env bash\n"
        "case \" $* \" in\n"
        "  *\" rev-parse --show-toplevel \"*)\n"
        f"    output=\"$({shlex.quote(bash_path(git_executable))} \"$@\")\"\n"
        "    status=$?\n"
        "    while [[ \"${output}\" == *$'\\r' || \"${output}\" == *$'\\n' ]]; do output=\"${output%?}\"; done\n"
        "    if [[ \"${output}\" =~ ^([A-Za-z]):/(.*)$ ]]; then\n"
        "      printf '/%s/%s\\n' \"${BASH_REMATCH[1],,}\" \"${BASH_REMATCH[2]}\"\n"
        "    else\n"
        "      printf '%s\\n' \"${output}\"\n"
        "    fi\n"
        "    exit \"${status}\"\n"
        "    ;;\n"
        "  *\" branch --show-current \"*)\n"
        f"    output=\"$({shlex.quote(bash_path(git_executable))} \"$@\")\"\n"
        "    status=$?\n"
        "    while [[ \"${output}\" == *$'\\r' || \"${output}\" == *$'\\n' ]]; do output=\"${output%?}\"; done\n"
        "    printf '%s\\n' \"${output}\"\n"
        "    exit \"${status}\"\n"
        "    ;;\n"
        "  *)\n"
        f"    exec {shlex.quote(bash_path(git_executable))} \"$@\"\n"
        "    ;;\n"
        "esac\n",
    )
    git.chmod(0o755)
    return bash_path(directory)


def bash_command(
    script: str | os.PathLike[str], *args: str | os.PathLike[str]
) -> list[str]:
    script_path = bash_path(script)
    arguments = [str(arg) for arg in args]
    if not _is_windows():
        return [bash_executable(), script_path, *arguments]
    return [
        bash_executable(),
        "-c",
        'export PATH="$1${PATH:+:$PATH}"; exec bash "$2" "${@:3}"',
        "context-test",
        _windows_python_shim(),
        script_path,
        *arguments,
    ]
