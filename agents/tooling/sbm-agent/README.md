# SBM Agent Creation Orchestrator 1.0.0

Operational entry point: `bin/sbm-agent`.

The CLI is an adapter over `sbm_agent_orchestrator.core.Orchestrator`; future API adapters use the same core. Runtime state is confined to `agents/runtime/sbm-agent`, with one workspace per execution, atomic JSON state, append-only NDJSON events, locks, immutable snapshots, isolated attempts, and promotion recovery.

Normal commands:

```text
sbm-agent create "<semantic brief>"
sbm-agent create
sbm-agent intake <execution_id> "<semantic response>"
sbm-agent import-response <execution_id> <external-response.json>
sbm-agent approve <execution_id>
sbm-agent status [<execution_id>]
sbm-agent resume <execution_id>
```

Bare `create` enters `CAPTURING_INTENT`. Free-form input is packaged for the configured Gepetto execution adapter; the deterministic accumulator accepts only a returned `STRUCTURED_INTENT_UPDATE`.

Multi-turn intake is accumulated in `INTENT_PROGRESS` with per-field provenance. Darwin `HUMAN_DECISION_REQUIRED` returns to that same execution, intent and identity reservation, then emits a newly hash-bound architecture request.

The workflow stops for an authenticated Darwin `SPEC_DECISIONS` submission and then for each Darwin/Noe review submission. The core validates reviewer identity and exact subject hashes and never synthesizes a verdict. API/reviewer adapters call `submit_spec_decisions` and `submit_review`; these are deliberately separate from the operator approval command.

The default routing mode is `MANUAL_CHAT`. Every route verifies agent ID/version, package SHA, a SHA-bound capability allowlist, request contract and response contract. Imported responses additionally require an `HMAC-SHA256/v1` provider attestation and one-use nonce; public response metadata is never authentication. The trusted key is supplied as hexadecimal through `SBM_AGENT_RESPONSE_ATTESTATION_KEY` and is not stored in the repository.

The historical Gepetto 1.0.0 package is intentionally bound to no intake capabilities because its physical contract prohibits inference and ambiguity resolution. Intake therefore fails closed until a separately governed intake-capable Gepetto version/package is activated; the historical ZIP is not relabeled or modified. Darwin and Noe retain only their explicitly listed architecture/review contracts.

`approve` fails closed unless the authenticated principal is `sbm-admin`. The published local configuration trusts the authenticated Unix owner of the `agents` authority root as `sbm-admin`, avoiding mutable runtime bootstrap files while keeping the principal outside command payloads.

The default adapters extract Generator and Factory from their pinned ZIPs into execution-local runtimes and byte-verify the complete trees before every invocation. Generator remains the sole DRAFT author. Factory 1.0.2 independently verifies `FACTORY_AUTHORIZATION/v1`; Factory 1.0.1 and all historical artifacts remain immutable. Promotion is a separate durable transaction.
