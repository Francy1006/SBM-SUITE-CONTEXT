# TEST MATRIX

| Requirement | Physical tests |
|---|---|
| Canonical Template ZIP resolve, exact SHA, root, TEMPLATE schema, templates/schemas | tests/unit/test_template_engine.py; tests/negative/test_template_sha_mismatch.py |
| Exact proposal/spec/materialization approvals | tests/unit/test_approvals.py; tests/negative/test_draft_blocked.py; tests/negative/test_approval_mismatch.py |
| Full NEW materialization from real Template v2 | tests/integration/test_create.py; tests/e2e/test_new_to_zip.py |
| Full CLONE reconstruction + resolved-contract COMPUTED_DELTA | tests/integration/test_clone.py; tests/e2e/test_clone_to_zip.py |
| STANDARD_UPGRADE via create with full invariants | tests/integration/test_standard_upgrade.py; tests/e2e/test_standard_upgrade_to_zip.py |
| Agent v2 validation without FACTORY_CONFIG | tests/e2e/test_new_to_zip.py; validation exercised by create/package |
| MANIFEST/CHECKSUMS agent integrity | tests/unit/test_manifest_checksums.py |
| Permissions/authority | tests/unit/test_permissions.py; tests/negative/test_permissions_invalid.py |
| Hierarchy | tests/unit/test_hierarchy.py; tests/negative/test_hierarchy_invalid.py |
| Relationships | tests/unit/test_relationships.py; tests/negative/test_relationships_invalid.py |
| Deployment conditionality | tests/integration/test_deployment_conditionality.py |
| Registry candidate only; no registry mutation | tests/integration/test_registry_candidate.py |
| Validate then mutate -> package rejection | tests/negative/test_extra_file.py; tests/negative/test_spec_mismatch.py |
| Prohibited artifacts / scaffold exclusion | tests/negative/test_prohibited_artifact.py |
| Standard/Template version mismatch | tests/negative/test_version_mismatch.py |
| Deterministic package + real generated-agent extract/rebuild | tests/unit/test_reproducibility.py; tests/e2e/test_rebuild_same_sha.py |

| Real generated-agent scripts/validate + scripts/test gate before package | tests/e2e/test_new_to_zip.py; tests/e2e/test_clone_to_zip.py; tests/e2e/test_standard_upgrade_to_zip.py |
| Physical failing agent test blocks package and qa_result cannot be PASS | tests/negative/test_spec_mismatch.py |
| Physical invalid agent contract makes generated scripts/validate nonzero | tests/negative/test_spec_mismatch.py |

| Final package requires explicit canonical Template contract | tests/negative/test_extra_file.py; tests/negative/test_template_sha_mismatch.py |
| Missing Template-required README/INIT/QA/schema/test blocks package even after valid MANIFEST/CHECKSUMS regeneration | tests/negative/test_extra_file.py |
| Conditional deployment presence/absence enforced by canonical Template contract | tests/integration/test_deployment_conditionality.py; package validation path |
