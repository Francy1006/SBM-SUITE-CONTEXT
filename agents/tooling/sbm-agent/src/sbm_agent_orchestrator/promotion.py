from __future__ import annotations

import os
import shutil
from pathlib import Path

from .errors import OrchestratorError
from .util import atomic_write_json, read_json, sha256_file, sortable_id, utc_now


class PromotionManager:
    def __init__(self, store, final_root=None):
        self.store = store
        self.final_root = Path(final_root or (store.agents_root / "final")).resolve(strict=False)
        try:
            self.final_root.relative_to(store.agents_root)
        except ValueError as exc:
            raise OrchestratorError("FORBIDDEN_WRITE", "Final registry root must be inside agents") from exc
        self.registry_path = store.state / "final-agent-registry.json"

    def _transaction_path(self, execution_id):
        return self.store.execution_dir(execution_id) / "promotion" / "transaction.json"

    def prepare(self, state, approval):
        candidate = Path(state["candidate_path"])
        if sha256_file(candidate) != approval["candidate_sha256"]:
            raise OrchestratorError("PROMOTION_BINDING_MISMATCH", "Promotion approval does not bind current candidate")
        destination = self.final_root / candidate.name
        transaction = {
            "promotion_transaction_id": sortable_id("promotion_"), "execution_id": state["execution_id"],
            "state": "PREPARED", "candidate_path": str(candidate), "candidate_sha256": approval["candidate_sha256"],
            "destination": str(destination), "reservation_id": state["identity"]["reservation_id"],
            "approval_event_sha256": approval["event_sha256"], "expected_registry": {
                "agent_id": state["identity"]["canonical_agent_id"], "agent_version": state["identity"]["agent_version"],
                "artifact_path": str(destination), "sha256": approval["candidate_sha256"], "execution_id": state["execution_id"],
            }, "created_at": utc_now(),
        }
        atomic_write_json(self._transaction_path(state["execution_id"]), transaction)
        return transaction

    def inspect_physical_state(self, tx):
        destination = Path(tx["destination"])
        registry = read_json(self.registry_path, {"revision": 0, "agents": []})
        registered = any(a.get("execution_id") == tx["execution_id"] for a in registry["agents"])
        artifact = destination.is_file() and sha256_file(destination) == tx["candidate_sha256"]
        if artifact and registered: return "COMMITTED"
        if artifact: return "ARTIFACT_APPLIED_REGISTRY_PENDING"
        if registered: return "REGISTRY_APPLIED_ARTIFACT_PENDING"
        return "NOT_APPLIED"

    def commit(self, tx, *, crash_at=None):
        path = self._transaction_path(tx["execution_id"])
        tx["state"] = "COMMITTING"; atomic_write_json(path, tx)
        if crash_at == "before_artifact":
            raise RuntimeError("injected crash before artifact promotion")
        self.final_root.mkdir(parents=True, exist_ok=True)
        destination = Path(tx["destination"])
        if destination.exists():
            if sha256_file(destination) != tx["candidate_sha256"]:
                tx["state"] = "FAILED_RECONCILABLE"; atomic_write_json(path, tx)
                raise OrchestratorError("PROMOTION_COLLISION", "Final artifact collision")
        else:
            staged = destination.with_name(f".{destination.name}.{tx['promotion_transaction_id']}.stage")
            shutil.copy2(tx["candidate_path"], staged)
            if sha256_file(staged) != tx["candidate_sha256"]:
                staged.unlink(missing_ok=True); raise OrchestratorError("PROMOTION_HASH_MISMATCH", "Staged artifact hash mismatch")
            os.replace(staged, destination)
        if crash_at == "after_artifact":
            raise RuntimeError("injected crash after artifact promotion")
        with self.store.lock("identity-allocation"):
            registry = read_json(self.registry_path)
            ledger = read_json(self.store.state / "identity-reservations.json")
            if registry is None or ledger is None: raise OrchestratorError("CANONICAL_STATE_MISSING", "Promotion requires registry and reservation ledger")
            reservation = next((r for r in ledger["reservations"] if r.get("reservation_id") == tx["reservation_id"]), None)
            if reservation is None or reservation.get("state") != "CONSUMING": raise OrchestratorError("RESERVATION_BINDING_INVALID", "Promotion reservation is not consuming")
            matches = [a for a in registry["agents"] if a.get("execution_id") == tx["execution_id"]]
            if not matches:
                if any(a.get("agent_id") == tx["expected_registry"]["agent_id"] and a.get("agent_version") == tx["expected_registry"]["agent_version"] for a in registry["agents"]):
                    raise OrchestratorError("REGISTRY_IDENTITY_CONFLICT", "Final identity already registered")
                registry["agents"].append(tx["expected_registry"]); registry["revision"] += 1; atomic_write_json(self.registry_path, registry)
            elif len(matches) > 1:
                raise OrchestratorError("DUPLICATE_REGISTRATION", "Execution registered more than once")
        if crash_at == "after_registry":
            raise RuntimeError("injected crash after registry mutation")
        tx["state"] = "COMMITTED"; tx["committed_at"] = utc_now(); atomic_write_json(path, tx)
        return tx

    def resume(self, execution_id):
        tx = read_json(self._transaction_path(execution_id))
        if not tx:
            raise OrchestratorError("PROMOTION_TRANSACTION_NOT_FOUND", "No promotion transaction exists")
        physical = self.inspect_physical_state(tx)
        if physical == "COMMITTED":
            tx["state"] = "COMMITTED"; atomic_write_json(self._transaction_path(execution_id), tx); return tx
        return self.commit(tx)
