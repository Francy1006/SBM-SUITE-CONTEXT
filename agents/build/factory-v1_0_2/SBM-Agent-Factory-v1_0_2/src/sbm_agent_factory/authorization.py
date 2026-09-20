import hashlib
import json
from pathlib import Path

import yaml

from .errors import blocked


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_authorization(authorization_path, build_event_path, projection_path, spec_path, template_path, execution_id, reservation_id):
    authorization = json.loads(Path(authorization_path).read_text(encoding="utf-8"))
    unsigned = dict(authorization); claimed = unsigned.pop("authorization_sha256", None)
    if authorization.get("contract") != "FACTORY_AUTHORIZATION/v1" or claimed != hashlib.sha256(_canonical(unsigned)).hexdigest():
        blocked("FACTORY_AUTHORIZATION_INVALID", "Orchestrator authorization hash is invalid")
    event = json.loads(Path(build_event_path).read_text(encoding="utf-8")); event_unsigned = dict(event); event_sha = event_unsigned.pop("event_sha256", None)
    spec = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    checks = {
        "execution_id": authorization.get("execution_id") == execution_id == event.get("execution_id"),
        "reservation_id": authorization.get("reservation_id") == reservation_id == event.get("reservation_id"),
        "prebuild_bundle_sha256": authorization.get("prebuild_bundle_sha256") == event.get("prebuild_bundle_sha256"),
        "approved_proposal_projection_sha256": authorization.get("approved_proposal_projection_sha256") == _sha(projection_path),
        "build_approval_event_sha256": authorization.get("build_approval_event_sha256") == event_sha == hashlib.sha256(_canonical(event_unsigned)).hexdigest(),
        "spec": authorization.get("spec_identity") == {"spec_id": spec.get("spec_id"), "spec_version": spec.get("spec_version")} and authorization.get("spec_sha256") == _sha(spec_path),
        "template": authorization.get("template_sha256") == _sha(template_path),
    }
    for field, valid in checks.items():
        if not valid: blocked("FACTORY_AUTHORIZATION_MISMATCH", f"Factory authorization mismatch: {field}")
    return authorization
