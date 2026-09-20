# ACCEPTANCE CRITERIA

PASS only when all criteria are true:

- FACTORY_CONFIG validates and remains the source of Standard, Template, SHA, roots, compression and reproducibility policy.
- The physical canonical `SBM-Agent-Template-v2_0_1.zip` resolves only at the approved SHA-256.
- Template resolution validates root, TEMPLATE.yaml, TEMPLATE schema and physical references before rendering.
- NEW produces a complete Template-v2 agent workspace, validates it, packages it, and emits registry candidate plus execution evidence.
- CLONE resolves the exact parent, compares resolved contracts, rebuilds the target from the canonical Template, and rejects unapproved deltas.
- MATERIALIZATION approval targets the exact AGENT_SPEC id/version.
- STANDARD_UPGRADE is NEW, has explicit migration_reference, null parent references, and non-clone lineage.
- `validate` treats Factory packages and generated Agent v2 workspaces as distinct artifact classes.
- `package` revalidates the current Agent v2 workspace and rejects post-validation mutation before ZIP creation.
- Unit, integration, negative and E2E QA use the canonical Template dependency; E2E NEW/CLONE/UPGRADE produce full agent packages.
- Agent rebuild from extracted content is byte-identical under DEFLATE level 6.
- Factory package MANIFEST/CHECKSUMS cover the exact approved 68-file tree.
- No prohibited artifact is present.

- Generated `scripts/validate` performs real Agent-v2 contract validation and must exit 0.
- Generated `scripts/test` executes Agent-specific QA, not Template self-QA, and must exit 0.
- `qa_result: PASS` is permitted only when both generated agent commands actually executed and returned 0.
- `create`, `clone`, and `package` execute current Agent QA before final ZIP creation.
- A physical failing generated-agent test or invalid contract blocks package creation.

- Final `package` requires `--template`; no heuristic discovery or null Template contract is permitted.
- Final package resolves and SHA-validates the canonical Template, then derives agent required/conditional files from its physical contract.
- Regenerated MANIFEST/CHECKSUMS cannot hide a missing Template-required README, INIT, QA matrix, schema, or test.
