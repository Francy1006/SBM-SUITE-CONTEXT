# ☸️ DevOps & Platform Engineering

> **Last updated:** 2026-08-12
>
> **Purpose:**
>
> Define the validated DevOps and Platform Engineering operating model for SBM Suite, including the lifecycle-aware context, QA and final documentation workflows used by `dp-api`.
>
> **Source of truth:**
>
> `DP-API` Git repository, `SBM-SUITE/context`, finalized project contexts, executed QA evidence, workflow scripts and the reviewed documentation package.

## 1. Overview

SBM Suite uses repository-based automation to manage explicit objective lifecycle phases, collect implementation and QA evidence, retrieve context and documentation from separate Qdrant collections, and apply reviewed upgrades through separate context and documentation workflows.

For `dp-api`, the `DP-QA-001` closure establishes a pre-development context cycle, an implementation-progress cycle, a validated closure cycle and a final documentation cycle.

## 2. Scope

This page covers:

- Docker-based local execution;
- explicit context lifecycle phases and objective identifiers;
- published contract validation through `GET /contexts/contract`;
- Git and QA evidence collection;
- context deployment and upgrade;
- documentation deployment and upgrade;
- Qdrant collection separation;
- ZIP manifests, authorized paths and SHA-256 validation;
- shared backups, atomic replacement and rollback;
- current validation boundaries.

It does not certify production deployment, cloud or Kubernetes execution, tenant isolation, object permissions, database compatibility, migration execution or Notion synchronization.

## 3. Current state

The supplied Git evidence for the current closure identifies changes in:

- `context/PROJECT_CONTEXT.md`;
- `context/QA_CONTEXT.md`.

The evidence-based QA procedure and lifecycle-aware context workflow covered by `DP-QA-001` remain implemented and closed.

For `DP-TEST-001`, the current evidence supports a lifecycle-only/no-op closure: the objective was removed from the project active-objective section and project QA context now records explicit closure evidence. No source-code, runtime, API, database or other implementation change is evidenced or claimed for this objective.

Validated lifecycle state from current global Context:

| Objective ID | Project | Status | Validation |
|---|---|---|---|
| DP-QA-001 | DP-API | completed | Historical closure evidence records the completed QA procedure and its validated scope. |
| DP-TEST-001 | DP-API | completed | Lifecycle-only/no-op closure with current QA evidence; no implementation-state change claimed. |
| OBJ-CTX-013 | SBM-SUITE | completed | Context closure evidence confirms the centralized Context/Documentation workflow, exact lifecycle dispatch, global reconciliation, stale-output handling and structured QA `not-applicable` support. |

Current workflow behavior includes:

- explicit `planning-activation`, `implementation-progress` and `implementation-closure` phases;
- a mandatory `objective_id` for every context export;
- a literal user prompt requirement for `planning-activation`;
- context contract preflight before shared exchange cleanup;
- bounded QA evidence persisted to `context/qa-results.md`;
- client-side ZIP manifest and physical-patch preflight before backend context upgrade;
- mandatory project/global objective and QA synchronization during closure;
- final documentation deployment only after successful QA and context closure.

The current documentation deployment completed for `dp-api`, indexed `28` documentation sources and `3390` chunks in `sbm_documentation`, and reported no errors.

Executed QA evidence generated on `2026-08-07` records `65` collected and passed tests, `0` failures, `88%` total configured pytest coverage, successful `coverage.xml` generation, SonarScanner exit code `0`, `ANALYSIS SUCCESSFUL`, `EXECUTION SUCCESS`, server-side Quality Gate `OK` and `40` indexed Python files.

## 4. Core concepts

- **Explicit lifecycle:** the requested context phase is supplied by the workflow caller and is never inferred from Git, QA or current context state.
- **Published contract:** context clients validate the backend contract version, supported phases, canonical project path and supported patch paths before export or upgrade.
- **Git source of truth:** repository content and Git evidence define the current manual workflow state.
- **Context workflow:** maintains project and global operational context independently from documentation.
- **Completed-objective history:** completed objectives are removed from operational tables and recorded only in the global completed-objectives register.
- **Documentation workflow:** supports planning-only roadmap updates for `active` or `pending` objectives and implemented-state updates only after validated closure.
- **Protected contracts:** `SYS_PROMPT.md` and `FORMAT_CONTEXT.md` guide generation but are not upgrade outputs.
- **Authorized paths:** upgrades may affect only existing files explicitly included in the package allowlist.
- **Single backup root:** successful context and documentation upgrades use `SBM-SUITE/context/backup/`.
- **Atomic replacement:** validated files are backed up and replaced as one controlled operation, with rollback on application failure.
- **Evidence-first generation:** unsupported claims are omitted rather than inferred.
- **Lifecycle-only/no-op closure:** an objective may be validated and closed without an implementation-state claim when current evidence explicitly shows no implementation change and QA validates the current project state.

## 5. Architecture or operating model

```text
Objective assignment
→ context-deploy planning-activation
→ reviewed context-upgrade
→ implementation
→ qa-check.sh
→ context-deploy implementation-progress or implementation-closure
→ reviewed closing context-upgrade
→ documentation-deploy
→ LLM-generated documentation-upgrade.zip
→ documentation-upgrade
→ shared backup and atomic replacement
```

| Component | Project | Responsibility | Technology | Runtime | Owner | Status |
|---|---|---|---|---|---|---|
| Context deploy | `DP-API` / `sbm-ai-assistant` | Validate the published contract and package explicitly phased context evidence | Bash, Python, FastAPI, Qdrant, ZIP | Docker | SBM Suite | active |
| Context upgrade | `DP-API` / `sbm-ai-assistant` | Preflight and apply authorized lifecycle-aware context section updates | Bash, Python, FastAPI | Docker | SBM Suite | active |
| QA evidence workflow | `DP-API` | Run configured pytest, coverage and SonarScanner checks and persist bounded evidence | Bash, pytest, pytest-cov, SonarScanner | Docker | DP-API | active |
| Documentation deploy | `DP-API` / `sbm-ai-assistant` | Index documentation and build a final-state documentation evidence package after closure | Bash, Python, FastAPI, Qdrant, ZIP | Docker | SBM Suite | active |
| Documentation upgrade | `DP-API` / `sbm-ai-assistant` | Validate and replace complete authorized Markdown files | Bash, Python, FastAPI | Docker | SBM Suite | active |
| Context collection | Qdrant | Store active context chunks | `sbm_contexts` | Docker | SBM Suite | active |
| Documentation collection | Qdrant | Store active documentation chunks | `sbm_documentation` | Docker | SBM Suite | active |

| Source | Target | Contract | Data | Authentication | Purpose | Status |
|---|---|---|---|---|---|---|
| DP-API workflow client | `GET /contexts/contract` | Published context contract | Contract version, lifecycle phases, canonical projects and supported patch paths | Internal service access | Block incompatible context export and upgrade operations | active |
| Git repository | Deploy workflow | Repository paths and workflow request | Diff, changed files, log, QA and global tree evidence | Local workflow access | Build evidence packages | active |
| Documentation deploy | Qdrant | Documentation indexing contract | Markdown chunks | Internal service access | Retrieve relevant documentation | active |
| Context deploy | Qdrant | Context indexing contract | Context chunks | Internal service access | Retrieve relevant context | active |
| Context upgrade | Context targets | Manifest, phase, hashes, target mappings and authorized patches | Section-level context operations | Local workflow access | Apply validated context state transitions | active |
| Documentation upgrade | Documentation root | Manifest, hashes and authorized existing paths | Complete Markdown replacements | Local workflow access | Apply validated final documentation updates | active |

| ADR ID | Decision | Status | Consequences | Projects | Reference |
|---|---|---|---|---|---|
| N/A | Keep context and documentation workflows separate | accepted | Prevents documentation upgrades from modifying context files and vice versa | SBM Suite | `FORMAT_CONTEXT.md` |
| N/A | Use explicit context lifecycle phases instead of inferred phases | accepted | Planning, implementation progress and closure remain distinguishable and independently validated | DP-API, SBM Suite | `context/DEPLOY_CONTEXT.md` |
| N/A | Keep Git as the current primary documentation source of truth | accepted | Notion synchronization remains downstream and must not overwrite Git silently | SBM Suite | `FORMAT_CONTEXT.md` |

## 6. Components

| Service | Project | Container | Internal port | Host port | Network | Health check | Status |
|---|---|---|---:|---:|---|---|---|
| DP-API | `DP-API` | api | N/A | N/A | Docker Compose network | Configured QA and application checks | active |
| Documentation backend | `sbm-ai-assistant` | backend | N/A | N/A | Docker Compose network | Backend endpoint validation | active |
| Qdrant | `sbm-ai-assistant` | qdrant | N/A | N/A | Docker Compose network | Collection access | active |
| PostgreSQL | `SBM-DB` | postgres | 5432 | 5432 | SBM network | Container health check | active |

Exact DP-API, backend and Qdrant ports are not established by the supplied package and remain `N/A` here.

## 7. Workflows

| Step | Component | Input | Action | Output | Validation |
|---:|---|---|---|---|---|
| 1 | Context lifecycle caller | Phase, objective ID and optional user prompt | Select the explicit lifecycle operation | Context export request | Phase and prompt rules |
| 2 | Context contract preflight | `GET /contexts/contract` | Validate version, lifecycle phases, canonical project path and supported patches | Compatible contract metadata | HTTP 200 and exact contract fields |
| 3 | Context exporter | Git, context and optional QA evidence | Index and retrieve context, render the prompt and build the evidence package | `context-package.zip` | Safe paths, protected contracts and package manifest |
| 4 | Context upgrade preflight | Reviewed context ZIP | Inspect members, manifest, execution mode, phase, target mappings, hashes and mandatory physical patches | Validated context upgrade request | Client and backend validation |
| 5 | Context upgrade backend | Validated context ZIP | Back up and apply authorized section operations | Synchronized operational and historical context | Atomic replacement and rollback |
| 6 | QA workflow | DP-API repository | Run configured pytest, coverage and SonarScanner sequence | `context/qa-results.md` and `coverage.xml` | Exit codes and bounded evidence |
| 7 | Documentation indexer and exporter | Validated contexts, Git and QA evidence when applicable | Index documentation, retrieve relevant documentation/context and build the package | `documentation-package.zip` | Planning-only for `active`/`pending`; implemented-state only after closure |
| 8 | LLM generation | Documentation package | Generate complete authorized replacements | `documentation-upgrade.zip` | Prompt and format contract |
| 9 | Documentation upgrade | Reviewed documentation ZIP | Validate, back up and replace existing authorized pages | Updated documentation | Hash, metadata, heading, path and rollback checks |

| Artifact | Workflow | Producer | Consumer | Path | Required | Description |
|---|---|---|---|---|---:|---|
| `qa-results.md` | QA | `qa-check.sh` | Context and documentation deploy | `SBM-SUITE/dp/DP-API/context/qa-results.md` | 1 for closure | Bounded pytest, coverage and SonarScanner evidence |
| `context-package.zip` | context deploy | Backend exporter | LLM | `SBM-SUITE/context/output/` | 1 | Context evidence package |
| `context-upgrade.zip` | context upgrade | LLM | Backend validator | `SBM-SUITE/context/input/` | 1 | Authorized context section updates |
| `documentation-package.zip` | documentation deploy | Backend exporter | LLM | `SBM-SUITE/context/documentation/output/` | 1 | Documentation evidence and workflow contracts |
| `documentation-upgrade.zip` | documentation upgrade | LLM | Backend validator | `SBM-SUITE/context/documentation/input/` | 1 | Complete authorized Markdown replacements |

| Workflow | Qdrant collection | Source of truth | Generated package | Upgrade output |
|---|---|---|---|---|
| Context workflow | `sbm_contexts` | Git context files | `context-package.zip` | `context-upgrade.zip` |
| Documentation workflow | `sbm_documentation` | Git documentation files | `documentation-package.zip` | `documentation-upgrade.zip` |
| Confluence assistant knowledge | `sbm_docs` | Confluence | N/A | N/A |

Required deployment control sequence:

```text
build
→ validate
→ deploy
→ health check
→ smoke test
→ monitor
→ rollback when required
```

The supplied evidence validates local QA and workflow execution; it does not prove that a production deployment followed this sequence.

## 8. Configuration

| Environment | Purpose | Runtime | Configuration source | Deployment method | Status |
|---|---|---|---|---|---|
| Local development | Execute DP-API, QA and workflow clients | Docker Compose and shell | `.env.dev` | Manually invoked scripts and Docker Compose | active |

The project scripts read these configuration names from the project-local `.env.dev` without exposing their values:

```text
DOPPLER_PROJECT
AI_ASSISTANT_URL
SBM_SUITE_ROOT
```

The backend uses these mounted paths:

```text
CONTEXT_UPGRADE_PROJECT_ROOT=/suite
CONTEXT_UPGRADE_SUITE_CONTEXT_ROOT=/suite/context
CONTEXT_UPGRADE_INPUT_ROOT=/suite/context/input
CONTEXT_UPGRADE_BACKUP_ROOT=/suite/context/backup
DOCUMENTATION_UPGRADE_DOCUMENTATION_ROOT=/suite/context/documentation
DOCUMENTATION_UPGRADE_INPUT_ROOT=/suite/context/documentation/input
DOCUMENTATION_UPGRADE_BACKUP_ROOT=/suite/context/backup
```

Context closure requires non-empty QA evidence at `SBM-SUITE/dp/DP-API/context/qa-results.md`. Context deployment must render every prompt template variable before packaging and must stop when unresolved template tokens remain.

Secret values, credentials and `.env` files remain outside documentation and generated ZIP contents.

## 9. Security

- Reject absolute paths, `..`, backslashes, duplicate paths and symlinks.
- Reject encrypted or corrupt ZIP members.
- Validate the published contract before cleaning shared exchange outputs or calling context upgrade.
- Validate physical ZIP files against manifest allowlists and supported patch paths.
- Restrict context operations and documentation replacements to exact authorized targets.
- Protect `SYS_PROMPT.md` and `FORMAT_CONTEXT.md` from automated upgrade.
- Validate SHA-256 hashes against the exact final file bytes.
- Create exactly one timestamped backup below `SBM-SUITE/context/backup/` before replacement.
- Roll back already replaced files when an application failure occurs.
- Do not package credentials, tokens, `.env` files, raw vectors or secret values.

## 10. Validation

Validated documentation deployment evidence:

- project: `dp-api`;
- workflow: `documentation-deploy`;
- status: `completed`;
- indexed documentation sources: `28`;
- indexed documentation chunks: `3390`;
- collection: `sbm_documentation`;
- deployment errors: none reported.

Validated `DP-TEST-001` lifecycle-only/no-op closure evidence generated on `2026-08-07`:

- configured pytest scope: `65` collected and `65` passed;
- failed tests: `0`;
- pytest exit code: `0`;
- total configured pytest coverage: `88%`;
- coverage artifact: `coverage.xml`;
- SonarScanner exit code: `0`;
- indexed Python files: `40`;
- Sonar analysis: `ANALYSIS SUCCESSFUL`;
- SonarScanner execution: `EXECUTION SUCCESS`;
- server-side Quality Gate: `OK`;
- implementation change evidenced for `DP-TEST-001`: none.

The validation applies to the configured QA scope and supports lifecycle closure without asserting a source-code or runtime change.

Historical `DP-QA-001` evidence dated `2026-08-02` remains valid for its recorded scope; that earlier scanner output did not contain a server-side Quality Gate result.

The documentation upgrade validator additionally requires exact metadata labels, exact level-two heading order, authorized existing paths, matching manifest lists and valid SHA-256 hashes.

## 11. Known limitations

- The `2026-08-07` QA run records server-side Quality Gate `OK`; this result applies only to that configured QA execution.
- Tenant isolation, object permissions, production readiness, deployment and database compatibility remain outside the validated QA scope.
- No migration or production deployment execution is evidenced.
- Exact runtime ports for DP-API, the documentation backend and Qdrant were not established by this package.
- Notion synchronization remains planned downstream work.
- The workflows remain manually initiated; Git commit and push remain manual.
- Historical documentation backup artifacts may appear as retrieval evidence, but only existing files below `documentation/pages/` are valid replacement targets.
- Related QA, SBM-Suite and development-roadmap pages retain legacy structures that do not satisfy the current complete-page contract and are not replaced automatically by this upgrade.

## 12. Roadmap

### QA transversal de `SBM-SUITE/context`

| Objective ID | Objective | Status | Priority | Target date | Branch |
|---|---|---|---:|---|---|
| OBJ-CTX-014 | Habilitar QA transversal en `SBM-SUITE/context` para ejecutar, centralizar y gestionar validaciones QA de los proyectos de la suite desde el contexto global, manteniendo los scripts QA específicos por proyecto y una orquestación común desde `context`. | pending | 5 | N/A | FEATURE-enables-transversal-qa |

Este objetivo permanece pending y representa exclusivamente planificación. No acredita implementación, ejecución QA ni cambios de runtime.

- Complete and validate `SBM-MANAGER` lifecycle integration across context and documentation workflows, QA/SonarQube evidence, and the canonical `sbm-ai-assistant` project contract before promoting it to current-state documentation.
- Implement asynchronous workflow orchestration when approved.
- Add downstream Notion synchronization without changing Git ownership.
- Expand observability for indexing, retrieval, validation, backup and rollback.
- Maintain separate context, documentation and Confluence collections.

## 13. Related pages

| Page | Path | Relationship |
|---|---|---|
| AI Engineering | `SBM-SUITE/context/documentation/pages/🤖 AI Architect Roadmap/🤖AI-Engineering 3a50bde8acd580fd84dbce95d8244e8d.md` | Defines AI, RAG and Tool architecture |
| QA and Testing | `SBM-SUITE/context/documentation/pages/🤖 AI Architect Roadmap/🧪QA & Testing 3a50bde8acd580028bb1ffa68930e538.md` | Defines QA strategy and evidence requirements |
| Security and DevSecOps | `SBM-SUITE/context/documentation/pages/🤖 AI Architect Roadmap/🔐 Security & DevSecOps 3a30bde8acd580b3abddca1cf6ff5ec9.md` | Defines security controls and risk handling |
| Observability and Monitoring | `SBM-SUITE/context/documentation/pages/🤖 AI Architect Roadmap/📊 Observability & Monitoring 3a30bde8acd580d99985d1f851394d0c.md` | Defines operational telemetry goals |

## 14. Subpages

| Subpage | Path | Description | Status |
|---|---|---|---|
| N/A | N/A | No authorized subpages are listed for this page in the supplied package. | active |

## 15. Document boundary

This page defines the current DevOps, QA evidence and context/documentation workflow operating model supported by supplied evidence. The `2026-08-07` configured QA run includes server-side Quality Gate `OK`, but this page does not certify production readiness, cloud or Kubernetes deployment, tenant isolation, object-level authorization, database compatibility, migration execution or Notion synchronization.
