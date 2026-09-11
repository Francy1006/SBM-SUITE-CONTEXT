# ACCEPTANCE CRITERIA — SBM-Agent-Template v2.0.1

Acceptance is binary. QA-TEMPLATE-01 through QA-TEMPLATE-26 and executable QA-SEPARATION-01 through QA-SEPARATION-05 must all PASS.

`scripts/validate` must return `VALID`, meaning PHYSICAL_INTEGRITY + SCHEMA_CONFORMANCE + INSTANCE_CONFORMANCE + CROSS_REFERENCE_CONFORMANCE. `TEMPLATE.yaml` must conform to the complete `schemas/TEMPLATE.schema.yaml`, including canonical root, conditional groups, prohibited patterns, and all physical schema/template/QA/fixture references.

Any mismatch is INVALID.

QA-TEMPLATE-12 is accepted only when canonical packaging uses DEFLATE/compresslevel=6 and generation A, generation B, the supplied delivered ZIP (when provided), and rebuild-from-extracted-content are byte-identical with equal SHA-256.
