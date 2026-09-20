# QA Test Matrix — generator-sbm-agent v2.0.0

Every normative gate is emitted by `scripts/test-package.js` only from the physical test that executed the behavior.

| Gate | Test file | Test case |
|---|---|---|
| GEN-SCHEMA-01 | tests/unit/prompt-mapping.test.js | Complete operational DRAFT_INPUT is schema-validated before canonical proposal construction. |
| GEN-SCHEMA-02 | tests/unit/prompt-mapping.test.js | Pinned canonical schema SHA-256 is exact. |
| GEN-SCHEMA-03 | tests/unit/prompt-mapping.test.js | Pinned canonical dialect is JSON Schema 2020-12. |
| GEN-SCHEMA-04 | tests/unit/dependency-metadata.test.js | Canonical Template SHA metadata is exact. |
| GEN-SCHEMA-05 | tests/unit/dependency-metadata.test.js | Pinned dependency closure is SELF_CONTAINED. |
| GEN-SCHEMA-06 | tests/unit/dependency-metadata.test.js | Ajv is pinned to 8.20.0 and imported from ajv/dist/2020. |
| GEN-SCHEMA-07 | tests/unit/dependency-metadata.test.js | YAML is pinned to 2.7.0. |
| GEN-SCHEMA-08 | tests/unit/draft-enforcement.test.js | Explicit namespace-sensitive values are validated before absent-only defaults; normalization audit preserves explicit values. |
| GEN-SCHEMA-09 | tests/unit/deterministic-proposal.test.js | Same valid input produces the same canonical proposal digest. |
| GEN-SCHEMA-10 | tests/unit/scaffold-metadata.test.js | Operational metadata/design intent never leaks into proposal output. |
| GEN-SCHEMA-11 | tests/integration/new-scaffold.test.js | Real Yeoman NEW produces canonical-valid proposal. |
| GEN-SCHEMA-12 | tests/integration/new-scaffold.test.js | Real Yeoman NEW produces parent_reference null. |
| GEN-SCHEMA-13 | tests/integration/clone-scaffold.test.js | Real Yeoman CLONE produces canonical-valid proposal. |
| GEN-SCHEMA-14 | tests/integration/clone-scaffold.test.js | Real Yeoman CLONE preserves exact/versioned parent reference. |
| GEN-SCHEMA-15 | tests/integration/non-interactive-new.test.js | Real config/non-interactive NEW rejects APPROVED/APROBABLE/CLONE explicit values before defaults and defaults absent status/mode. |
| GEN-SCHEMA-16 | tests/integration/non-interactive-clone.test.js | Real config/non-interactive CLONE rejects APPROVED/APROBABLE/NEW explicit values before defaults and defaults absent status/mode. |
| GEN-SCHEMA-17 | tests/unit/dependency-metadata.test.js | Trusted pinned conversion uses exact verified canonical bytes with maxAliasCount=-1; untrusted YAML remains maxAliasCount=100. |
| GEN-SCHEMA-18 | tests/separation/factory-convergence.test.js | Dedicated pinned path/provenance and exact SHA+size identity verification precede trusted conversion. |
| GEN-SCHEMA-19 | tests/separation/factory-convergence.test.js | REF_COUNT=0, unresolved=0, SELF_CONTAINED closure. |
| GEN-SCHEMA-20 | tests/negative/final-spec-generation.test.js | Real generation pipeline with one-byte-mutated TEST COPY reaches identity stage, returns DEPENDENCY_MISMATCH and leaves no FINAL/TEMP/LOCK. |
| GEN-SCHEMA-21 | tests/unit/deterministic-proposal.test.js | Real canonical validator cases cover type, required, additionalProperties, minLength, items, oneOf, enum, allOf/if/const/then. |
| GEN-SCHEMA-22 | tests/separation/factory-convergence.test.js | Alias-heavy noncanonical TEST COPY fails exact pinned identity before trusted conversion and leaves no FINAL/TEMP/LOCK. |
| GEN-ATOMIC-01 | tests/negative/scaffold-exists.test.js | Two real concurrent processes, same execution_id -> exactly one SUCCESS and one SCAFFOLD_EXISTS. |
| GEN-ATOMIC-02 | tests/negative/outside-build-write.test.js | Fault after first TEMP write and after second write before rename -> no FINAL/owned TEMP/owned LOCK. |

Additional config/non-interactive regression evidence covers six mandatory explicit-invalid cases and three absent-default cases. No explicit contractual value is replaced before validation.

## Yeoman domain-error adapter regression

| Gate | Test file | Test case |
|---|---|---|
| YEOMAN_DOMAIN_ERROR_ADAPTER | tests/integration/new-scaffold.test.js | Real yeoman-test intentional INVALID_INPUT preserves the full SBM domain error while the throwable exposes no textual `.code`. |
| CONTROLLED_INVALID_INPUT_REAL_GATE | tests/integration/new-scaffold.test.js | Physical `yo sbm-agent` intentional INVALID_INPUT exits numeric non-zero, emits no `ERR_INVALID_ARG_TYPE`, and leaves no scaffold/TEMP/LOCK. |

Adapter unit coverage is in `tests/unit/draft-enforcement.test.js`, including physically executed multi-category preservation for `INVALID_INPUT` and `UNSAFE_PATH`, strict `UNSAFE_PATH` assertions that adapted `code === undefined`, adapted `exitCode === undefined`, and adapted `message === domainError.message`, plus pass-through identity for unknown `ERR_TEST_RUNTIME` errors. Interactive CLONE adapter behavior is exercised in `tests/integration/clone-scaffold.test.js`; config/non-interactive tests recover the preserved domain error from the adapted Yeoman throwable.

<!-- SBM_CHECKLIST_269_FINAL_MAPPING -->
## Checklist 269 final ownership

- Physical CLI ownership for REAL_YEOMAN_NEW, REAL_YEOMAN_CLONE and CONTROLLED_INVALID_INPUT_REAL_GATE belongs exclusively to the independent candidate-aware external acceptance gate outside the Generator ZIP.
- yeoman-test remains independent evidence for GEN-SCHEMA-11..16, YEOMAN_TEST_IMPORT and PROMPTS_REAL_VIA_YEOMAN_TEST.
- GEN-SCHEMA-19 additionally requires REF_COUNT=0, UNRESOLVED_REF_COUNT=0, EXTERNAL_REF_COUNT=0 and SELF_CONTAINED.
- GEN-ATOMIC-01 requires two real processes plus winner-lock ownership barrier.
- GEN-ATOMIC-02 remains the two controlled TEMP-write fault injections.
- UNSAFE_PATH requires lexical plus build/scaffolds/final symlink escape cases.
- CWD and cleanup isolation are executable requirements.
- CEO_HARDCODED=false requires static productive scan plus runtime genericity comparison.
- QA schema injection must remain test-only and non-overridable through productive interfaces.
- Final acceptance requires the closed 71-ID external evidence set with zero pending, skipped, missing, duplicate or unknown required gates.
- The historical ce496 gate is immutable historical identity evidence only and is not authoritative for a new candidate SHA.

