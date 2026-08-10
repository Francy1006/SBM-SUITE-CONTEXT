# PROJECT_CONTEXT.md

> **Last updated:** 2026-08-07
>
> **Purpose**
>
> Persistent global project context for **SBM Suite**.
>
> **Accuracy note**
>
> Git Markdown is the current source of truth. Qdrant is a semantic index. Active objectives, pending objectives, completed-objective history, QA results, documentation state and implemented behavior remain explicitly separated.

## 1. Executive summary

SBM Suite is evolving toward a governed context and documentation lifecycle based on Git, RAG, Qdrant, ChatGPT-reviewed section patches, validated upgrades, QA evidence and later Notion synchronization.

The current design separates:

- project and global contexts;
- QA execution from QA interpretation;
- context workflows from documentation workflows;
- `sbm_contexts` from `sbm_documentation`;
- active and pending objectives from completed-objective history and validated implementation.

## 2. Suite purpose

SBM Suite groups business APIs, internal platform APIs, data ownership, frontend applications, AI orchestration, QA evidence and operational documentation under shared governance rules.

Primary responsibilities:

```text
SBM-MANAGER
→ enterprise web frontend consuming DP-API and SBM-API

DP-API
→ client-facing business API

SBM-API
→ internal platform API

sbm-ai-assistant
→ AI orchestration, embeddings, Qdrant, RAG, context and documentation processing

SBM-SUITE/context
→ global project, suite, business, QA, security, data and decision contexts
```

## 3. Active objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
| OBJ-CTX-001 | SBM-SUITE | Validate and stabilize the expanded context governance model, synchronized section patches and project-tree evidence | active | 5 |  | FEATURE-expands-context-governance | `context/documentation/pages/AI Architect Roadmap/`, `context/documentation/pages/SBM-Suite/` |
| SBM-MANAGER-001 | SBM-MANAGER | Integrar SBM-MANAGER completamente a SBM Suite, incluyendo contextos, lifecycle scripts, QA/SonarQube, registro en sbm-ai-assistant, sincronización global y actualización del diagrama canónico de arquitectura en SUITE_CONTEXT.md. | active | 5 | 2026-08-07 | FEATURE-integrates-sbm-manager | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |
| SBM-DB-001 | SBM-DB | habilitación de sbm-db | active | 5 | 2026-08-07 | FEATURE-enables-sbm-db | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |

Rules:

- this section contains only objectives currently being addressed;
- status is always `active`;
- branch is mandatory before implementation begins;
- every project objective change must update this section and the project summary;
- completed objectives are removed and appended only to `context/COMPLETED_OBJECTIVES.md`.

## 4. Pending objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
| SBM-MANAGER-002 | SBM-MANAGER | Corregir SBM-MANAGER para consumir correctamente SBM-API y DP-API según ownership canónico. | pending | 5 | N/A | BUGFIX-corrects-api-ownership | N/A |
| SBM-MANAGER-003 | SBM-MANAGER | Corregir y completar QA de SBM-MANAGER. | pending | 5 | N/A | BUGFIX-completes-manager-qa | N/A |
| OBJ-DOC-001 | SBM-SUITE | Implement the manual documentation deploy and upgrade workflow with dedicated RAG and Qdrant collection | pending | 4 |  | FEATURE-adds-documentation-workflow | `context/documentation/pages/AI Architect Roadmap/`, `context/documentation/pages/Roadmap/`, `context/documentation/pages/SBM-Suite/` |
| SBM-DB-002 | SBM-DB | Actualizar SBM-DB al contrato lifecycle actual de Context, incluyendo objectives[], execution_mode, preservación literal de objetivos y paths relativos. | pending | 5 | N/A | FEATURE-updates-context-lifecycle | N/A |
| OBJ-CTX-002 | SBM-SUITE | Habilitar un sistema automatizado para ejecutar flujos transversales sobre uno o varios proyectos. | pending | 5 | N/A | FEATURE-automates-cross-project-flows | N/A |
| OBJ-CTX-003 | SBM-SUITE | Separar QA y Context mediante una estructura específica por proyecto. | pending | 5 | N/A | FEATURE-separates-qa-context | N/A |
| OBJ-CTX-004 | SBM-SUITE | Habilitar un nuevo proyecto para procesamiento asíncrono, incluyendo PostgreSQL, Celery, Redis, Kafka y los componentes de infraestructura relacionados. | pending | 5 | N/A | FEATURE-enables-async-platform | N/A |
| OBJ-CTX-005 | SBM-SUITE | Habilitar un proyecto UTIL para centralizar servicios y utilidades reutilizables y desacoplarlos de proyectos específicos, incluyendo generación de ZIP y procesamiento de contextos. | pending | 5 | N/A | FEATURE-enables-shared-utils | N/A |
| OBJ-CTX-006 | SBM-SUITE | Habilitar un agente de backlog que convierta objetivos en issues y épicas y gestione su sincronización con Jira vía API. El nombre definitivo del agente se revisará al activar el objetivo. | pending | 5 | N/A | FEATURE-enables-backlog-agent | N/A |
| OBJ-CTX-007 | SBM-SUITE | Habilitar un agente QA para gestionar y automatizar procesos de validación de calidad de los proyectos. | pending | 5 | N/A | FEATURE-enables-qa-agent | N/A |
| OBJ-CTX-008 | SBM-SUITE | Habilitar un entorno y flujo de seguridad ejecutado después de QA y antes del commit. | pending | 5 | N/A | FEATURE-enables-security-flow | N/A |
| OBJ-CTX-009 | SBM-SUITE | Habilitar un agente de seguridad para ejecutar y gestionar las validaciones del flujo de seguridad. | pending | 5 | N/A | FEATURE-enables-security-agent | N/A |
| OBJ-CTX-010 | SBM-SUITE | Habilitar una aplicación para visualizar y gestionar agentes, definiendo la tecnología y lenguaje apropiados al activar el objetivo. | pending | 5 | N/A | FEATURE-enables-agent-management | N/A |
| OBJ-CTX-011 | SBM-SUITE | Completar `INIT_CONTEXT.md` para soportar creación/onboarding de nuevos proyectos SBM. | pending | 5 | N/A | FEATURE-completes-project-onboarding | N/A |
| OBJ-CTX-012 | SBM-SUITE | Separar el flujo del agente en `SBM_AGENT_INIT.md`, dejando `INIT_CONTEXT.md` como punto de entrada y orquestación. | pending | 5 | N/A | FEATURE-separates-agent-init-flow | N/A |
| OBJ-CTX-013 | SBM-SUITE | Corregir y validar el workflow de documentación de `SBM-SUITE/context`, incluyendo `documentation-deploy.sh`, `documentation-upgrade.sh` y el flujo completo posterior a `context-upgrade`. | pending | 5 | N/A | BUGFIX-fixes-context-documentation-workflow | N/A |

Rules:

- this section contains only approved objectives not yet started;
- status is always `pending`;
- objectives move to `Active objectives` when implementation begins;
- completed objectives never remain here;
- every project objective change must update this section and the project summary.

## 5. Projects and ownership

| Project | Ownership | Main responsibilities | Source of truth |
|---|---|---|---|
| DP-API | Client-facing business operations | Products, materials, services, catalogs, tickets, providers, pricing, branches and other client domains | Project code, project contexts and canonical APIs |
| SBM-MANAGER | Enterprise web frontend | Vue 3 management UI, frontend orchestration, reusable CRUD behavior and explicit DP-API / SBM-API consumption | Project code, project contexts and frontend API clients |
| SBM-API | Internal platform operations | Internal administration, franchise, fiscal, inventory, calculation, configuration and platform services | Project code and project contexts |
| SBM-DB | Physical database and migration authority | PostgreSQL schemas, DBML, Flyway migrations, constraints, views and structural seeds | DBML, Flyway, PostgreSQL runtime and project contexts |
| sbm-ai-assistant | AI and knowledge orchestration | Embeddings, Qdrant, RAG, Slack, context export/upgrade and future documentation workflows | AI repository and indexed Git Markdown |
| SBM-SUITE/context | Global governance | Cross-project context, architecture, business, QA, security, data, decisions and workflow contracts | Git Markdown |

Canonical project roots include `SBM-SUITE/dp/DP-API/`, `SBM-SUITE/sbm/SBM-API/`, `SBM-SUITE/sbm/SBM-DB/`, `SBM-SUITE/sbm/SBM-MANAGER/` and `SBM-SUITE/sbm/sbm-ai-assistant/`. Their canonical runtime roots are `/suite/dp/DP-API`, `/suite/sbm/SBM-API`, `/suite/sbm/SBM-DB`, `/suite/sbm/SBM-MANAGER` and `/suite/sbm/sbm-ai-assistant`.

## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| DP-API | Client-facing business API | test fix | Dedicated Service app; Material consumer migration; duplicate Product endpoint retirement | `BUGFIX-test-fix` | `dp/DP-API/context/PROJECT_CONTEXT.md` | `dp/DP-API/context/QA_CONTEXT.md` | `context/documentation/pages/QA & Testing/`, `context/documentation/pages/Development Roadmap/` |
| SBM-MANAGER | Enterprise web frontend | Integrar SBM-MANAGER completamente a SBM Suite | Corregir SBM-MANAGER para consumir correctamente SBM-API y DP-API según ownership canónico.<br>Corregir y completar QA de SBM-MANAGER. | `FEATURE-integrates-sbm-manager` | `sbm/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `sbm/SBM-MANAGER/context/QA_CONTEXT.md` | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |
| SBM-DB | PostgreSQL schema and migration authority | habilitación de sbm-db | Actualizar SBM-DB al contrato lifecycle actual de Context, incluyendo objectives[], execution_mode, preservación literal de objetivos y paths relativos. | `FEATURE-enables-sbm-db` | `sbm/SBM-DB/context/PROJECT_CONTEXT.md` | `sbm/SBM-DB/context/QA_CONTEXT.md` | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |
| SBM-API | Internal platform API | Not defined | Not defined | N/A | `sbm/SBM-API/context/PROJECT_CONTEXT.md` | `sbm/SBM-API/context/QA_CONTEXT.md` | To be mapped |
| sbm-ai-assistant | AI orchestration and RAG | Support expanded context governance and project-tree evidence | Add documentation export, upgrade and dedicated collection | `FEATURE-expands-context-governance` | `sbm/sbm-ai-assistant/context/PROJECT_CONTEXT.md` | `sbm/sbm-ai-assistant/context/QA_CONTEXT.md` | `context/documentation/pages/AI Engineering/`, `context/documentation/pages/SBM-Suite/` |
| SBM-SUITE | Global governance and orchestration | Implement expanded context governance | Implement documentation workflow<br>Habilitar un sistema automatizado para ejecutar flujos transversales sobre uno o varios proyectos.<br>Separar QA y Context mediante una estructura específica por proyecto.<br>Habilitar un nuevo proyecto para procesamiento asíncrono, incluyendo PostgreSQL, Celery, Redis, Kafka y los componentes de infraestructura relacionados.<br>Habilitar un proyecto UTIL para centralizar servicios y utilidades reutilizables y desacoplarlos de proyectos específicos, incluyendo generación de ZIP y procesamiento de contextos.<br>Habilitar un agente de backlog que convierta objetivos en issues y épicas y gestione su sincronización con Jira vía API. El nombre definitivo del agente se revisará al activar el objetivo.<br>Habilitar un agente QA para gestionar y automatizar procesos de validación de calidad de los proyectos.<br>Habilitar un entorno y flujo de seguridad ejecutado después de QA y antes del commit.<br>Habilitar un agente de seguridad para ejecutar y gestionar las validaciones del flujo de seguridad.<br>Habilitar una aplicación para visualizar y gestionar agentes, definiendo la tecnología y lenguaje apropiados al activar el objetivo.<br>Completar `INIT_CONTEXT.md` para soportar creación/onboarding de nuevos proyectos SBM.<br>Separar el flujo del agente en `SBM_AGENT_INIT.md`, dejando `INIT_CONTEXT.md` como punto de entrada y orquestación. | `FEATURE-expands-context-governance` | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | `context/documentation/` |

## 7. Global architecture

Current context architecture:

```text
Git Markdown contexts
→ context-deploy.sh
→ sbm-ai-assistant
→ embeddings
→ Qdrant sbm_contexts
→ RAG context package
→ ChatGPT section patches
→ context-upgrade.sh
→ validated backup and atomic replacement
```

Planned documentation architecture:

```text
Git Markdown documentation
+ updated contexts
→ documentation-deploy.sh
→ sbm-ai-assistant
→ embeddings
→ Qdrant sbm_documentation
→ RAG documentation package
→ ChatGPT updated authorized documentation Markdown
→ documentation-upgrade.sh
→ documentation backup and replacement
→ later Notion synchronization
```

QA architecture:

```text
qa-check.sh
→ tests
→ coverage
→ SonarQube
→ qa-results.md and evidence
→ context-deploy.sh
→ project QA_CONTEXT patch
→ global QA_CONTEXT summary patch
```

## 8. Shared infrastructure

Current shared infrastructure includes:

| Component | Purpose | Current ownership |
|---|---|---|
| PostgreSQL | Business and platform data | SBM-DB |
| Flyway | Business-schema migrations | SBM-DB |
| Qdrant | Semantic indexes | sbm-ai-assistant |
| Docker Compose | Local runtime orchestration | Each project and suite infrastructure |
| Git | Primary source of truth and version history | All projects |
| SonarQube | Static analysis and quality evidence | QA workflow |

Qdrant collections:

```text
sbm_docs
→ Confluence and assistant knowledge

sbm_contexts
→ suite and project contexts

sbm_documentation
→ roadmap and documentation pages
```

`sbm_documentation` is planned and must remain separate from `sbm_contexts`.

## 9. Cross-project integrations

```text
DP-API
→ client-facing requests
→ canonical business operations

SBM-MANAGER
→ DP-API for client-owned operations
→ SBM-API for internal/platform operations

SBM-API
→ internal platform operations

DP-API
→ asynchronous orchestration toward SBM-API where ownership requires it

SBM-DB
→ physical schema and migration authority

sbm-ai-assistant
→ canonical APIs and indexed Markdown
→ never writes directly to PostgreSQL

SBM-SUITE/context
→ global synchronization of project objectives and QA summaries
```

Every project `PROJECT_CONTEXT.md` update must update this global context.

Every project `QA_CONTEXT.md` update must update the global `QA_CONTEXT.md` summary.

## 10. Context deployment and upgrade workflow

### Deployment

```text
qa-check.sh
→ execute the configured pytest and coverage workflow
→ run SonarScanner only after successful test and coverage execution
→ persist bounded evidence in context/qa-results.md

context-deploy.sh <lifecycle_phase> <objective_id> [user_prompt]
→ validate the explicit lifecycle phase and objective
→ request GET /contexts/contract before cleaning exchange directories
→ validate contract version, lifecycle phases, canonical project path and supported patches
→ use SBM-SUITE/context/SYS_PROMPT.md and SBM-SUITE/context/FORMAT_CONTEXT.md
→ execute SBM-SUITE/context/project-tree.sh and require project-tree.txt
→ collect Git and QA evidence without packaging environment values
→ call POST /contexts/export with project_root=/suite/<brand>/<project>
→ index authorized contexts in sbm_contexts
→ retrieve relevant chunks
→ package evidence plus complete authorized source snapshots as input-only files
→ generate context-package.zip, context-export-response.json and a fully parameterized SYS_PROMPT.md
```

### Planning activation and review

```text
planning-activation
→ requires the literal objective text
→ synchronizes project and global active or pending objectives
→ records planned QA without execution results
→ forbids completed-objective history
```

### Implementation progress

```text
implementation-progress
→ records only evidence-supported current state
→ preserves the objective as active or pending
→ forbids completed-objective history and closure claims
```

### Implementation closure

```text
implementation-closure
→ requires implementation evidence and successful QA evidence
→ requires project and global objective patches
→ requires project and global QA patches
→ removes only the requested objective from operational contexts
→ appends exactly one record to context/COMPLETED_OBJECTIVES.md
```

### Upgrade

```text
context-upgrade.zip
→ context/input
→ context-upgrade.sh
→ inspect manifest.json without extracting the archive
→ reject unsafe, unsupported or phase-incompatible members
→ require all five closing patches during implementation closure
→ call POST /contexts/upgrade only after client preflight succeeds
→ create context/backup/<timestamp>_<project>/
→ preserve original files plus EXECUTIVE_README.md and COMMIT_MESSAGE.md
→ write BACKUP_MANIFEST.json with project, workflow, time, reason, paths and SHA-256 hashes
→ apply authorized section patches atomically
→ remove input only after complete success
```

## 11. Documentation deployment and upgrade workflow

Documentation structure:

```text
context/documentation/
├── FORMAT_CONTEXT.md
├── SYS_PROMPT.md
├── input/
├── output/
└── pages/
    └── <page>/
        ├── <page>.md
        └── subpages/
            └── <subpage>.md
```

Manual workflow:

```text
completed implementation
→ qa-check.sh and SonarQube validation
→ final context upgrade and objective closure
→ user confirms git status
→ documentation-deploy.sh
→ RAG from current documentation and updated contexts
→ documentation-package.zip + documentation SYS_PROMPT.md
→ user uploads both to ChatGPT
→ ChatGPT returns documentation-upgrade.zip
→ documentation-upgrade.sh
→ validate authorized existing pages and format
→ create the timestamped documentation backup under context/backup
→ replace only authorized Markdown
→ print proposed commit message
```

Rules:

- Git is the primary source of truth during the first stage;
- documentation pages and subpages are modified only when authorized by the documentation format;
- main pages are first-class documents and maintain subpage links;
- automated creation, deletion, rename and structural changes are not allowed initially;
- structural changes require manual updates to the page, documentation format and documentation system prompt;
- context and documentation upgrades remain separate;
- documentation is executed only after implementation closure and never for planning activation;
- later synchronization with Notion may become bidirectional.
- `SBM-SUITE/context/backup/` is the only backup root for both workflows;
- pluralized and workflow-local backup directories must never be used or recreated.

## 12. Current implementation status

Verified current capabilities include:

- global and DP-API context files exist;
- `GET /contexts/contract`, `POST /contexts/export` and `POST /contexts/upgrade` exist in `sbm-ai-assistant`;
- contract version, lifecycle phases, canonical project paths and supported patches are validated before export and upgrade;
- deterministic and idempotent context indexing exists in `sbm_contexts`;
- RAG-based context retrieval exists;
- context packages contain bounded evidence and complete authorized source snapshots for safe section replacement;
- manifest, path, UTF-8, ZIP-member and SHA-256 validation exist;
- timestamped backup, atomic replacement and rollback support exist;
- DP-API deploy and upgrade scripts use explicit lifecycle phases and objective identifiers;
- activation, progress and closure behaviors are separated;
- implementation closure requires project/global objective and QA synchronization;
- completed objectives use a single global historical register outside the operational development context;
- project-tree generation and package evidence exist;
- `qa-check.sh` writes test, coverage and SonarScanner evidence to `context/qa-results.md`;
- DP-API closure evidence records 65 passing tests, 88% configured pytest coverage and successful SonarScanner execution.

Planned or incomplete capabilities:

- fresh SBM-MANAGER QA execution and end-to-end context lifecycle validation;
- complete cross-project synchronization coverage beyond the validated DP-API flow;
- expanded context types and remaining project contexts;
- dedicated documentation workflow and `sbm_documentation` validation;
- Git-to-Notion synchronization;
- asynchronous database-flag orchestration.

## 13. Validated decisions

1. Git Markdown is the primary source of truth during the manual stage.
2. Qdrant is a semantic index, not an authoritative store.
4. Context and documentation use separate Qdrant collections.
5. QA execution is performed by `qa-check.sh`; QA interpretation occurs in the context workflow.
6. Project objective changes synchronize to the global project context.
7. Project QA changes synchronize to the global QA context.
8. Context and documentation upgrades use separate deploy and upgrade workflows.
9. ChatGPT generates section-level context patches rather than complete context documents.
10. Documentation upgrade initially modifies only existing authorized pages.
10. Branch names are assigned before development using `FEATURE`, `BUGFIX` or `HOTFIX` and a maximum four-word slug.
11. Commit metadata is returned by the upgrade command to support one final commit.
12. Future asynchronous processing may use database configuration flags.
13. Active and pending objectives are stored separately in project and global contexts.
14. Completed objectives are removed from operational contexts and stored only in `context/COMPLETED_OBJECTIVES.md`.
15. Documentation runs only after implementation, QA validation and final context closure.

## 14. Accepted risks and constraints

- The current workflow is manual.
- Context and documentation consistency depends on completing both workflows when required.
- RAG retrieval may omit required source sections; unsafe patches must then be omitted.
- Project contexts for remaining repositories may not yet exist or may be incomplete.
- Documentation format and page authorization are not yet implemented.
- Notion synchronization is not yet implemented.
- Database flags and asynchronous orchestration are deferred.
- Existing contexts may require structural migration to the new format before patch-based upgrades succeed.

## 15. Completed work

- initial global context structure defined;
- `SUITE_CONTEXT.md` created;
- `BUSINESS_CONTEXT.md` created;
- global `QA_CONTEXT.md` created;
- `SYS_PROMPT.md` created;
- DP-API contexts created;
- DP-API `context-deploy.sh` created;
- DP-API `context-upgrade.sh` created;
- `POST /contexts/export` implemented;
- `POST /contexts/upgrade` implemented;
- `sbm_contexts` implemented;
- deterministic and idempotent indexing implemented;
- context ZIP and manifest generation implemented;
- RAG-based context retrieval implemented;
- context backup, validation, atomic replacement and rollback implemented;
- evidence and user-guided execution modes defined;
- documentation exported to Git under `context/documentation/`;
- expanded `FORMAT_CONTEXT.md` contract defined.
- SBM-MANAGER canonical project context, QA context, deploy context and lifecycle scripts prepared;
- SBM-DB canonical project context, QA context, deploy context and lifecycle scripts prepared;
- section-level patch validation and application implemented;
- project-tree generation integrated into context deployment;
- context export response persistence and completion validation implemented;
- context upgrade input and response validation strengthened;
- QA evidence file generation implemented in `qa-check.sh`;

## 16. Pending work

1. Validate SBM-MANAGER project-to-global synchronization and QA lifecycle with fresh evidence.
2. Validate SBM-DB canonical registry, migration QA and project-to-global lifecycle with fresh evidence.
3. Complete validated project-to-global synchronization coverage for the remaining projects.
4. Create and populate `SECURITY_CONTEXT.md` with validated evidence.
4. Create and populate `DATA_CONTEXT.md` with validated evidence.
5. Create and populate `DECISIONS_CONTEXT.md` with validated evidence.
6. Complete and validate the documentation deploy and upgrade workflow.
7. Create and validate `sbm_documentation`.
8. Map all documentation pages to relevant contexts.
9. Add later Git-to-Notion synchronization.
10. Add later asynchronous database-flag orchestration.

## 17. Required behavior

Before changes:

1. identify the target project;
2. read applicable contexts;
4. inspect actual repository state;
5. execute QA when required;
6. verify database ownership when relevant;
7. report missing information;
8. define or update the objective as active or pending and assign its branch before implementation.

During changes:

- preserve canonical ownership;
- avoid speculative refactors;
- avoid unauthorized migrations;
- do not expose secrets;
- do not modify unrelated projects;
- synchronize project and global contexts when required;
- keep implemented, planned and validated states separate;
- use only authorized section patches;
- do not perform Git operations unless requested.

After changes:

- report files modified;
- report validation executed and not executed;
- report database and migration impact;
- report remaining risks;
- update required project and global contexts;
- update the project README when a reusable service, `.sh` script, model, reusable module, shared utility or public technical component is added, removed, renamed, moved or changed significantly;
- keep the global `context/README.md` general and update it only for suite-level structure, architecture, shared functionality or global workflows;
- close completed objectives by removing them from project and global operational contexts and appending them to `context/COMPLETED_OBJECTIVES.md`;
- run the documentation workflow only after implementation and QA closure when architecture, structure, technology or tangible behavior changed;
- print the proposed commit message from the final upgrade.

## 18. Historical decisions

Previous context exports included complete update-authorized Markdown files. The accepted target design replaces that behavior with RAG-selected evidence and section-level JSON patches to reduce tokens and avoid unsafe full-document replacement.

Previous QA and business contexts were protected from context upgrades. The accepted target design authorizes their controlled update when evidence and synchronization rules require it.

Documentation was previously external to the context lifecycle. It is now versioned in Git and will use a separate deploy and upgrade workflow before later Notion synchronization.

## 19. Related documentation

Current documentation root:

```text
SBM-SUITE/context/documentation/
```

Primary documentation groups currently relevant to the global roadmap include:

- `AI Architect Roadmap`;
- `Development Roadmap`;
- `SBM-Suite`;
- `QA & Testing`;
- `Security & DevSecOps`;
- `AI Engineering`;
- `DevOps`;
- `Observability`;
- `Cloud`;
- `Automation`;
- `Technologies` when available in the exported hierarchy.

Exact page and subpage paths must be maintained by the documentation format contract.

## 20. Document boundary

This file records global project state, ownership, active and pending objectives, cross-project workflows, validated decisions, risks and high-level summaries. Completed-objective history is stored separately in `context/COMPLETED_OBJECTIVES.md`.

It does not replace:

- detailed project contexts;
- `SUITE_CONTEXT.md` technical inventories and endpoint contracts;
- `BUSINESS_CONTEXT.md` brand and business metrics;
- project or global `QA_CONTEXT.md` test inventories and evidence;
- `SECURITY_CONTEXT.md` security controls;
- `DATA_CONTEXT.md` data ownership and lifecycle;
- `DECISIONS_CONTEXT.md` detailed ADR records;
- deployment contexts;
- roadmap and Notion documentation pages.
