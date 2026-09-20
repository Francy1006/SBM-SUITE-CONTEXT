# generator-sbm-agent v2.0.0

Deterministic Yeoman capture/scaffolding layer for SBM agent proposals. It creates DRAFT scaffolds only and has no authority to approve or materialize final agents.

## Contract separation

- `schemas/DRAFT_INPUT.schema.yaml`: generator-owned operational input contract.
- `schemas/pinned/SBM-Agent-Template-v2_0_0/AGENT_PROPOSAL.schema.yaml`: immutable pinned snapshot used only to validate canonical proposal output.
- Source of truth for the pinned snapshot remains `SBM-Agent-Template-v2_0_0.zip` SHA-256 `c0ad9729f21b31f5ef859f60169691c9eacee5cda0accc7abb130e954488d272`.
- Pinned schema SHA-256: `cac183a89c78224dce6739f77ccbb081849c69f2f1137c0a0b587c6d7d3d0cd5`, size 2290, self-contained.

## Validation pipeline

RAW INPUT -> DRAFT_INPUT schema validation -> generator semantic rules -> proposal construction -> pinned schema identity -> YAML 1.2 initialization -> Ajv2020 canonical output validation -> scaffold metadata validation -> atomic TEMP/LOCK/rename commit.

Ajv is exactly 8.20.0; YAML is exactly 2.7.0. The generator does not use remote schema resolution, fallback validators or data mutation.

## Atomicity

Each execution stages within `build/scaffolds/`, acquires `.lock-<execution_id>` via exclusive `wx`, writes an owned TEMP directory on the same filesystem, then publishes with rename. Cleanup removes only owned resources. v2 provides namespace/process atomicity; crash durability and stale-lock recovery are not promised.

## Scope

Outputs only `build/scaffolds/<execution_id>/AGENT_PROPOSAL.yaml` and `.sbm/scaffold.json`. It does not produce approvals, AGENT_SPEC, AGENT_DEFINITION, final agent ZIP, registry/context/dist writes, or invoke Factory automatically.

## Acceptance authority

Internal package QA is supporting implementation evidence only. Final acceptance is owned by the independent external candidate-aware gate at the tooling/governance layer; that gate is not packaged inside this Generator ZIP. The immutable historical ce496 gate remains historical identity evidence only.

Authoritative final acceptance binds an explicit candidate path and SHA-256 at gate start and closure and requires the closed 71-gate set to finish with 71 PASS, 0 FAIL, 0 SKIPPED and 0 PENDING. A candidate-internal PASS string is never sufficient external acceptance evidence.
