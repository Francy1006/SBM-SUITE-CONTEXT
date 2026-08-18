# SUITE_CONTEXT.md

> **Last updated:** 2026-08-16
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
→ SBM-AI-ASSISTANT
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
| SBM | SBM Suite | Platform, infrastructure, shared services and control planes | active |
| Ditaly Pasta / DP | Client ERP reference | Closed business; one year real historical data retained as development/reference implementation | historical-reference |
| Kiseki Tech / KS | Brand platform | Technology import/sale; current production target | planned-onboarding |
| PortalConvenios.cl / PC | Brand platform | Health/wellness operations and referral services; current production target | planned-onboarding |
| Consorcio y Gestión / CG | Brand platform | Permit/procedure/document workflows; current production target | planned-onboarding |

`SBM` is treated as its own technical/platform brand. Planned brands do not imply existing repositories or schemas.

## 4. Project map

| Project | Brand | Primary responsibility | Canonical owner |
|---|---|---|---|
| DP-API | Ditaly Pasta | Client-facing business API | Client operations |
| SBM-MANAGER | SBM | Enterprise web frontend for client and platform interaction | Frontend |
| SBM-API | SBM | Internal platform API | Platform administration |
| SBM-DB | SBM | PostgreSQL business schemas and Flyway migrations | Data layer |
| SBM-AI-ASSISTANT | SBM | AI orchestration, RAG, embeddings and Tools | AI-assisted workflows |
| SBM-SUITE/context | SBM | Global context and documentation contracts | Context governance |

Canonical repository paths currently evidenced here include `SBM-SUITE/dp/DP-API/`, `SBM-SUITE/sbm/SBM-API/`, `SBM-SUITE/sbm/SBM-DB/`, `SBM-SUITE/sbm/SBM-MANAGER/` and `SBM-SUITE/sbm/sbm-ai-assistant/`. Canonical runtime roots preserve those brand segments as `/suite/dp/DP-API`, `/suite/sbm/SBM-API`, `/suite/sbm/SBM-DB`, `/suite/sbm/SBM-MANAGER` and `/suite/sbm/sbm-ai-assistant`.

## 5. Applications and services

### Existing/current repositories

| Brand | Project | Application or service | Type | Description | Runtime state |
|---|---|---|---|---|---|
| SBM | SBM-MANAGER | Enterprise web frontend | web frontend | Management UI consuming brand APIs and SBM-API | active |
| DP | DP-API | Historical/reference brand API | API | Real-data reference implementation; not a current production brand | active-reference |
| SBM | SBM-API | Shared platform API | API | Authentication, users, token, franchise, roles, permissions, restrictions and internal services | active |
| SBM | SBM-DB | Data/migration authority | database repository | PostgreSQL/DBML/Flyway authority; not runtime gateway | active |
| SBM | SBM-AI-ASSISTANT | AI orchestrator | AI/API service | RAG, Tools, agents and context/documentation processing | active |
| SBM | QA infrastructure | SonarQube | QA service | Static analysis/quality gates on demand | QA-only |

### Planned applications

See `## 23. Target multi-brand application portfolio — 2026-08-16` for the complete planned shared/brand project inventory.

## 6. Technology inventory

| Brand | Project | Category | Technology | Version | Purpose | Status |
|---|---|---|---|---|---|---|
| SBM | SBM-MANAGER | web frontend | Vue.js 3 | N/A | Enterprise web interface | active |
| Ditaly Pasta | DP-API | backend | Python | N/A | Historical/reference API implementation | active-reference |
| Ditaly Pasta | DP-API | backend framework | Django REST Framework | N/A | Historical/reference REST API | active-reference |
| SBM | SBM-API | backend | Python | N/A | Internal API implementation | active |
| SBM | SBM-API | backend framework | Django REST Framework | N/A | Internal REST API | active |
| SBM | SBM-AI-ASSISTANT | backend | Python | N/A | AI orchestration | active |
| SBM | SBM-AI-ASSISTANT | backend framework | FastAPI | N/A | AI API | active |
| SBM | SBM-AI-ASSISTANT | vector database | Qdrant | N/A | Semantic retrieval | active |
| SBM | SBM-DB | database | PostgreSQL | N/A | Business and platform persistence | active |
| SBM | SBM-DB | migrations | Flyway | N/A | Versioned business-schema migrations | active |
| SBM | Shared infrastructure | containers | Docker Compose | N/A | Local orchestration | active |
| SBM | QA infrastructure | static analysis | SonarQube | N/A | Quality gates on demand | QA-only |

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
→ SBM-AI-ASSISTANT
→ explicit Tool
→ DP-API or SBM-API
→ structured result
```

Context flow:

```text
Project Git evidence
→ context-deploy.sh
→ SBM-AI-ASSISTANT
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
| PostgreSQL | ditaly_pasta | SBM-DB | Ditaly Pasta | Historical/reference operational and commercial data | Flyway | active-reference |
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
| Ditaly Pasta | DP-API | DP-API | `/api` | Authorized reference/dev users | Required | Historical/reference business operations | active-reference |
| SBM | SBM-API | SBM-API | `/api` | Internal SBM users and services | Required | Internal platform administration | active |
| SBM | SBM-AI-ASSISTANT | SBM-AI-ASSISTANT | `/` | Approved channels and internal integrations | Endpoint-specific | AI orchestration and context services | active |

## 10. Endpoint contracts

| Brand | API | Method | Path | Request body | Response | Authentication | Purpose | Status |
|---|---|---|---|---|---|---|---|---|
| SBM | SBM-AI-ASSISTANT | GET | `/health` | none | health status | N/A | Service health check | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/contexts/export` | context export request | ZIP export metadata | Required by environment | Generate RAG context package | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/contexts/upgrade` | context upgrade ZIP | upgrade result and commit message | Required by environment | Validate and apply context patches | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/confluence/pages/{id}/ingest` | ingestion request | ingestion result | Required by environment | Ingest one Confluence page | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/confluence/ingest` | ingestion request | ingestion result | Required by environment | Ingest Confluence content | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/confluence/sync` | synchronization request | synchronization result | Required by environment | Synchronize Confluence content | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/slack/test` | Slack test payload | test result | Required by environment | Validate Slack integration | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/slack/rag` | Slack RAG query | assistant response | Slack validation | Execute RAG response | implemented |
| SBM | SBM-AI-ASSISTANT | POST | `/slack/events` | Slack event body | acknowledgement / response | Slack signature | Receive Slack events | implemented |
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

```text
Public/store/mobile/client/customer channels
→ responsible brand API

SBM-MANAGER / SBM-MOBILE
→ brand APIs for brand-owned operations
→ SBM-API for shared platform/identity operations

Brand APIs
→ SBM-DB-owned schemas through application persistence
→ SBM-CALCULATION for reusable financial calculations
→ SBM-CORE for durable async workflows
→ SBM-UTIL for deterministic external integrations

SBM-AI-ASSISTANT
→ explicit Tools/agents
→ canonical APIs/services
→ never direct PostgreSQL writes

SBM-CONTROL / SBM-SECURITY / SBM-AI-MANAGER
→ privileged control-plane APIs
→ observe/manage their bounded domains, not business ownership
```

Future KS/PC/CG repositories must not be treated as canonical integrations until onboarding creates and registers them. Cross-brand analytics must use approved APIs/events/read models rather than SBM-DB as a runtime query gateway.

## 13. Infrastructure and containers

| Component | Container or service | Internal port | Host port | Network | Status |
|---|---|---:|---:|---|---|
| SBM-MANAGER | app / sbm_manager | 8080 | 8080 | sbm-network | active |
| DP-API | dp-core | 8000 | 8081 | sbm-network | active |
| SBM-API | `SBM-CORE` (legacy runtime name; rename pending) | 8000 | 8082 | sbm-network | active |
| SBM-AI-ASSISTANT | backend | 8000 | 8000 | sbm-network | active |
| Qdrant | qdrant | 6333 | 6333 | sbm-network | active |
| PostgreSQL | postgres | 5432 | 5432 | sbm-network | active |
| Flyway | flyway | N/A | N/A | sbm-network | active |
| SonarQube | sonarqube | N/A | N/A | independent/shared as configured | QA-only/on-demand |

Do not assume current names, ports or versions without checking the project Compose files.

Runtime naming constraint:

- the current SBM-API runtime/service is documented as `sbm-core`;
- the new asynchronous platform project is also named `SBM-CORE`;
- `SBM-API-002` must rename the legacy SBM-API runtime/container/service before onboarding the new project to avoid Docker/DNS/service-name collision.


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
| `sbm_docs` | SBM-AI-ASSISTANT | Confluence documentation | Assistant knowledge |
| `sbm_contexts` | SBM-AI-ASSISTANT | Global and project contexts | Context RAG |
| `sbm_documentation` | SBM-AI-ASSISTANT | Git documentation pages | Documentation RAG |

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

Planned governance integrations:

```text
Documentation Markdown (Git source of truth)
→ SBM-UTIL / Notion API
→ Notion page projection

Objectives (Context source of truth)
→ SBM-UTIL / Jira API
→ Project → Epic → Issue/Task backlog
→ future Scrum Agent management

SBM_AGENT.md
→ minimal new-chat bootstrap
→ consumes INIT_CONTEXT.md
```

Cross-project tooling is implemented under `SBM-SUITE/context`. It discovers physical repositories through `scripts/suite-repositories.py`, reads the explicit `shared/artifacts.json` allowlist, supports read-only `check` and explicit `apply` for one, several or all repositories, rejects dirty target repositories before mutation and never overwrites unmarked project-specific content. Standard project onboarding registers repo/local path, Context, Documentation, QA, Security, Git lifecycle and optional `__BASE-*` lineage.

The transversal Git Flow policy is implemented once in `scripts/git-flow-policy.py`: every temporary branch type starts from `main`, carries an atomic 1..N objective batch across one or more projects, requires complete QA plus updated Documentation, merges with `--no-ff` directly into `main`, returns every involved repository to `main`, and is removed locally/remotely. Fast-track lifecycle transitions may omit intermediate states but never QA or Documentation.


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
QA/qa-full.sh
→ every lifecycle batch requires canonical full-suite successful execution evidence before finalization
→ `not-applicable`, missing, stale or failed evidence blocks finalization

./scripts/context-deploy.sh <project_name> <lifecycle_phase> <objectives-json-array> [user_prompt]
→ validate the selected project through the backend Project Registry
→ dispatch planning-activation, objective-activation, objective-registration, objective-completion, objective-deletion, objective-update, implementation-progress and implementation-closure by exact literal equality
→ reserve planning-activation for new objectives
→ reserve objective-activation for one or more existing pending → active transitions validated and applied atomically
→ preserve active/pending state during implementation-progress
→ support atomic registration, completion, deletion and allowed pending/active updates without forced intermediate states
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
- Notion synchronization is downstream: OBJ-CTX-042 publishes controlled Git/Markdown changes to Notion while Git remains the source of truth; bidirectional sync is deferred.
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

## 23. Target multi-brand application portfolio — 2026-08-16

### Brand state

| Brand | State | Role |
|---|---|---|
| DP / Ditaly Pasta | historical-reference | Real-data development/reference implementation; closed business |
| KS / Kiseki Tech | production-target | Technology import/sale; rental deferred |
| PC / PortalConvenios.cl | production-target | Health/wellness operations and referrals |
| CG / Consorcio y Gestión | production-target | Permits, sanitary resolutions, premises enablement and procedure workflows |

### Shared platform projects

| Project | State | Responsibility |
|---|---|---|
| __BASE-FRANCHISE-API | planned | Python/Django REST canonical base for brand APIs and controlled inheritance |
| __BASE-STORE | planned | Reusable store/web base |
| __BASE-MOBILE | planned | Reusable React Native brand-user mobile base |
| __BASE-CLIENT | planned | Reusable client application base |
| __BASE-CUSTOMER | planned | Reusable customer application base |
| SBM-MANAGER | existing | Enterprise management frontend |
| SBM-API | existing | Auth/users/tokens/franchise/roles/permissions/restrictions/platform |
| SBM-DB | existing | Flyway/DBML/PostgreSQL authority; no runtime data gateway |
| SBM-AI-ASSISTANT | existing | RAG, Tools and agent orchestration |
| SBM-CORE | planned | Scheduler/cron, state flags DB, Celery/Redis, retries/idempotency, optional Kafka |
| SBM-CALCULATION | planned | Financial/accounting calculation engine, tax/currency/commission/provision formulas |
| SBM-UTIL | planned | Spring Boot deterministic integrations/utilities, email/files/external APIs/exchange-rate ingestion |
| SBM-AI-MANAGER | planned | Agent management/control plane |
| SBM-SECURITY | planned | Human Security findings/scans/evidence/risk/approval control plane |
| SBM-SECURITY-API | planned | Go/Gin/PostgreSQL isolated Security API for tool runs, pentests, findings, evidence, policy and approvals |
| SBM-MARKETING | planned | Node.js/TypeScript/NestJS API for social data, SEO, campaigns, scheduling, production sessions, promotion payments, equipment rental and contracted marketing services |
| SBM-CONTENT | planned | Python/FastAPI assets, production/generation/editing workflows and creative-tool integrations |
| SBM-CONTROL | planned | Suite operations control plane: status/logs/jobs/context/QA/security/deploys/backups |
| SBM-MOBILE | planned | React Native channel for SBM User |

### Brand projects/channels

| Brand | API | Store | Brand-user mobile | Client app | Customer app |
|---|---|---|---|---|---|
| DP | DP-API (reference) | N/A current | N/A current | N/A current | N/A current |
| KS | KS-API ← __BASE-FRANCHISE-API | KS-STORE ← __BASE-STORE | KS-MOBILE ← __BASE-MOBILE | KS-CLIENT ← __BASE-CLIENT | store/public channels as required |
| PC | PC-API ← __BASE-FRANCHISE-API | PC-STORE ← __BASE-STORE | PC-MOBILE ← __BASE-MOBILE | PC-CLIENT ← __BASE-CLIENT | PC-CUSTOMER ← __BASE-CUSTOMER |
| CG | CG-API ← __BASE-FRANCHISE-API | CG-STORE ← __BASE-STORE | CG-MOBILE ← __BASE-MOBILE | CG-CLIENT ← __BASE-CLIENT | store/public channels as required |

All planned project paths remain non-canonical until onboarding creates the repositories and registry entries.

### Canonical naming, reusable bases and selected technologies

Canonical application/project display names are uppercase. Existing repository paths, Docker identifiers and backend registry IDs remain literal operational identifiers until an explicit migration changes them.

```text
DP-API + SBM-API
→ stabilize and validate integration (DP-ARCH-001)
→ generate __BASE-FRANCHISE-API from validated DP-API (BASE-FRANCHISE-001)
→ parameterize common/optional franchise capabilities
→ register DP-API as first controlled derived API
→ create KS-API / PC-API / CG-API from __BASE-FRANCHISE-API

__BASE-STORE         → KS-STORE / PC-STORE / CG-STORE
__BASE-MOBILE        → KS-MOBILE / PC-MOBILE / CG-MOBILE
__BASE-CLIENT        → KS-CLIENT / PC-CLIENT / CG-CLIENT
__BASE-CUSTOMER      → PC-CUSTOMER and future customer channels
```

Derived projects record base project/version/commit, last inherited version, inheritance status, enabled/disabled optional modules and explicit divergences. Base changes are propagated through controlled diff/adaptation with agent review, QA, Security and rollback. Yeoman is an allowed candidate for initial scaffolding/generation only; ongoing BASE→derived synchronization is owned by SBM tooling and Git/agent validation, not Yeoman.

Selected planned technologies: `SBM-CALCULATION` = Python/FastAPI/pandas/scikit-learn/statsmodels; `SBM-MARKETING` = Node.js/TypeScript/NestJS; `SBM-CONTENT` = Python/FastAPI; `SBM-SECURITY-API` = Go/Gin/PostgreSQL.

## 24. Runtime responsibility boundaries

```text
Public/brand channels
→ responsible brand API
→ business persistence owned structurally by SBM-DB/Flyway

Shared auth/platform
→ SBM-API

Async jobs/events
→ SBM-CORE

Security domain API / evidence / approvals
→ SBM-SECURITY-API

Financial/accounting calculations
→ SBM-CALCULATION

Deterministic external integrations
→ SBM-UTIL

Agent reasoning/orchestration
→ SBM-AI-ASSISTANT

Operational visibility/control
→ SBM-CONTROL / SBM-SECURITY / SBM-AI-MANAGER
```


### Named-agent and Security runtime boundaries

`SBM-AI-ASSISTANT` hosts governed named agents. `SBM Agent` and `Scrum Agent` coordinate activation/dependencies; deterministic APIs/services/jobs/cron remain preferred when reasoning is unnecessary. Security is led by `Batman Agent`; Development by `Tesla Agent` with independent `Edison Agent` review; `Igor Agent` owns technical QA/DevOps/SRE; `Armstrong Agent` coordinates deploy/release. `Snape Agent` remains an independent `sbm-admin` auditor outside Batman's operational Security chain.

Canonical named-agent catalog:

| N° | Agent | Gobierno | Responsabilidad | Apps / fuentes |
|---:|---|---|---|---|
| 1 | CEO Agent | Primordial | Dirección estratégica, decisiones y autorizaciones finales. | sbm-admin ; SBM-MANAGER ; reportes |
| 2 | SBM Agent | Primordial | Orquesta y consolida procesos, dominios, agentes y marcas. | SBM-CORE ; Control API ; SBM-MANAGER ; sbm-admin |
| 3 | CFO Agent | CEO | Evalúa finanzas, tecnología, riesgos y autorizaciones económicas. | sbm-admin ; Finanzas ; Procurement ; reportes |
| 4 | Snape Agent | sbm-admin | Audita independientemente al CEO y escala desviaciones. | sbm-admin ; audit logs ; reportes ; Context/Documentation |
| 5 | Jarvis Agent | CEO | Asiste al CEO con síntesis, métricas, decisiones y seguimiento. | sbm-admin ; Galileo/read-model ; reportes |
| 6 | Spock Agent | CFO | Analiza trade-offs, riesgos y costo/beneficio para CFO. | Finanzas ; Sherlock ; Nostradamus ; sbm-admin |
| 7 | Scrum Agent | SBM | Coordina procesos asíncronos, prioridades, dependencias y activaciones IA. | SBM-CORE ; Control API ; Jira ; SBM-MANAGER |
| 8 | Sherlock Agent | SBM | Investiga tecnologías, amenazas, normativa, tendencias y evidencia nueva. | Web/search ; Knowledge Base ; Context ; Documentation |
| 9 | Nostradamus Agent | SBM | Realiza forecasting y predicciones estadísticas transversales. | Galileo/read-model ; históricos ; SBM-CORE |
| 10 | Darwin Agent | SBM | Entrena, evalúa, fine-tunea y mejora continuamente los agentes. | SBM-AI-ASSISTANT ; eval pipelines ; Sherlock ; Nostradamus |
| 11 | Tesla Agent | CFO + CEO | Diseña e implementa desarrollos autorizados. | Git repos ; CI ; project APIs ; SBM-CORE |
| 12 | Edison Agent | CFO | Desafía independientemente las decisiones tecnológicas de Tesla. | Git repos ; CI ; Sherlock ; Nostradamus |
| 13 | Igor Agent | Tesla | QA técnico, DevOps/SRE, infraestructura y troubleshooting. | CI/CD ; tests ; cloud ; observabilidad |
| 14 | Armstrong Agent | Tesla + Robin | Coordina deploy, release, readiness y rollback. | CI/CD ; cloud deploy ; repos ; releases |
| 15 | Batman Agent | CEO + sbm-admin | Patrulla, anticipa ataques, encuentra fallos y exige mejoras. | SBM-SECURITY-API ; SBM-SECURITY ; logs ; SBM-CORE |
| 16 | Alfred Agent | Batman | Gestiona requerimientos de seguridad y garantiza QA/CIA. | SBM-MANAGER ; QA ; repos ; SBM-SECURITY |
| 17 | Robin Agent | Batman | Protege integridad funcional/data, backups y coherencia documental. | Context ; Documentation ; backups ; object storage |
| 18 | Gotham Agent | Robin + Batman | Detecta diferencias entre SBM-SUITE real, Context y Documentation. | Context ; Documentation ; repos ; service inventory |
| 19 | Joker Agent | Batman / Control API | Ejecuta Red Team y pentesting autorizado contra SBM-SUITE. | Security lab ; pentest tools ; SBM-SECURITY-API ; logs |
| 20 | Queen Agent | Joker / Control API | Administra ambientes, herramientas y QA técnico de Joker. | Security lab ; CI/CD ; tools/APIs |
| 21 | Darth Maul Agent | Batman | Threat hunting y atribución de atacantes reales. | SBM-SECURITY-API ; logs ; threat intel ; Joker outputs |
| 22 | Cerberus Agent | Batman | Trata correo y adjuntos como hostiles y controla cuarentena. | SBM-UTIL mail ; sandbox ; SBM-SECURITY-API |
| 23 | Hercules Agent | Cerberus + MacGyver | Normaliza contenido sanitizado a formatos seguros para agentes. | SBM-UTIL ; parsers ; object storage |
| 24 | Murphy Agent | CFO + CEO | Gestiona riesgo transversal y escenarios adversos. | Risk register ; Operations ; Finance ; Security reports |
| 25 | Abagnale Agent | CFO + Batman | Detecta fraude, falsificación, suplantación y patrones anómalos. | Payments ; identity logs ; finance data ; Galileo |
| 26 | L Agent | Snape + sbm-admin | Auditoría investigativa, evidencias y reconstrucción de hechos. | audit logs ; Context ; Documentation ; reports |
| 27 | Belfort Agent | CEO | Lidera estrategia de Marketing/Sales, campañas, tendencias y métricas. | SBM-MARKETING ; Google Analytics ; Search Console ; social APIs |
| 28 | Stratton Agent | Belfort | Mano técnica de Marketing: ambientes, integraciones, QA y desarrollos. | SBM-MARKETING ; CI/CD ; social APIs ; integrations |
| 29 | Donnie Agent | Belfort | Ejecuta canales, redes, chatbot y atención externa. | SBM-MARKETING ; social APIs ; chatbot ; messaging |
| 30 | DaVinci Agent | Belfort | Produce contenido creativo, visual, frontend y campañas. | Blender ; Photoshop ; frontend repos ; asset storage |
| 31 | Medici Agent | Belfort | QA creativo, estándares, patrones, consistencia y tendencias. | asset storage ; design systems ; Sherlock |
| 32 | WallStreet Agent | CEO | Gestiona ventas, revenue, pipeline, conversión y forecast. | CRM/Sales ; sbm-admin ; Galileo |
| 33 | Rockefeller Agent | CFO | Controla gastos, costos, consumo y cotizaciones. | Finance ; cloud billing ; Procurement ; sbm-admin |
| 34 | Buffett Agent | CFO | Presupuestos, proyecciones, austeridad y optimización de costos. | Finance ; pricing/cost sources ; sbm-admin |
| 35 | Burns Agent | CFO | Normativa contable/fiscal, monedas, UF/USD y estructuras. | SII ; Accounting ; FX/UF ; sbm-admin |
| 36 | Smithers Agent | Burns | Operación contable, facturas, respaldos y faltantes. | Accounting ; SII ; Records |
| 37 | Frink Agent | Burns | Tecnología, integraciones, ambientes y deploys contables. | Accounting integrations ; SBM-UTIL ; CI/CD ; Tesla |
| 38 | Midas Agent | CFO | Tesorería: caja, pagos, cobranza, conciliación y liquidez. | Finance ; bank/payment APIs ; Accounting |
| 39 | Galileo Agent | SBM + CEO | KPIs, analytics, calidad de datos y read-model multimarcas. | Data warehouse ; Analytics ; brand data |
| 40 | MacGyver Agent | SBM + Tesla | Integraciones, conectores, email, archivos y APIs determinísticas. | SBM-UTIL ; external APIs ; mail/files |
| 41 | Blackbeard Agent | CFO + Mario | Procurement, proveedores, OC, logística, aduana y supply chain. | Procurement ; supplier APIs/docs ; Logistics |
| 42 | Gringotts Agent | Mario | Gestiona inventario, stock, bodegas, equipos y activos. | Inventory/Assets ; warehouse data ; SBM-MANAGER |
| 43 | Hermione Agent | Robin | Records, documentos, assets, versionado, retención y archivo. | Object Storage ; Records ; Documentation |
| 44 | Sparrow Agent | Blackbeard + CEO | Investiga mercados, proveedores, rutas, riesgos y costos de importación. | Procurement/import ; research ; freight/customs |
| 45 | Barbossa Agent | Blackbeard + CEO | Gestiona importaciones, embarques, aduana, documentos y atrasos. | Import/Logistics ; customs/freight ; Procurement |
| 46 | Mario Agent | SBM | Gestiona operaciones, atrasos, procesos, cotizaciones, KPIs y estimaciones. | Operations ; SBM-MANAGER ; operational read-model |
| 47 | Luigi Agent | Mario | Genera diagramas, formatos, reportes y documentación operacional. | Operations ; diagram/report tools ; Documentation |
| 48 | Harvey Agent | CEO | Legal: contratos, riesgos jurídicos y análisis legal. | Legal docs ; contracts ; sbm-admin ; Hermione |
| 49 | Louis Agent | CEO | Compliance, controles, obligaciones y evidencia regulatoria. | Compliance ; audit logs ; regulatory sources ; sbm-admin |
| 50 | DP Agent | Admin DP + SBM Manager | Vela exclusivamente por los intereses de DP. | SBM-MANAGER ; sbm-admin |
| 51 | KS Agent | Admin KS + SBM Manager | Vela exclusivamente por los intereses de KS. | SBM-MANAGER ; sbm-admin |
| 52 | PC Agent | Admin PC + SBM Manager | Vela exclusivamente por los intereses de PC. | SBM-MANAGER ; sbm-admin |
| 53 | CG Agent | Admin CG + SBM Manager | Vela exclusivamente por los intereses de CG. | SBM-MANAGER ; sbm-admin |

Agents are capabilities, not permanently running processes. `Scrum Agent` plus the control/orchestration APIs decide activation based on process, priority and dependencies.

```text
QA PASS
→ authorized Security agents
→ SBM-SECURITY-API (Go/Gin/PostgreSQL)
→ SBM-CORE only for scheduling/job execution
→ local/docker/external Security tools
→ findings/evidence/risk/mitigation
→ SBM-SECURITY human review
→ APPROVE release | REJECT Development → QA → Security
```

Brand agents (`DP Agent`, `KS Agent`, `PC Agent`, `CG Agent`) protect only their brand interests and interact through SBM Manager / `sbm-admin`, not directly with specialist internal agents.

SBM-DB never becomes the query proxy for brand databases. Cross-brand analytics must be built through approved APIs/events or a dedicated read model.

## 25. Canonical item/commercial model target

```text
Product      purchased to sell
Material     purchased for operational consumption
Service      contracted/performed non-stock service
Equipment    retained/fixed asset (planned)
        ↓
Package      mandatory association for every item type; Service uses logical package
        ↓
Catalog      configurable BOM/recipe/composition with quantities/dosage
        ↓
Ticket       sold/reported/scheduled commercial unit
        ↓
Price        base amount → rules/FX/tax → net/gross
```

Ditaly validates recipe/dosage and franchise/internal movement patterns; KS extends the model to per-acquisition import cost composition; PC extends Ticket to scheduled/confirmed service settlement; CG extends Service/Catalog to staged document/procedure workflows.

Kiseki rental/contract/technical-service/spares is a future Equipment evolution and not current sale scope.

## 26. Document boundary

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
