# SBM-Agent-Template v2.0.1

Canonical physical template for deterministic SBM agent materialization under `AGENT_CLONING_STANDARD v2.0.0`.

- Creation modes: `NEW`, `CLONE`.
- Supported migration type: `STANDARD_UPGRADE` through `AGENT_SPEC.migration_reference`; it is not a creation mode and is not clone semantics.
- The package contains exactly the 67 paths declared by `TEMPLATE.yaml.required_files`.
- `MANIFEST.yaml` inventories all 67 physical files. `CHECKSUMS.sha256` hashes exactly the other 66 files, including the final manifest.
- Deployment is separate from identity and is conditional in generated agents. The source template carries deployment templates and schema only.
- Validation: `python scripts/validate`.
- QA: `python scripts/test`.
- Deterministic ZIP normalization: ZIP_DEFLATED, compresslevel=6, lexicographic path order, UTF-8/LF content, mode 0644, fixed timestamp 2020-01-01 00:00:00 UTC and stable ZIP metadata.
- `context/agents/<Agent>/` is an operational versioned distribution registry, not the canonical identity source.
