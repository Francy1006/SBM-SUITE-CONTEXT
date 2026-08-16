# SUITE_CONTEXT.md

> **Last updated:** 2026-08-07
>
> **Purpose**
>
> Persistent global technical context for **SBM Suite**. It defines brands, projects, applications, technologies, APIs, endpoint contracts, integrations, infrastructure and shared operational boundaries.
>
> **Accuracy note**
>
> Verified repository, runtime, API, database and QA evidence takes precedence over this document when a conflict exists. Unknown versions, bodies or response contracts must remain `N/A` until evidenced.

## 1. Suite identity

SBM Suite is a modular ERP and business platform composed of independent repositories with explicit ownership boundaries.

Primary responsibility model:

```text
Enterprise web interaction
→ SBM-MANAGER

Client business operations
→ DP-API

Internal platform operations
→ SBM-API

AI orchestration
→ sbm-ai-assistant
```

Git Markdown is the current source of truth for contexts and documentation. Qdrant is a semantic index only.

## 2. Product scope

SBM Suite separates:

- client-facing business operations;
- internal platform administration;
- enterprise frontend interaction;
- database ownership and migrations;
- AI-assisted workflows;
- quality assurance;
- deployment;
- context and documentation lifecycle management.

Current business scope includes products, materials, services, catalogs, pricing, providers, branches, agreements, tickets, users, roles and permissions.

## 3. Brands and platforms

| Brand | Platform | Description | Status |
|---|---|---|---|
| SBM | SBM Suite | Platform, infrastructure, internal services and shared capabilities | active |
| Ditaly Pasta | Client ERP | Brand-specific operational and commercial platform | active |

`SBM` is treated as its own brand for technical, platform and infrastructure records.

## 4. Project map

| Project | Brand | Primary responsibility | Canonical owner |
|---|---|---|---|
| DP-API | Ditaly Pasta | Client-facing business API | Client operations |
| SBM-MANAGER | SBM | Enterprise web frontend for client and platform interaction | Frontend |
| SBM-API | SBM | Internal platform API | Platform administration |
| SBM-DB | SBM | PostgreSQL business schemas and Flyway migrations | Data layer |
| sbm-ai-assistant | SBM | AI orchestration, RAG, embeddings and Tools | AI-assisted workflows |
| SBM-SUITE/context | SBM | Global context and documentation contracts | Context governance |

Canonical repository paths currently evidenced here include `SBM-SUITE/dp/DP-API/`, `SBM-SUITE/sbm/SBM-API/`, `SBM-SUITE/sbm/SBM-DB/`, `SBM-SUITE/sbm/SBM-MANAGER/` and `SBM-SUITE/sbm/sbm-ai-assistant/`. Canonical runtime roots preserve those brand segments as `/suite/dp/DP-API`, `/suite/sbm/SBM-API`, `/suite/sbm/SBM-DB`, `/suite/sbm/SBM-MANAGER` and `/suite/sbm/sbm-ai-assistant`.

## 5. Applications and services

| Brand | Project | Application or service | Type | Description | Language | Framework | Version | Runtime | Owner |
|---|---|---|---|---|---|---|---|---|---|
| SBM | SBM-MANAGER | Enterprise web frontend | web frontend | Web interface consuming DP-API and SBM-API | JavaScript | Vue.js 3 | N/A | container | SBM-MANAGER |
| Ditaly Pasta | DP-API | Client-facing API | API | Business operations for authorized client users | Python | Django REST Framework | N/A | container | DP-API |
| SBM | SBM-API | Internal platform API | API | Critical, contractual and administrative platform operations | Python | Django REST Framework | N/A | container | SBM-API |
| SBM | sbm-ai-assistant | AI orchestrator | API / AI service | Intent routing, RAG, embeddings and explicit Tools | Python | FastAPI | N/A | container | sbm-ai-assistant |
| SBM | sbm-ai-assistant | Qdrant | vector database | Semantic indexes for documents, contexts and documentation | Rust service | Qdrant | N/A | container | sbm-ai-assistant |
| SBM | QA infrastructure | SonarQube | quality service | Static analysis and quality gates | Java service | SonarQube | N/A | container | QA workflow |

## 6. Technology inventory

| Brand | Project | Category | Technology | Version | Purpose | Status |
|---|---|---|---|---|---|---|
| SBM | SBM-MANAGER | web frontend | Vue.js 3 | N/A | Enterprise web interface | active |
| Ditaly Pasta | DP-API | backend | Python | N/A | API implementation | active |
| Ditaly Pasta | DP-API | backend framework | Django REST Framework | N/A | REST API | active |
| SBM | SBM-API | backend | Python | N/A | Internal API implementation | active |
| SBM | SBM-API | backend framework | Django REST Framework | N/A | Internal REST API | active |
| SBM | sbm-ai-assistant | backend | Python | N/A | AI orchestration | active |
| SBM | sbm-ai-assistant | backend framework | FastAPI | N/A | AI API | active |
| SBM | sbm-ai-assistant | vector database | Qdrant | N/A | Semantic retrieval | active |
| SBM | SBM-DB | database | PostgreSQL | N/A | Business and platform persistence | active |
| SBM | SBM-DB | migrations | Flyway | N/A | Versioned business-schema migrations | active |
| SBM | Shared infrastructure | containers | Docker Compose | N/A | Local orchestration | active |
| SBM | QA infrastructure | static analysis | SonarQube | N/A | Quality gates | active |

## 7. Runtime architecture

### Canonical relationship diagram

Legend:

```text
🟦 Web frontend
🟪 Mobile frontend
🟩 API / Backend
🟨 Middleware / AI
🟥 Database / Vector database
🟧 Infrastructure / Migration
⬜ External channel
```

```text
                              ┌───────────────────────────┐
                              │       USUARIOS SBM        │
                              └─────────────┬─────────────┘
                                            │
                         ┌──────────────────┴──────────────────┐
                         │                                     │
                         ▼                                     ▼
              ┌─────────────────────────┐          ┌─────────────────────────┐
              │ 🟦 SBM-MANAGER          │          │ ⬜ Slack / otros canales│
              │ Vue.js 3 · Front Web    │          │ Interfaces aprobadas    │
              └────────────┬────────────┘          └────────────┬────────────┘
                           │                                    │
                 ┌─────────┴─────────┐                          ▼
                 │                   │               ┌──────────────────────────┐
                 ▼                   ▼               │ 🟨 SBM-AI-ASSISTANT      │
       ┌──────────────────┐  ┌──────────────────┐    │ FastAPI · RAG · Tools   │
       │ 🟩 DP-API        │  │ 🟩 SBM-API       │◄───┤ API/tool orchestration  │
       │ Django / DRF     │  │ Django / DRF     │    └────────────┬─────────────┘
       │ Client operations│  │ Platform / Admin │                 │
       └─────────┬────────┘  └─────────┬────────┘                 ├────► 🟩 DP-API
                 │                     │                          │
                 └──────────┬──────────┘                          │ Vector API
                            │                                     ▼
                            ▼                          ┌──────────────────────────┐
                ┌───────────────────────────┐         │ 🟥 Qdrant                │
                │ 🟥 PostgreSQL · SBM-DB   │         │ sbm_docs                 │
                │                           │         │ sbm_contexts             │
                │ sbm_business              │         │ sbm_documentation        │
                │ ditaly_pasta              │         └──────────────────────────┘
                │ accounting                │
                │ analytics                 │
                │ public                    │
                └─────────────▲─────────────┘
                              │ schema / migrations
                              │
                ┌─────────────┴─────────────┐
                │ 🟧 Flyway · SBM-DB       │
                │ sbm_business             │
                │ ditaly_pasta             │
                │ cross · analytics        │
                └───────────────────────────┘
```

Diagram maintenance rules:

- This diagram is a canonical structural view, not a decorative snapshot.
- Update it whenever a structural change modifies a project, application, frontend, API, middleware, database, vector store, primary integration or ownership boundary.
- Preserve the semantic type markers and rectangle-based layout when updating it.
- Do not add planned components as active topology; mark them explicitly as planned or omit them until the relationship is evidenced.
- Keep the diagram consistent with `Project map`, `Applications and services`, `Integrations and data flows`, `Data architecture` and `Infrastructure and containers`.
- A non-structural implementation change does not require diagram modification.

Client-facing flow:

```text
Client user
→ SBM-MANAGER or approved client channel
→ DP-API
→ validated domain operation
→ PostgreSQL
```

Internal platform flow:

```text
Internal SBM user
→ SBM-MANAGER or approved internal channel
→ SBM-API
→ platform operation
→ PostgreSQL
```

AI-assisted flow:

```text
User
→ Slack / approved channel
→ sbm-ai-assistant
→ explicit Tool
→ DP-API or SBM-API
→ structured result
```

Context flow:

```text
Project Git evidence
→ context-deploy.sh
→ sbm-ai-assistant
→ Qdrant sbm_contexts
→ RAG package
→ ChatGPT
→ context-upgrade.zip
→ context-upgrade.sh
→ validated section patches
```

Documentation flow:

```text
Updated contexts + Git documentation
→ documentation-deploy.sh
→ Qdrant sbm_documentation
→ documentation package
→ ChatGPT
→ documentation-upgrade.zip
→ documentation-upgrade.sh
→ validated Markdown replacement
```

## 8. Data architecture

Relevant schemas currently include:

| Database | Schema | Owner project | Brand | Purpose | Migration owner | Status |
|---|---|---|---|---|---|---|
| PostgreSQL | ditaly_pasta | SBM-DB | Ditaly Pasta | Brand operational and commercial data | Flyway | active |
| PostgreSQL | sbm_business | SBM-DB | SBM | Shared platform and business references | Flyway | active |
| PostgreSQL | public | SBM-DB | SBM | Shared technical objects where applicable | Flyway | active |

Rules:

- SBM-DB and Flyway own business schema changes.
- Application models map existing tables.
- Application repositories must not generate business-schema migrations unless explicitly authorized.
- DBML, Flyway and runtime schema must remain synchronized.
- Detailed data ownership belongs in `DATA_CONTEXT.md`.

## 9. API inventory

| Brand | API | Owner project | Base path | Audience | Authentication | Description | Status |
|---|---|---|---|---|---|---|---|
| Ditaly Pasta | DP-API | DP-API | `/api` | Authorized client users | Required | Client-facing business operations | active |
| SBM | SBM-API | SBM-API | `/api` | Internal SBM users and services | Required | Internal platform administration | active |
| SBM | sbm-ai-assistant | sbm-ai-assistant | `/` | Approved channels and internal integrations | Endpoint-specific | AI orchestration and context services | active |

## 10. Endpoint contracts

| Brand | API | Method | Path | Request body | Response | Authentication | Purpose | Status |
|---|---|---|---|---|---|---|---|---|
| SBM | sbm-ai-assistant | GET | `/health` | none | health status | N/A | Service health check | implemented |
| SBM | sbm-ai-assistant | POST | `/contexts/export` | context export request | ZIP export metadata | Required by environment | Generate RAG context package | implemented |
| SBM | sbm-ai-assistant | POST | `/contexts/upgrade` | context upgrade ZIP | upgrade result and commit message | Required by environment | Validate and apply context patches | implemented |
| SBM | sbm-ai-assistant | POST | `/confluence/pages/{id}/ingest` | ingestion request | ingestion result | Required by environment | Ingest one Confluence page | implemented |
| SBM | sbm-ai-assistant | POST | `/confluence/ingest` | ingestion request | ingestion result | Required by environment | Ingest Confluence content | implemented |
| SBM | sbm-ai-assistant | POST | `/confluence/sync` | synchronization request | synchronization result | Required by environment | Synchronize Confluence content | implemented |
| SBM | sbm-ai-assistant | POST | `/slack/test` | Slack test payload | test result | Required by environment | Validate Slack integration | implemented |
| SBM | sbm-ai-assistant | POST | `/slack/rag` | Slack RAG query | assistant response | Slack validation | Execute RAG response | implemented |
| SBM | sbm-ai-assistant | POST | `/slack/events` | Slack event body | acknowledgement / response | Slack signature | Receive Slack events | implemented |
| Ditaly Pasta | DP-API | GET | `/api/products` | none | product collection | Required | List products | implemented |
| Ditaly Pasta | DP-API | POST | `/api/products` | product payload | created product | Required | Create product | implemented |
| Ditaly Pasta | DP-API | GET | `/api/products/{id}` | none | product detail | Required | Retrieve product | planned |
| Ditaly Pasta | DP-API | PATCH | `/api/products/{id}` | partial product payload | updated product | Required | Update product | planned |
| Ditaly Pasta | DP-API | DELETE | `/api/products/{id}` | none | deletion result | Required | Soft-delete product | planned |

Any endpoint creation, removal, path change, method change, request body change or response change must update this table.

## 11. Authentication and authorization

Cross-suite resolution target:

```text
identity
→ tenant or franchise
→ contracted modules
→ role
→ permission
→ restriction
→ requested object
→ validated action
```

Rules:

- Client and internal credentials remain separated.
- Tenant isolation requires explicit enforcement.
- Object-level permissions must be validated.
- AI-triggered actions require the same authorization as direct user actions.
- Internal platform operations must not be exposed through DP-API.
- Detailed security controls belong in `SECURITY_CONTEXT.md`.

## 12. Integrations and data flows

| Source | Target | Contract | Purpose | Status |
|---|---|---|---|---|
| SBM-MANAGER | DP-API | REST API | Client business operations | active |
| SBM-MANAGER | SBM-API | REST API | Internal platform operations | active |
| sbm-ai-assistant | DP-API | Explicit Tool / REST API | AI-assisted client operations | planned |
| sbm-ai-assistant | SBM-API | Explicit Tool / REST API | AI-assisted internal operations | planned |
| DP-API | PostgreSQL | ORM / approved data access | Business persistence | active |
| SBM-API | PostgreSQL | ORM / approved data access | Platform persistence | active |
| sbm-ai-assistant | Qdrant | Vector API | Semantic retrieval | active |
| sbm-ai-assistant | Confluence | REST API | Documentation ingestion | active |
| sbm-ai-assistant | Slack | Events API | Assistant interface | active |
| Context workflow | ChatGPT | ZIP + SYS_PROMPT | Reviewed context generation | active |
| Documentation workflow | ChatGPT | ZIP + SYS_PROMPT | Reviewed documentation generation | planned |

Current `SBM-MANAGER-002` evidence confirms that Service, Catalog and Provider client-owned frontend flows use `dpApi`; franchise lookup remains on `sbmApi` as an internal/platform operation.

Cross-project communication must use explicit APIs or contracts. Direct repository imports and uncontrolled shared writes are prohibited.

## 13. Infrastructure and containers

| Component | Container or service | Internal port | Host port | Network | Status |
|---|---|---:|---:|---|---|
| SBM-MANAGER | app / sbm_manager | 8080 | 8080 | sbm-network | active |
| DP-API | dp-core | 8000 | 8081 | sbm-network | active |
| SBM-API | sbm-core | 8000 | 8082 | sbm-network | active |
| sbm-ai-assistant | backend | 8000 | 8000 | sbm-network | active |
| Qdrant | qdrant | 6333 | 6333 | sbm-network | active |
| PostgreSQL | postgres | 5432 | 5432 | sbm-network | active |
| Flyway | flyway | N/A | N/A | sbm-network | active |
| SonarQube | sonarqube | N/A | N/A | independent/shared as configured | active |

Do not assume current names, ports or versions without checking the project Compose files.

## 14. Shared configuration

Shared configuration rules:

- secrets and `.env` values must remain outside Git and ZIP packages;
- project-specific environment files own local runtime values;
- `SBM-MANAGER` uses canonical repository root `SBM-SUITE/sbm/SBM-MANAGER/` and runtime root `/suite/sbm/SBM-MANAGER`;
- `SBM-DB` uses canonical repository root `SBM-SUITE/sbm/SBM-DB/` and runtime root `/suite/sbm/SBM-DB`;
- project context scripts resolve the absolute suite root from `SBM_SUITE_ROOT`;
- suite-level context contracts, prompts, input, output and project-tree artifacts are resolved below `SBM-SUITE/context`;
- container requests use repository paths mounted below `/suite`, including `/suite/<brand>/<project>` for project roots;
- context packages may include metadata but never secret values;
- repository-relative paths are required in manifests and documentation references;
- context and documentation collections remain separated;
- project, brand, document type, path, version and content hash must be available as retrieval filters.

## 15. Context and knowledge architecture

Qdrant collections:

| Collection | Owner | Content | Purpose |
|---|---|---|---|
| `sbm_docs` | sbm-ai-assistant | Confluence documentation | Assistant knowledge |
| `sbm_contexts` | sbm-ai-assistant | Global and project contexts | Context RAG |
| `sbm_documentation` | sbm-ai-assistant | Git documentation pages | Documentation RAG |

Rules:

- collections remain separate;
- vectors are never exported;
- Git Markdown is the source of truth;
- Qdrant is a rebuildable semantic index;
- context packages contain selected RAG chunks, bounded evidence, the format contract and complete authorized source snapshots;
- complete source snapshots are input-only and must never appear in the generated upgrade ZIP;
- generated upgrades contain validated section-level JSON patches rather than complete target documents;
- documentation packages use documentation chunks and updated contexts only in the separate documentation workflow.

Current context evidence includes Git diff, changed files, change summary, QA results, project tree, retrieved Qdrant chunks and full current snapshots for authorized targets. Contract version and canonical project mappings are validated before export and upgrade.

## 16. Deployment model

Current stage:

```text
manual validated workflow
```

Future stage:

```text
database configuration flags
→ asynchronous orchestration
→ automatic context and documentation processing
```

Current deployment principles:

- one validated step at a time;
- Docker-based local services;
- backup before replacement;
- manifest and hash validation;
- atomic application or rollback;
- no automatic Git commit or push unless requested.

## 17. Security rules

1. Secrets, credentials and tokens must never enter Git or generated ZIP files.
2. AI services must not write directly to business databases.
3. User identity, tenant and authorization context must be preserved.
4. API ownership must not be bypassed.
5. Internal and client operations remain separated.
6. CORS and development credentials must not be treated as production configuration.
7. Input ZIP paths, hashes and symlinks must be validated.
8. Context and documentation replacements require backups.
9. Detailed controls and risks belong in `SECURITY_CONTEXT.md`.

## 18. Operational constraints

- The workflow remains manual in the first stage.
- Context changes precede documentation changes.
- Documentation deploy uses updated contexts.
- Context and documentation upgrades produce one final commit message each.
- `git status` confirms changed files but not semantic correctness.
- Structural format changes require manual updates to format contracts.
- Structural architecture changes must also update the canonical relationship diagram in `## 7. Runtime architecture` and its related inventory tables.
- Unknown facts, versions, endpoint bodies and QA results must remain `N/A` or unchanged.
- No unrelated project files may be modified.

## 19. Current suite state

Current verified direction:

- SBM-MANAGER is the canonical Vue 3 web frontend consuming DP-API and SBM-API through explicit frontend clients.
- SBM-MANAGER context, QA and lifecycle scaffolding is present; current implementation-progress QA reports 45/45 tests passed, 70.14% coverage and server-side SonarQube Quality Gate PASSED while SBM-MANAGER-002 remains active.
- SBM-DB is the canonical PostgreSQL/Flyway authority; project context, QA/lifecycle scaffolding and canonical routing are defined, and the current transversal without-Sonar queue records its project QA entrypoint as passed.
- Product is the accepted DP-API reference vertical.
- Material is separated into its own domain app.
- Service is a planned backend domain.
- Catalog and Ticket remain future domains.
- Context contract, export and upgrade endpoints exist.
- Context RAG uses `sbm_contexts`.
- Section-level patch output and complete input-only source snapshots are implemented.
- Global Project, Suite, Business, QA, Security, Data and Decisions contexts exist.
- `project-tree.txt` is generated and packaged as structural evidence.
- `SBM-SUITE/context/QA` provides centralized Context QA, per-project QA dispatch and all-project queue orchestration while preserving project-owned QA entrypoints.
- the current `OBJ-CTX-014` implementation-progress evidence records all five project repositories passed in `without-sonar` mode and Context QA passed; this evidence does not close the objective.
- `implementation-progress` for `sbm-suite-context` validates transversal summary/queue evidence and normalizes verified QA evidence into the generated context package.
- Documentation lifecycle and `sbm_documentation` remain separate follow-up work.

Validated workflow state:

- context deployment validates the published contract before cleaning exchange outputs;
- lifecycle phase and objective ID are explicit and are not inferred from implementation evidence;
- implementation closure requires five synchronized objective and QA patches;
- context upgrade preflights ZIP members, manifest metadata and patch mappings before backend submission;
- `qa-check.sh` creates bounded execution evidence in `context/qa-results.md`;
- the supplied DP-API evidence records 65 passing tests, 88% configured coverage and successful SonarScanner execution;
- the supplied scanner log does not include a server-side Quality Gate result.

## 20. Context deployment lifecycle

Run all lifecycle orchestration from the root of `SBM-SUITE/context`.

```text
<selected-project>/scripts/qa-check.sh
→ when present, QA is applicable and closure requires canonical successful execution evidence
→ when absent, closure QA is structurally `not-applicable`
→ missing or failed evidence for an applicable QA workflow blocks closure

./scripts/context-deploy.sh <project_name> <lifecycle_phase> <objectives-json-array> [user_prompt]
→ validate the selected project through the backend Project Registry
→ dispatch planning-activation, objective-activation, implementation-progress and implementation-closure by exact literal equality
→ reserve planning-activation for new objectives
→ reserve objective-activation for exactly one existing pending → active transition
→ preserve active/pending state during implementation-progress
→ reserve active → completed exclusively for implementation-closure
→ request GET /contexts/contract before exchange-directory cleanup
→ generate project-tree.txt through ./scripts/project-tree.sh
→ collect Git evidence and canonical QA evidence from the registry-resolved project root
→ for sbm-suite-context implementation-progress, optionally validate QA/output/qa-all-without-sonar-results.md with its queue and include Context QA evidence when present
→ normalize verified progress QA into qa-results.md and the inner context-package manifest without applying closure semantics
→ call POST /contexts/export
→ package bounded evidence and complete authorized source snapshots
→ generate context-package.zip, context-export-response.json and parameterized SYS_PROMPT.md

review process
→ read FORMAT_CONTEXT.md, the source manifest, evidence and applicable complete snapshots
→ generate only authorized section-level JSON patches
→ preserve the source-manifest QA decision literally during implementation-closure
→ use append_to_section only when the canonical completed-objective project group is absent
→ use replace_section when that completed-objective project group already exists
→ generate manifest.json from the final ZIP contents only

./scripts/context-upgrade.sh
→ require exactly one context-upgrade.zip
→ request GET /contexts/contract
→ inspect manifest.json before extraction
→ reject unsafe, unsupported or phase-incompatible files
→ for sbm-suite-context closure require global-project-context, completed-objectives and global-qa-context patches and forbid project-scoped patches
→ for project-scoped closure additionally require project-context and project-qa-context patches
→ recalculate QA applicability from repository-relative scripts/qa-check.sh and require exact agreement with manifest.qa
→ call POST /contexts/upgrade only after local preflight succeeds
→ create SBM-SUITE/context/backup/<timestamp>_<project>/
→ apply authorized patches atomically and roll back on failure
→ remove the input ZIP only after complete success
```

The backend remains the authoritative validation, backup, replacement and rollback boundary. Client preflight rejects invalid archives earlier but does not replace backend validation.

## 21. Documentation lifecycle

Run Documentation globally from the root of `SBM-SUITE/context`; do not select or pass a project.

```text
1. complete the applicable Context upgrade
2. refresh the loaded context state before any state-reading menu is reused
3. ./scripts/documentation-deploy.sh
4. reconcile global Context objective lifecycle against canonical objective rows in all functional Documentation pages
5. ignore narrative lifecycle words and reject conflicting canonical duplicate objective states
6. if Documentation is already synchronized, remove stale deploy artifacts, write a no-op response, generate no package and stop successfully
7. if real differences exist, index/retrieve the required global documentation candidates and generate documentation-package.zip
8. review the generated package and create documentation-upgrade.zip only from real functional document targets
9. place the ZIP in documentation/input
10. ./scripts/documentation-upgrade.sh validates manifest/file equality and authorized Markdown targets
11. create a timestamped documentation backup under SBM-SUITE/context/backup/
12. replace validated documentation files
13. return the proposed commit message
14. refresh context.zip again before returning to any state-reading menu
```

Current rules:

- Git is the primary source of truth.
- Documentation reconciliation is global and never filters by an originator `project_name`.
- Lifecycle status is read only from canonical unfenced Markdown objective tables under the applicable exact `Current state`, `Pending work` or `Roadmap` section.
- Only existing pages and subpages authorized by the documentation format may be modified.
- Creation, deletion, rename or structural change requires explicit manual contract updates.
- Main pages are documents and must maintain subpage links.
- A synchronized no-op must not leave a previous `documentation-package.zip` reusable as a current result.
- Notion synchronization is downstream and planned for a later stage.
- `SBM-SUITE/context/backup/` is the single backup root for Context and Documentation workflows.

## 22. Related documentation

Documentation paths follow:

```text
SBM-SUITE/context/documentation/pages/<page>/<page>.md
SBM-SUITE/context/documentation/pages/<page>/subpages/<subpage>.md
```

Relevant documentation domains include:

- SBM Suite;
- Development;
- Roadmap;
- Technologies;
- Security and DevSecOps;
- QA and Testing;
- Observability;
- DevOps;
- Cloud;
- Automation;
- AI Engineering.

Specific paths must be recorded in project objectives and context references when the documentation tree is finalized.

## 23. Document boundary

This document defines the suite as a technical system.

It does not replace:

- project-specific `PROJECT_CONTEXT.md`;
- detailed project QA plans;
- global or project security evidence;
- data governance details;
- business metrics;
- ADR history;
- deployment instructions;
- documentation page content;
- live repository, runtime, API or database evidence.

When sources disagree, report the conflict and verify the current repositories and runtime before modifying code or context.
