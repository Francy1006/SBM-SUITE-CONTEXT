from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from .errors import OrchestratorError
from .util import atomic_write_json, canonical_json, sha256_file, sha256_object, sortable_id, utc_now


def write_yaml(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")


def read_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


class ExternalIntentBriefContract:
    """Validates the approved Darwin intake handoff without interpreting it."""

    AUTHORIZED_INTAKE_MODE = "DARWIN_TEMPORARY_INTAKE"
    SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "contract", "requested_name", "desired_outcome", "semantic_complete",
            "unresolved_human_semantic_requirements", "provenance",
        ],
        "properties": {
            "contract": {"const": "INTENT_BRIEF/v1"},
            "requested_name": {"type": "string", "minLength": 1},
            "semantic_brief": {"type": "string"},
            "desired_outcome": {"type": "string", "minLength": 1},
            "specific_objectives": {"type": "array", "items": {"type": "string"}},
            "material_limits": {"type": "array"},
            "important_relationships": {"type": "array"},
            "style": {"type": ["string", "null"]},
            "responsibilities": {"type": ["array", "null"], "items": {"type": "string"}},
            "personality": {"type": ["string", "null"]},
            "communication_style": {"type": ["string", "null"]},
            "clarifications": {"type": "array"},
            "unresolved_human_semantic_requirements": {"const": []},
            "semantic_complete": {"const": True},
            "provenance": {
                "type": "object",
                "additionalProperties": True,
                "required": ["semantic_source", "intake_adapter", "intake_mode"],
                "properties": {
                    "semantic_source": {"const": "sbm-admin"},
                    "intake_adapter": {"const": "Darwin"},
                    "intake_mode": {"const": "DARWIN_TEMPORARY_INTAKE"},
                },
            },
        },
    }

    @classmethod
    def accept(cls, intent, *, intake_mode, principal):
        if intake_mode != cls.AUTHORIZED_INTAKE_MODE:
            raise OrchestratorError("INTAKE_ADAPTER_UNAUTHORIZED", "External intake adapter is not authorized")
        if principal != "sbm-admin":
            raise OrchestratorError("EXTERNAL_INTENT_SOURCE_UNAUTHORIZED", "External INTENT_BRIEF requires authenticated sbm-admin")
        errors = sorted(Draft202012Validator(cls.SCHEMA).iter_errors(intent), key=lambda error: list(error.path))
        if errors:
            error = errors[0]
            code = "INTENT_BRIEF_PROVENANCE_INVALID" if list(error.path)[:1] == ["provenance"] or error.validator == "required" and "provenance" in error.message else "INTENT_BRIEF_SCHEMA_INVALID"
            raise OrchestratorError(code, f"External INTENT_BRIEF schema is invalid: {error.message}", details={"path": list(error.path)})
        return copy.deepcopy(intent)


class IntentAccumulator:
    """Deterministically merges structured updates; it never interprets free-form text."""
    def accumulate(self, update, intake_state_view, current_progress=None, provenance=None):
        if update.get("contract") != "STRUCTURED_INTENT_UPDATE/v1" or not isinstance(update.get("fields"), dict): raise OrchestratorError("INTENT_UPDATE_INVALID", "A structured Gepetto intent update is required")
        policy = intake_state_view["field_source_policy"]; current = copy.deepcopy(current_progress or {"values": {}, "field_provenance": {}, "turns": []}); provenance = provenance or {}
        values = current.setdefault("values", {})
        field_provenance = current.setdefault("field_provenance", {})
        for field, value in update.get("fields", {}).items():
            if value not in (None, "", []):
                values[field] = value
                field_provenance.setdefault(field, []).append({"source": provenance.get("provider", "external-agent"), "request_sha256": provenance.get("request_sha256"), "response_sha256": sha256_object(update), "captured_at": utc_now()})
        current.setdefault("turns", []).append({"request_sha256": provenance.get("request_sha256"), "response_sha256": sha256_object(update), "captured_at": utc_now()})
        unresolved = []
        questions = policy.get("questions", {})
        for field, source in policy["fields"].items():
            if source == "SBM_ADMIN_REQUIRED" and not values.get(field):
                unresolved.append({"field": field, "question": questions.get(field, f"Necesito definir {field}.")})
            if source == "SBM_ADMIN_CONDITIONAL" and field in policy.get("conditional_required", []) and not values.get(field):
                unresolved.append({"field": field, "question": questions.get(field, f"Necesito definir {field}.")})
        intent = {
            "requested_name": values.get("requested_name"),
            "semantic_brief": values.get("semantic_brief", ""),
            "desired_outcome": values.get("desired_outcome"),
            "specific_objectives": [values["desired_outcome"]] if values.get("desired_outcome") else [],
            "material_limits": values.get("material_limits", []),
            "important_relationships": values.get("important_relationships", []),
            "style": values.get("style"),
            "responsibilities": values.get("responsibilities"),
            "personality": values.get("personality"),
            "communication_style": values.get("communication_style", values.get("style")),
            "clarifications": values.get("clarifications", []),
            "unresolved_human_semantic_requirements": unresolved,
            "semantic_complete": not unresolved,
            "intent_progress": current,
            "provenance": {
                "producer": provenance.get("principal_id"),
                "provider": provenance.get("provider"),
                "intake_state_view_sha256": sha256_object(intake_state_view),
                "captured_at": utc_now(),
            },
        }
        return intent


class DarwinSubmissionContract:
    """Validates authenticated Darwin output; it never derives Darwin decisions."""

    @staticmethod
    def request(intent, proposal, snapshot, intake_view, profile):
        request = {
            "contract": "DARWIN_ARCHITECTURE_REQUEST/v1",
            "intent_brief": copy.deepcopy(intent),
            "agent_proposal": copy.deepcopy(proposal),
            "creation_context": copy.deepcopy(snapshot),
            "intent_brief_sha256": sha256_object(intent),
            "agent_proposal_sha256": sha256_object(proposal),
            "creation_context_snapshot_sha256": snapshot["snapshot_sha256"],
            "relevant_relationships": intent.get("important_relationships", []),
            "governance": snapshot["governance"],
            "field_source_policy": profile["field_source_policy"],
            "intake_state_view_sha256": sha256_object(intake_view),
        }
        request["request_sha256"] = sha256_object(request)
        return request

    @staticmethod
    def accept(submission, request, principal, profile):
        if principal != "Darwin":
            raise OrchestratorError("WRONG_REVIEWER", "SPEC_DECISIONS must be submitted by authenticated Darwin")
        if submission.get("architecture_request_sha256") != request["request_sha256"]:
            raise OrchestratorError("DARWIN_SUBJECT_MISMATCH", "SPEC_DECISIONS do not bind the current architecture request")
        if submission.get("status") == "HUMAN_DECISION_REQUIRED":
            question = str(submission.get("question", "")).strip()
            if not question:
                raise OrchestratorError("DARWIN_SUBMISSION_INVALID", "A directed human question is required")
            return {"status": "HUMAN_DECISION_REQUIRED", "question": question}
        if submission.get("status") != "RESOLVED" or not isinstance(submission.get("decisions"), dict):
            raise OrchestratorError("DARWIN_SUBMISSION_INVALID", "Darwin submission must be RESOLVED or HUMAN_DECISION_REQUIRED")
        decisions = copy.deepcopy(submission["decisions"])
        governed = profile["field_source_policy"]["fields"]
        required = {name for name, source in governed.items() if source == "DARWIN_ARCHITECTURAL"}
        missing = sorted(required - set(decisions))
        if missing:
            raise OrchestratorError("DARWIN_SUBMISSION_INCOMPLETE", "Darwin architectural fields are missing", details={"fields": missing})
        decisions["submission"] = {
            "authenticated_principal": principal,
            "architecture_request_sha256": request["request_sha256"],
        }
        return {"status": "RESOLVED", "decisions": decisions}


class SpecCompiler:
    VERSION = "1.0.0"

    def compile(self, output_root, proposal, decisions, reservation, profile, approval_id):
        output_root = Path(output_root)
        aid = reservation["canonical_agent_id"]
        av = reservation["agent_version"]
        spec_id = f"SPEC-{aid}"
        spec_version = "1.0.0"
        refs = {
            "AGENT_DEFINITION": {"artifact_id": f"DEF-{aid}", "artifact_version": av},
            "AGENT_CONTEXT": {"artifact_id": aid, "artifact_version": av},
            "CONTEXT_CONTRACT": {"artifact_id": f"CTX-{aid}", "artifact_version": av},
            "RUNTIME_PROFILE": {"artifact_id": f"RUN-{aid}", "artifact_version": av},
            "CLONE_LINEAGE": {"artifact_id": f"LINEAGE-{aid}", "artifact_version": av},
            "PERMISSIONS": {"artifact_id": f"PERM-{aid}", "artifact_version": av},
            "HIERARCHY": {"artifact_id": aid, "artifact_version": av},
            "RELATIONSHIPS": {"artifact_id": f"REL-{aid}", "artifact_version": av},
        }
        deployment = decisions.get("deployment")
        deployment_enabled = isinstance(deployment, dict) and deployment.get("target") not in (None, "NONE")
        if deployment_enabled: refs["DEPLOYMENT_PROFILE"] = {"artifact_id": f"DEPLOY-{aid}", "artifact_version": av}
        spec = {
            "spec_id": spec_id, "spec_version": spec_version, "agent_id": aid, "agent_version": av,
            "standard_id": profile["bindings"]["standard"]["id"], "standard_version": profile["bindings"]["standard"]["version"],
            "template_id": profile["bindings"]["template"]["id"], "template_version": profile["bindings"]["template"]["version"],
            "proposal_reference": {"proposal_id": proposal["proposal_id"], "proposal_version": proposal["proposal_version"]},
            "component_references": refs,
            "qa_reference": {"artifact_id": aid, "artifact_version": av},
            "deployment_reference": refs.get("DEPLOYMENT_PROFILE"),
            "approval_reference": {"approval_id": approval_id, "artifact_version": spec_version},
            "migration_reference": None, "creation_mode": "NEW", "parent_reference": None,
        }
        definition = {
            "agent_definition_id": f"DEF-{aid}", "agent_definition_version": av, "agent_id": aid, "agent_version": av,
            "identity": reservation["canonical_agent_name"], "purpose": proposal["agent_purpose"], "role": "SPECIALIZED_AGENT",
            "description": proposal["agent_description"], "responsibilities": proposal["responsibilities"] + [f"OUTPUT:{value}" for value in decisions["outputs"]],
            "personality": proposal["personality"], "essential_behavior": ["DO_NOT_INFER", "NO_LLM_BY_DEFAULT"] + [f"QA:{value}" for value in decisions["qa"]],
            "communication_style": proposal["communication_style"], "authority": decisions["authority"],
            "essential_constraints": decisions["security_boundaries"],
        }
        agent_context = {
            "agent_id": aid, "agent_version": av, "context_version": av, "general_context": proposal["general_context"],
            "specific_objectives": proposal["specific_objectives"], "current_scope": [aid], "domain_context": "SBM-SUITE",
            "relevant_entities": [x.get("actor", str(x)) if isinstance(x, dict) else str(x) for x in decisions["relationships"]],
            "operational_assumptions": ["Canonical creation context snapshot is valid", "RUNTIME:" + canonical_json(decisions["runtime"]).decode("utf-8")], "context_sources": decisions["required_context"],
            "updated_at": "1980-01-01T00:00:00Z",
        }
        context_contract = {
            "context_contract_id": f"CTX-{aid}", "context_contract_version": av, "agent_id": aid,
            "context_zip_required": True, "required_context": decisions["required_context"], "optional_context": ["documentation.zip"],
            "retrieval_sources": ["SBM-SUITE"], "context_artifact_types": ["context.zip"], "context_validation_policy": "FULL_CURRENT_CONTEXT",
        }
        runtime_decisions = decisions["runtime"]
        runtime = {
            "runtime_profile_id": f"RUN-{aid}", "runtime_profile_version": av, "agent_id": aid,
            "execution_modes": decisions["execution_modes"], "context_delivery": runtime_decisions.get("context_delivery", "ZIP"), "retrieval_strategy": decisions["retrieval_strategy"],
            "embedding_strategy": decisions["embedding_strategy"], "llm_invocation_policy": "NO_LLM_BY_DEFAULT",
            "deterministic_capabilities": decisions["authority"], "asynchronous_capabilities": decisions["asynchronous_capabilities"],
            "scheduling_requirements": runtime_decisions.get("scheduling_requirements", ["NONE"]), "cost_control_policy": runtime_decisions.get("cost_control_policy", "NO_LLM_BY_DEFAULT"), "caching_policy": runtime_decisions.get("caching_policy", "DISABLED"),
            "idempotency_policy": runtime_decisions.get("idempotency", runtime_decisions.get("idempotency_policy", "REQUIRED")), "retry_policy": runtime_decisions.get("retry_policy", "NO_IMPLICIT_RETRY"), "timeout_policy": runtime_decisions.get("timeout_policy", "BOUNDED"),
            "concurrency_policy": runtime_decisions.get("concurrency_policy", "SERIAL"), "execution_dependencies": decisions["execution_dependencies"],
            "observability_requirements": runtime_decisions.get("observability_requirements", ["RESULT", "AUDIT_EVENT"]), "runtime_reference": ({"target": deployment["target"], "deployment_profile_id": f"DEPLOY-{aid}", "deployment_profile_version": av} if deployment_enabled else None),
        }
        permissions = {
            "permissions_id": f"PERM-{aid}", "permissions_version": av, "agent_id": aid,
            "allowed_actions": decisions["permissions"], "denied_actions": ["WRITE_STANDARD", "SELF_APPROVE", "PROMOTE_SELF"],
            "approval_required_actions": ["MATERIALIZE", "PROMOTE"], "escalation_rules": decisions["escalation_rules"],
        }
        hierarchy_decision = decisions["hierarchy"]
        hierarchy = {"agent_id": aid, "hierarchy_version": av, "reports_to": hierarchy_decision.get("reports_to", "sbm-admin"), "can_request_from": hierarchy_decision.get("can_request_from", ["Darwin", "Noe"]), "can_instruct": hierarchy_decision.get("can_instruct", []), "requires_approval_from": hierarchy_decision.get("requires_approval_from", ["sbm-admin"]), "escalation_target": hierarchy_decision.get("escalation_target", "sbm-admin")}
        normalized_relationships = []
        for item in decisions["relationships"]:
            if isinstance(item, dict) and {"actor", "relationship_type", "direction", "purpose"} <= set(item): normalized_relationships.append({key: item[key] for key in ("actor", "relationship_type", "direction", "purpose")})
            else:
                actor = item.get("agent_id", item.get("actor", "UNKNOWN")) if isinstance(item, dict) else str(item)
                normalized_relationships.append({"actor": actor, "relationship_type": "ARCHITECTURAL", "direction": "BIDIRECTIONAL", "purpose": "Darwin-approved relationship"})
        if not any(item["actor"] == "sbm-admin" for item in normalized_relationships): normalized_relationships.append({"actor": "sbm-admin", "relationship_type": "APPROVER", "direction": "INBOUND", "purpose": "Final human authority"})
        relationships = {
            "relationships_id": f"REL-{aid}", "relationships_version": av, "agent_id": aid,
            "relationships": normalized_relationships,
        }
        lineage = {
            "clone_lineage_id": f"LINEAGE-{aid}", "agent_id": aid, "agent_version": av, "is_clone": False,
            "clone_id": None, "parent_agent_id": None, "parent_agent_version": None, "parent_spec_id": None, "parent_spec_version": None,
        }
        artifacts = {
            "AGENT_SPEC.yaml": spec, "AGENT_DEFINITION.yaml": definition, "AGENT_CONTEXT.yaml": agent_context,
            "config/CONTEXT_CONTRACT.yaml": context_contract, "config/RUNTIME_PROFILE.yaml": runtime,
            "config/PERMISSIONS.yaml": permissions, "config/HIERARCHY.yaml": hierarchy,
            "config/RELATIONSHIPS.yaml": relationships, "config/CLONE_LINEAGE.yaml": lineage,
        }
        if deployment_enabled:
            artifacts["deployment/DEPLOYMENT_PROFILE.yaml"] = {"deployment_profile_id": f"DEPLOY-{aid}", "deployment_profile_version": av, "agent_id": aid, "agent_version": av, "target": deployment["target"], "enabled": bool(deployment.get("enabled", True))}
        for relative, value in artifacts.items():
            write_yaml(output_root / relative, value)
        return {name: sha256_file(output_root / name) for name in artifacts}

    @staticmethod
    def validate_schema(path, schema_path):
        obj = read_yaml(path); schema = read_yaml(schema_path)
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        if errors:
            raise OrchestratorError("SPEC_COMPILATION_INVALID", errors[0].message, details={"path": list(errors[0].path)})
        return True


class ReviewSubmissionContract:
    """Persists only an authenticated reviewer submission bound to exact subjects."""

    def accept(self, root, record_type, execution_id, expected_reviewer, expected_subjects, submission, principal):
        if principal != expected_reviewer:
            raise OrchestratorError("WRONG_REVIEWER", f"{record_type} requires authenticated {expected_reviewer}")
        if submission.get("subject_hashes") != expected_subjects:
            raise OrchestratorError("REVIEW_SUBJECT_MISMATCH", f"{record_type} does not bind the current subjects")
        verdict = submission.get("verdict")
        if verdict not in {"PASS", "FAIL"}:
            raise OrchestratorError("REVIEW_SUBMISSION_INVALID", "Review verdict must be PASS or FAIL")
        record = {
            "record_type": record_type, "execution_id": execution_id, "reviewer_identity": principal,
            "subject_hashes": copy.deepcopy(expected_subjects), "verdict": verdict,
            "submission_id": sortable_id("review_submission_"), "timestamp": utc_now(),
        }
        record["record_sha256"] = sha256_object(record)
        path = Path(root) / f"{record_type}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
        except FileExistsError as exc:
            raise OrchestratorError("REVIEW_ALREADY_SUBMITTED", f"{record_type} is immutable") from exc
        return record

    @staticmethod
    def valid(record, expected_subjects):
        copy_record = dict(record); claimed = copy_record.pop("record_sha256", None)
        return claimed == sha256_object(copy_record) and record["subject_hashes"] == expected_subjects and record["verdict"] == "PASS"


class ApprovalWriter:
    def write_build_approval(self, root, state, principal):
        execution_id = state["execution_id"]
        bundle_hash = state["prebuild_bundle_sha256"]
        decision_id = sortable_id("decision_")
        ids = state["reserved_approval_ids"]
        proposal = read_yaml(Path(root) / "prebuild" / "AGENT_PROPOSAL.yaml")
        spec = read_yaml(Path(root) / "prebuild" / "AGENT_SPEC.yaml")
        event = {
            "event_type": "BUILD_APPROVAL_EVENT", "human_decision_id": decision_id, "execution_id": execution_id,
            "reservation_id": state["identity"]["reservation_id"],
            "prebuild_bundle_sha256": bundle_hash, "build_context_snapshot_sha256": state["build_context_snapshot_sha256"],
            "authenticated_principal": principal.principal_id, "authentication_provider_method": principal.provider,
            "authentication_session_reference": principal.session_reference, "authentication_timestamp": principal.authenticated_at,
            "proposal_identity": {"proposal_id": proposal["proposal_id"], "proposal_version": proposal["proposal_version"]},
            "proposal_sha256": sha256_file(Path(root) / "prebuild/AGENT_PROPOSAL.yaml"),
            "spec_identity": {"spec_id": spec["spec_id"], "spec_version": spec["spec_version"]},
            "spec_sha256": sha256_file(Path(root) / "prebuild/AGENT_SPEC.yaml"),
            "decision_timestamp": utc_now(), "timestamp": utc_now(),
            "approval_ids": ids,
        }
        event["event_sha256"] = sha256_object(event)
        atomic_write_json(Path(root) / "BUILD_APPROVAL_EVENT.json", event)
        approved = copy.deepcopy(proposal); approved["review_status"] = "APPROVED"
        approved_path = Path(root) / "approved" / "AGENT_PROPOSAL.yaml"
        write_yaml(approved_path, approved)
        projection = {
            "original_proposal_sha256": sha256_file(Path(root) / "prebuild" / "AGENT_PROPOSAL.yaml"),
            "approved_proposal_sha256": sha256_file(approved_path), "human_decision_id": decision_id,
            "proposal_approval_id": ids["proposal"], "prebuild_bundle_sha256": bundle_hash, "review_status": "APPROVED",
        }
        atomic_write_json(Path(root) / "approved" / "APPROVED_PROPOSAL_PROJECTION.json", projection)
        projection_sha = sha256_file(Path(root) / "approved/APPROVED_PROPOSAL_PROJECTION.json")
        authorization = {
            "contract": "FACTORY_AUTHORIZATION/v1", "execution_id": execution_id,
            "reservation_id": state["identity"]["reservation_id"], "prebuild_bundle_sha256": bundle_hash,
            "approved_proposal_projection_sha256": projection_sha, "build_approval_event_sha256": event["event_sha256"],
            "spec_identity": event["spec_identity"], "spec_sha256": event["spec_sha256"],
            "template_identity": state["template_identity"], "template_sha256": state["template_sha256"],
        }
        authorization["authorization_sha256"] = sha256_object(authorization)
        atomic_write_json(Path(root) / "approved/FACTORY_AUTHORIZATION.json", authorization)
        records = {
            "PROPOSAL_APPROVAL.yaml": (ids["proposal"], "AGENT_PROPOSAL", proposal["proposal_id"], proposal["proposal_version"]),
            "SPEC_APPROVAL.yaml": (ids["spec"], "AGENT_SPEC", spec["spec_id"], spec["spec_version"]),
            "MATERIALIZATION_APPROVAL.yaml": (ids["materialization"], "MATERIALIZATION", spec["spec_id"], spec["spec_version"]),
        }
        for filename, (approval_id, approval_type, artifact_id, artifact_version) in records.items():
            write_yaml(Path(root) / "approved" / filename, {
                "approval_id": approval_id, "approval_type": approval_type, "approved_by": principal.principal_id,
                "approved_at": event["timestamp"], "artifact_id": artifact_id, "artifact_version": artifact_version,
                "approval_status": "APPROVED",
            })
        return event

    def write_promotion_approval(self, root, state, principal):
        binding = {
            "event_type": "PROMOTION_APPROVAL_EVENT", "human_decision_id": sortable_id("decision_"),
            "execution_id": state["execution_id"], "agent_id": state["identity"]["canonical_agent_id"],
            "agent_version": state["identity"]["agent_version"], "candidate_sha256": state["candidate_sha256"],
            "qa_evidence_sha256": state["qa_evidence_sha256"], "darwin_review_sha256": state["darwin_final_review_sha256"],
            "noe_review_sha256": state["noe_final_review_sha256"], "registry_candidate_sha256": state["registry_candidate_sha256"],
            "authenticated_principal": principal, "timestamp": utc_now(),
        }
        binding["event_sha256"] = sha256_object(binding)
        atomic_write_json(Path(root) / "PROMOTION_APPROVAL_EVENT.json", binding)
        return binding
