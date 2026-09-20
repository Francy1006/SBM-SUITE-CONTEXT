import hashlib
import json

import pytest
import yaml

from sbm_agent_factory.authorization import verify_authorization
from sbm_agent_factory.errors import FactoryError


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path):
    execution_id = "exec-authorization"; reservation_id = "res-authorization"
    projection = tmp_path / "projection.json"; projection.write_text("{}\n")
    spec = tmp_path / "spec.yaml"; spec.write_text(yaml.safe_dump({"spec_id": "SPEC-X", "spec_version": "1.0.0"}))
    template = tmp_path / "template.zip"; template.write_bytes(b"template")
    event = {"execution_id": execution_id, "reservation_id": reservation_id, "prebuild_bundle_sha256": "a" * 64}; event["event_sha256"] = hashlib.sha256(canonical(event)).hexdigest(); event_path = tmp_path / "event.json"; event_path.write_text(json.dumps(event))
    authorization = {"contract": "FACTORY_AUTHORIZATION/v1", "execution_id": execution_id, "reservation_id": reservation_id, "prebuild_bundle_sha256": event["prebuild_bundle_sha256"], "approved_proposal_projection_sha256": digest(projection), "build_approval_event_sha256": event["event_sha256"], "spec_identity": {"spec_id": "SPEC-X", "spec_version": "1.0.0"}, "spec_sha256": digest(spec), "template_identity": {"template_id": "SBM-Agent-Template", "template_version": "2.0.1"}, "template_sha256": digest(template)}
    authorization["authorization_sha256"] = hashlib.sha256(canonical(authorization)).hexdigest(); authorization_path = tmp_path / "authorization.json"; authorization_path.write_text(json.dumps(authorization))
    return authorization, authorization_path, event_path, projection, spec, template, execution_id, reservation_id


def test_complete_authorization_passes(tmp_path):
    _, auth, event, projection, spec, template, execution_id, reservation_id = fixture(tmp_path)
    assert verify_authorization(auth, event, projection, spec, template, execution_id, reservation_id)["contract"] == "FACTORY_AUTHORIZATION/v1"


@pytest.mark.parametrize("field,value", [("execution_id", "wrong"), ("reservation_id", "wrong"), ("prebuild_bundle_sha256", "0" * 64), ("approved_proposal_projection_sha256", "0" * 64), ("build_approval_event_sha256", "0" * 64)])
def test_authorization_binding_mismatch_fails(tmp_path, field, value):
    authorization, auth, event, projection, spec, template, execution_id, reservation_id = fixture(tmp_path); authorization[field] = value; authorization.pop("authorization_sha256"); authorization["authorization_sha256"] = hashlib.sha256(canonical(authorization)).hexdigest(); auth.write_text(json.dumps(authorization))
    with pytest.raises(FactoryError, match="FACTORY_AUTHORIZATION_MISMATCH"):
        verify_authorization(auth, event, projection, spec, template, execution_id, reservation_id)
