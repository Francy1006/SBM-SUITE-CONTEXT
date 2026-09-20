# SBM Agent Factory v1.0.1

Deterministic Python factory governed by `AGENT_CLONING_STANDARD v2.0.0` and canonical `SBM-Agent-Template v2.0.1` SHA-256 `f8f3901d23720d34e617a48f7a26956c34afe8fba73fc807eaaa6736323dd663`.

CLI: `sbm-agent create|clone|validate|test|package|docs`. Exit codes: 0 SUCCEEDED, 2 INVALID, 3 BLOCKED, 4 FAILED. Shell files are wrappers only. The structured source of truth is `config/FACTORY_CONFIG.yaml`.

Architecture separates build workspaces, distribution ZIPs, and `context/agents`; Factory produces registry candidates and evidence but never updates the official registry unilaterally. Packaging uses DEFLATE level 6, fixed ZIP timestamps, stable ordering and permissions, and byte-identical rebuild verification. Factory has no Yeoman/Node/npm dependency and normative logic defaults to NO_LLM_BY_DEFAULT.

Run QA with `sbm-agent test --root .` or `pytest -q tests`.

## Canonical Template consumption

Factory resolves the external `SBM-Agent-Template-v2_0_1.zip` by exact configured SHA-256, validates its root and `TEMPLATE.yaml` against `TEMPLATE.schema.yaml`, and materializes agents from its physical templates/schemas. The Template ZIP is not embedded in the Factory package.

`create` and `clone` produce complete Agent v2 workspaces, validate instances/cross-references/approvals, generate deterministic MANIFEST/CHECKSUMS and ZIP, then emit registry candidate and execution evidence outside the generated agent package. `package` revalidates the current Agent v2 workspace and rejects validate-then-mutate TOCTOU changes.
