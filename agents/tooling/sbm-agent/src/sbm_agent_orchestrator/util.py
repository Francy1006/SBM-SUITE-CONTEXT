from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

from .errors import OrchestratorError


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_object(value):
    return sha256_bytes(canonical_json(value))


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sortable_id(prefix=""):
    # ULID-class: wall-clock sortable prefix plus collision-resistant entropy.
    millis = int(time.time_ns() // 1_000_000)
    return f"{prefix}{millis:013x}{secrets.token_hex(10)}"


def normalize_brief(value):
    return re.sub(r"\s+", " ", value.strip())


def ensure_within(root, target):
    root = Path(root).resolve(strict=False)
    target = Path(target).resolve(strict=False)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise OrchestratorError("FORBIDDEN_WRITE", "Path escapes agents root", details={"path": str(target)}) from exc
    cursor = target
    while not cursor.exists() and cursor != root:
        cursor = cursor.parent
    if cursor.exists() and cursor.resolve(strict=True) != cursor.resolve(strict=False):
        resolved = cursor.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise OrchestratorError("FORBIDDEN_WRITE", "Symlink escapes agents root", details={"path": str(target)}) from exc
    return target


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    with tmp.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
