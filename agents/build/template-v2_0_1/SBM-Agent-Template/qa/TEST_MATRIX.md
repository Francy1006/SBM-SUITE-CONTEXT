# TEST MATRIX — SBM-Agent-Template v2.0.1

QA-TEMPLATE-01..26 are executable in `tests/` and must all PASS.

`tests/test_separation.py` contains the deterministic QA-only harness for QA-SEPARATION-01..05. It performs real attempted materialization, approval-path rejection, physical package inspection, provisional registry-candidate rejection, and byte-identical canonical-output comparison. The harness is test-only and is not SBM Agent Factory or generator-sbm-agent.

`test_instance_validation.py` validates complete fixture instances against exact schemas. `test_cross_references.py` validates exact IDs/versions and compatibility rules. `test_standard_upgrade.py` validates real STANDARD_UPGRADE invariants.

QA-TEMPLATE-12 uses ZIP_DEFLATED with compresslevel=6 and fixed ZIP metadata. It asserts generation A == generation B, optionally asserts generation A == the physical delivered ZIP supplied through `SBM_DELIVERED_ZIP`, then extracts that delivered artifact and rebuilds it from extracted content, requiring byte-identical equality and the same SHA-256.
