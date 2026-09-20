from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path

from .errors import OrchestratorError
from .util import atomic_write_json, ensure_within, read_json, sha256_object, sortable_id, utc_now


class RuntimeStore:
    def __init__(self, agents_root, runtime_root):
        self.agents_root = Path(agents_root).resolve(strict=False)
        self.root = ensure_within(self.agents_root, runtime_root)
        self.executions = self.root / "executions"
        self.locks = self.root / ".locks"
        self.state = self.root / "canonical-state"
        for path in (self.root, self.executions, self.locks, self.state):
            path.mkdir(parents=True, exist_ok=True)
        self.bootstrap_canonical_state()

    def bootstrap_canonical_state(self):
        """Explicit, locked first-use bootstrap; normal reads remain fail-closed."""
        marker = self.state / "BOOTSTRAP.json"
        with self.lock("canonical-bootstrap"):
            required = {
                "final-agent-registry.json": {"revision": 0, "agents": []},
                "identity-reservations.json": {"revision": 0, "next_sequence": 1, "reservations": []},
            }
            existing = [self.state / name for name in required]
            if marker.exists():
                if not all(path.is_file() for path in existing):
                    raise OrchestratorError("CANONICAL_STATE_MISSING", "Bootstrapped canonical state is incomplete")
                return
            if any(path.exists() for path in existing) and not all(path.is_file() for path in existing):
                raise OrchestratorError("CANONICAL_STATE_RECOVERY_REQUIRED", "Partial canonical state requires explicit recovery")
            for name, value in required.items():
                if not (self.state / name).exists(): atomic_write_json(self.state / name, value)
            atomic_write_json(marker, {"contract": "CANONICAL_STATE_BOOTSTRAP/v1", "created_at": utc_now()})

    def safe(self, *parts):
        return ensure_within(self.root, self.root.joinpath(*parts))

    @contextmanager
    def lock(self, name):
        path = self.safe(".locks", f"{name}.lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def execution_dir(self, execution_id):
        if not execution_id or "/" in execution_id or ".." in execution_id:
            raise OrchestratorError("INVALID_EXECUTION_ID", "Unsafe execution id")
        return self.safe("executions", execution_id)

    def state_path(self, execution_id):
        return self.execution_dir(execution_id) / "state.json"

    def load_execution(self, execution_id):
        state = read_json(self.state_path(execution_id))
        if state is None:
            raise OrchestratorError("EXECUTION_NOT_FOUND", "Execution does not exist", details={"execution_id": execution_id})
        return state

    def save_execution(self, state):
        atomic_write_json(self.state_path(state["execution_id"]), state)

    def create_execution(self, state):
        root = self.execution_dir(state["execution_id"])
        try:
            root.mkdir(parents=True, exist_ok=False)
        except FileExistsError as exc:
            raise OrchestratorError("EXECUTION_COLLISION", "Execution id collision") from exc
        self.save_execution(state)

    def append_event(self, execution_id, actor, action, *, inputs=None, outputs=None, attempt_id=None, details=None):
        event = {
            "event_id": sortable_id("evt_"),
            "execution_id": execution_id,
            "actor": actor,
            "action": action,
            "input_hashes": inputs or {},
            "output_hashes": outputs or {},
            "attempt_id": attempt_id,
            "timestamp": utc_now(),
            "details": details or {},
        }
        path = self.execution_dir(execution_id) / "events.ndjson"
        line = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def write_immutable(self, execution_id, relative, value):
        path = ensure_within(self.execution_dir(execution_id), self.execution_dir(execution_id) / relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        try:
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise OrchestratorError("IMMUTABLE_ARTIFACT_EXISTS", "Immutable artifact already exists", details={"path": relative}) from exc
        return path, sha256_object(value)

    def transition(self, state, new_state, actor="orchestrator", details=None):
        old = state["state"]
        state["state"] = new_state
        state["updated_at"] = utc_now()
        self.save_execution(state)
        self.append_event(state["execution_id"], actor, "STATE_TRANSITION", details={"from": old, "to": new_state, **(details or {})})
        return state
