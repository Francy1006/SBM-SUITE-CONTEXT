from __future__ import annotations

import re

from .errors import OrchestratorError
from .util import atomic_write_json, read_json, sortable_id, utc_now


class IdentityAllocator:
    def __init__(self, store):
        self.store = store
        self.path = store.state / "identity-reservations.json"

    @staticmethod
    def canonicalize(requested_name):
        requested = re.sub(r"\s+", " ", requested_name.strip())
        requested = re.sub(r"\s+Agent$", "", requested, flags=re.IGNORECASE).strip()
        if not requested or not re.fullmatch(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 ._-]{0,79}", requested):
            raise OrchestratorError("INVALID_AGENT_NAME", "Requested agent name is invalid")
        display = " ".join(part[:1].upper() + part[1:] for part in requested.split()) + " Agent"
        slug = re.sub(r"[^A-Za-z0-9]+", "-", requested).strip("-")
        return f"{slug}-Agent", display

    def reserve(self, execution_id, requested_name, agent_version="1.0.0"):
        agent_id, agent_name = self.canonicalize(requested_name)
        with self.store.lock("identity-allocation"):
            ledger = read_json(self.path)
            registry = read_json(self.store.state / "final-agent-registry.json")
            if ledger is None or registry is None:
                raise OrchestratorError("CANONICAL_STATE_MISSING", "Identity allocation requires registry and reservation ledger")
            if any(a.get("agent_id") == agent_id and str(a.get("agent_version")) == str(agent_version) for a in registry.get("agents", [])):
                raise OrchestratorError("FINAL_REGISTRY_IDENTITY_CONFLICT", "Agent identity is already registered", details={"agent_id": agent_id})
            conflicts = [r for r in ledger["reservations"] if r["canonical_agent_id"] == agent_id and r["state"] not in ("RELEASED",)]
            if conflicts and all(r["execution_id"] != execution_id for r in conflicts):
                raise OrchestratorError("IDENTITY_CONFLICT", "Agent identity is already reserved", details={"agent_id": agent_id})
            existing = next((r for r in ledger["reservations"] if r["execution_id"] == execution_id), None)
            if existing:
                return existing
            sequence = ledger["next_sequence"]
            ledger["next_sequence"] += 1
            reservation = {
                "reservation_id": sortable_id("res_"),
                "execution_id": execution_id,
                "canonical_agent_id": agent_id,
                "canonical_agent_name": agent_name,
                "agent_version": agent_version,
                "sequence": sequence,
                "timestamp": utc_now(),
                "state": "RESERVED",
            }
            ledger["reservations"].append(reservation)
            ledger["revision"] += 1
            atomic_write_json(self.path, ledger)
            return reservation

    def set_state(self, reservation_id, state):
        if state not in ("RESERVED", "CONSUMING", "CONSUMED", "RELEASED"):
            raise OrchestratorError("INVALID_RESERVATION_STATE", "Invalid reservation state")
        with self.store.lock("identity-allocation"):
            ledger = read_json(self.path)
            reservation = next((r for r in ledger["reservations"] if r["reservation_id"] == reservation_id), None)
            if reservation is None:
                raise OrchestratorError("RESERVATION_NOT_FOUND", "Identity reservation does not exist")
            reservation["state"] = state
            ledger["revision"] += 1
            atomic_write_json(self.path, ledger)
            return reservation

    def conflicts(self, reservation):
        ledger = read_json(self.path); registry = read_json(self.store.state / "final-agent-registry.json")
        if ledger is None or registry is None: raise OrchestratorError("CANONICAL_STATE_MISSING", "Identity conflict check requires canonical state")
        return any(a.get("agent_id") == reservation["canonical_agent_id"] and str(a.get("agent_version")) == str(reservation["agent_version"]) for a in registry.get("agents", [])) or any(
            r["canonical_agent_id"] == reservation["canonical_agent_id"]
            and r["execution_id"] != reservation["execution_id"]
            and r["state"] != "RELEASED"
            for r in ledger["reservations"]
        )
