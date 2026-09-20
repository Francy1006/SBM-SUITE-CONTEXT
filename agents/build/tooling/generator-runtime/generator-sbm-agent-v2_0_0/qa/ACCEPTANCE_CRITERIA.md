# Acceptance Criteria — generator-sbm-agent v2.0.0

- Package tree contains exactly the 45 declared physical files; MANIFEST contains 45 entries and CHECKSUMS contains 44 hashes.
- `schemas/DRAFT_INPUT.schema.yaml` remains the generator-owned operational input contract and is physically distinct from the pinned canonical output snapshot.
- Raw capture, absent-only defaulting, validated input and proposal output are distinct stages.
- Explicit `review_status` values other than `DRAFT` and namespace-conflicting explicit `creation_mode` values fail with `INVALID_INPUT` before defaults.
- Defaults apply only when the property is absent: review_status -> DRAFT; NEW namespace creation_mode -> NEW; CLONE namespace creation_mode -> CLONE. Operational defaults are also absent-only and explicit values are preserved to the schema gate.
- Six config/non-interactive negative cases produce INVALID_INPUT with no scaffold; the three required absent-default positive cases execute through the same config/non-interactive generation route when exact runtime dependencies are available.
- Proposal output is validated separately against the pinned canonical schema before any scaffold commit.
- GEN-SCHEMA-20 and GEN-SCHEMA-22 use an internal QA-only schema seam through the real generation pipeline; the production CLI/config/prompt surface cannot override the pinned canonical schema.
- GEN-SCHEMA-20 must reach `PINNED_SCHEMA_IDENTITY_CHECK`, return DEPENDENCY_MISMATCH and leave FINAL absent with zero owned TEMP/LOCK residuals.
- GEN-SCHEMA-22 must reject alias-heavy/noncanonical schema bytes at `PINNED_SCHEMA_IDENTITY_CHECK` with DEPENDENCY_MISMATCH before trusted conversion, leaving FINAL absent with zero owned TEMP/LOCK residuals.
- Ajv is exactly 8.20.0 using Ajv2020 from `ajv/dist/2020`; YAML is exactly 2.7.0. All approved Ajv/YAML options are explicit and no fallback/remote schema resolution/data mutation is used.
- `GEN-SCHEMA-01..22` and `GEN-ATOMIC-01..02` each have exactly one physical gate mapping with test file, executed test case and result.
- Candidate-internal QA may report environment unavailability as supporting evidence only; authoritative final acceptance may not convert unavailable runtime gates into PASS.
- Final acceptance is owned by an independent candidate-aware gate outside the Generator ZIP, bound to explicit candidate SHA at start and closure. The historical ce496 gate is identity/integrity evidence only for its historical artifact.
- Authoritative final accounting is exactly 71 PASS, 0 FAIL, 0 SKIPPED and 0 PENDING.
- Package ZIP is deterministic: DEFLATE level 6, timestamp 1980-01-01, lexical ordering, scripts 0755, general files 0644, directories 0755; generation A/B/delivered/rebuild must be byte-identical.

- The SBM domain error contract remains `code/message/path/details`; its textual taxonomy is unchanged.
- At the Yeoman boundary only, controlled SBM domain errors are adapted to a throwable without a textual `.code`; the complete original domain error remains recoverable from the adapted throwable.
- Unknown/programming/runtime errors are not wrapped or reclassified by the adapter.
- Interactive NEW, interactive CLONE, config/non-interactive and yeoman-test all traverse the same `makeYeomanClass` boundary adapter. Physical `yo sbm-agent` INVALID_INPUT regression requires a numeric non-zero exit, no `ERR_INVALID_ARG_TYPE`, no secondary TypeError and no FINAL/TEMP/LOCK residual.
- QA fixtures use v2 DRAFT_INPUT types (`permissions` and `relationships` arrays; `hierarchy` a deliberate semantic string); no v1 fixture compatibility coercion is introduced.
- Adapter unit QA must physically cover at least two distinct known SBM categories (`INVALID_INPUT` and `UNSAFE_PATH`) through the same production `operationalError -> adapt -> recover` flow; for `UNSAFE_PATH`, adapted `code` and `exitCode` must be exactly `undefined` and adapted `message` must exactly equal the domain error message; unknown runtime errors must remain pass-through by identity.

<!-- SBM_CHECKLIST_269_FINAL_ACCEPTANCE -->
## Checklist 269 final acceptance additions

Required physical evidence includes:

- build symlink escape -> UNSAFE_PATH
- build/scaffolds symlink escape -> UNSAFE_PATH
- FINAL symlink escape -> UNSAFE_PATH
- regular preexisting FINAL -> SCAFFOLD_EXISTS with byte preservation
- real lock ownership barrier
- no partial scaffold on controlled failures
- exact two-file NEW and CLONE output
- QA schema seam is not productively overridable
- CWD isolation
- cleanup isolation
- CEO_HARDCODED=false by static and runtime semantic comparison
- exact Yeoman dependency versions
- real physical CLI NEW and CLONE owned by the definitive external harness
- zero pending/skipped/missing/duplicate/unknown required gates
- evidence bound to exact final candidate SHA and exact external harness SHA
