# PROJECT_CONTEXT.md

> **Last updated:** 2026-08-16
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

SBM Suite groups shared platform services, brand APIs, business channels, data ownership, AI/agent orchestration, asynchronous processing, deterministic integrations, security, observability, QA and operational documentation under shared governance rules.

Current implemented/reference responsibilities:

```text
SBM-MANAGER
→ enterprise web frontend

DP-API
→ Ditaly Pasta historical/reference brand API and current reusable business baseline

SBM-API
→ shared identity, authorization and internal platform API

SBM-DB
→ PostgreSQL/DBML/Flyway authority; not a runtime query gateway

sbm-ai-assistant
→ AI orchestration, agents, RAG, context/documentation processing

SBM-SUITE/context
→ global governance, objectives, QA, security, data, decisions and documentation
```

Target production expansion:

```text
Brand APIs       → ks-api / pc-api / cg-api
Async platform   → sbm-core
Calculation      → sbm-calculation
Deterministic integrations → sbm-util
Agent UI         → sbm-ai-manager
Security UI      → sbm-security
Marketing        → sbm-marketing
Content          → sbm-content
Operations UI    → sbm-control
SBM mobile       → sbm-mobile
Stores           → ks-store / pc-store / cg-store
Brand-user mobile→ ks-mobile / pc-mobile / cg-mobile
Client channels  → ks-client / pc-client / cg-client
Customer channel → pc-customer
```

Ditaly Pasta is closed operationally but retains one year of real historical data and remains the reference implementation used to stabilize reusable business logic before adapting/cloning it for active brands. Kiseki Tech, PortalConvenios.cl and Consorcio y Gestión are the current production-target brands.

## 3. Active objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
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
| SBM-MANAGER-003 | SBM-MANAGER | Corregir y completar QA de SBM-MANAGER. | pending | 5 | N/A | BUGFIX-completes-manager-qa | N/A |
| SBM-MANAGER-004 | SBM-MANAGER | Extender la UI genérica para Equipment, Package obligatorio, composición/dosificación de Catalog y Price multimoneda sin duplicar lógica backend. | pending | 5 | N/A | FEATURE-expands-item-management | N/A |
| SBM-MANAGER-005 | SBM-MANAGER | Habilitar módulo de documentos y planos para CG con editor drag-and-drop, versionado/exportación e integración OCR/IA mediante servicios autorizados. | pending | 5 | N/A | FEATURE-enables-plan-editor | N/A |
| SBM-API-001 | SBM-API | Consolidar identidad/autorización multinivel para SBM User, Franchise/Brand User, Client User y Customer User cuando aplique, preservando franchise como alcance canónico de marca y roles/permisos/restricciones backend. | pending | 5 | N/A | FEATURE-expands-identity-model | N/A |
| SBM-API-002 | SBM-API | Renombrar el runtime/container legacy `sbm-core` usado actualmente por SBM-API para liberar el nombre del futuro proyecto `sbm-core` y evitar colisión de servicio/red. | pending | 5 | N/A | BUGFIX-renames-sbm-api-runtime | N/A |
| OBJ-DOC-001 | SBM-SUITE | Implement the manual documentation deploy and upgrade workflow with dedicated RAG and Qdrant collection | pending | 5 | N/A | FEATURE-adds-documentation-workflow | N/A |
| SBM-DB-002 | SBM-DB | Actualizar SBM-DB al contrato lifecycle actual de Context, incluyendo objectives[], execution_mode, preservación literal de objetivos y paths relativos. | pending | 5 | N/A | FEATURE-updates-context-lifecycle | N/A |
| SBM-DB-003 | SBM-DB | Definir e implementar la topología de datos multimarcas para SBM, DP histórico, KS, PC y CG con aislamiento lógico/credenciales, preservando SBM-DB como autoridad Flyway y no como gateway de consultas. | pending | 5 | N/A | FEATURE-defines-multibrand-data | N/A |
| SBM-DB-004 | SBM-DB | Agregar Equipment como dominio y formalizar Package obligatorio para Product, Material, Service, Equipment, Catalog y Ticket; Service usa un Package lógico no físico. | pending | 5 | N/A | FEATURE-adds-equipment-package | N/A |
| SBM-DB-005 | SBM-DB | Modelar Catalog como composición/BOM configurable con componentes Product, Material, Service y Equipment, cantidades/dosificación/unidades, manteniendo Ticket como unidad vendida/reportada. | pending | 5 | N/A | FEATURE-adds-catalog-components | N/A |
| SBM-DB-006 | SBM-DB | Extender Price para base_net_amount, net_amount, gross, IVA, impuestos adicionales, moneda y tipo de cambio versionado, incluyendo USD observado y futuras monedas/UF. | pending | 5 | N/A | FEATURE-adds-multicurrency-pricing | N/A |
| SBM-DB-007 | SBM-DB | Modelar trazabilidad de adquisición y movimiento: orden de compra, factura, IVA crédito, guía de despacho, traslado interno, venta a cliente/franquiciado, provisión y costo real. | pending | 5 | N/A | FEATURE-adds-procurement-trace | N/A |
| SBM-DB-008 | SBM-DB | Modelar costos de importación KS por compra/unidad: FOB, naviera, embarcador, aduana, desconsolidación, seguros, fletes, bodega, grúas, garantía, reposición y otros servicios instanciados por adquisición. | pending | 5 | N/A | FEATURE-adds-ks-import-costs | N/A |
| SBM-DB-009 | SBM-DB | Modelar PC para operativos y derivaciones: Client/Customer, agendamiento, QR, estados, comisión configurable, conciliación y suscripción mensual por máximo entre valor fijo y pacientes tratados. | pending | 5 | N/A | FEATURE-adds-pc-service-model | N/A |
| SBM-DB-010 | SBM-DB | Modelar CG para trámites, documentos, planos, etapas, dependencias, calendarización y proveedores externos, manteniendo datos/documentos sensibles con clasificación explícita. | pending | 5 | N/A | FEATURE-adds-cg-workflow-model | N/A |
| DP-ARCH-001 | DP-API | Consolidar DP-API como implementación histórica de referencia reutilizable para nuevas brand APIs, preservando data real de Ditaly Pasta y separando lógica genérica de particularidades de marca. | pending | 5 | N/A | FEATURE-prepares-brand-template | N/A |
| OBJ-CTX-002 | SBM-SUITE | Habilitar un sistema automatizado para ejecutar flujos transversales sobre uno o varios proyectos. | pending | 5 | N/A | FEATURE-automates-cross-project-flows | N/A |
| OBJ-CTX-003 | SBM-SUITE | Separar QA y Context mediante una estructura específica por proyecto. | pending | 5 | N/A | FEATURE-separates-qa-context | N/A |
| OBJ-CTX-004 | SBM-SUITE | Crear sbm-core para scheduler/cron, PostgreSQL de flags/estado, Celery, Redis, retries/idempotency y Kafka solo donde el patrón event-driven lo justifique; sin lógica financiera de negocio. | pending | 5 | N/A | FEATURE-enables-sbm-core | N/A |
| OBJ-CTX-005 | SBM-SUITE | Crear sbm-util como servicio reutilizable y desacoplado, preferentemente Java Spring Boot, para email, utilidades de archivos, APIs externas, conectores determinísticos y tipos de cambio oficiales consumidos por otros servicios/agentes. | pending | 5 | N/A | FEATURE-enables-sbm-util | N/A |
| OBJ-CTX-006 | SBM-SUITE | Habilitar un backlog-agent que convierta objetivos en issues/épicas y gestione Jira vía API. | pending | 5 | N/A | FEATURE-enables-backlog-agent | N/A |
| OBJ-CTX-007 | SBM-SUITE | Habilitar qa-agent para gestionar y automatizar procesos de validación de calidad. | pending | 5 | N/A | FEATURE-enables-qa-agent | N/A |
| OBJ-CTX-008 | SBM-SUITE | Habilitar un entorno y flujo de seguridad ejecutado después de QA y antes del commit/release. | pending | 5 | N/A | FEATURE-enables-security-flow | N/A |
| OBJ-CTX-009 | SBM-SUITE | Habilitar security-agent para ejecutar y gestionar validaciones del flujo de seguridad. | pending | 5 | N/A | FEATURE-enables-security-agent | N/A |
| OBJ-CTX-010 | SBM-SUITE | Crear sbm-ai-manager como frontend/control plane para registrar, visualizar, configurar y operar agentes; tecnología .NET/Blazor queda como candidata a validar al activar. | pending | 5 | N/A | FEATURE-enables-ai-manager | N/A |
| OBJ-CTX-011 | SBM-SUITE | Completar INIT_CONTEXT.md para soportar creación/onboarding de nuevos proyectos SBM. | pending | 5 | N/A | FEATURE-completes-project-onboarding | N/A |
| OBJ-CTX-012 | SBM-SUITE | Separar el flujo del agente en SBM_AGENT_INIT.md, dejando INIT_CONTEXT.md como punto de entrada y orquestación. | pending | 5 | N/A | FEATURE-separates-agent-init-flow | N/A |
| OBJ-CTX-015 | SBM-SUITE | Crear ks-api reutilizando la base validada de DP-API para venta/importación KS: Product/Material/Service/Catalog/Ticket, inventario, costos de importación, pricing multimoneda y trazabilidad; arriendo queda fuera del alcance inmediato. | pending | 5 | N/A | FEATURE-enables-ks-api | N/A |
| OBJ-CTX-016 | SBM-SUITE | Crear pc-api para operativos y derivaciones: agendamiento, Client/Customer, QR, confirmación, comisión, conciliación y suscripción mensual. | pending | 5 | N/A | FEATURE-enables-pc-api | N/A |
| OBJ-CTX-017 | SBM-SUITE | Crear cg-api para trámites, documentos, etapas, dependencias, calendarización, proveedores y planos. | pending | 5 | N/A | FEATURE-enables-cg-api | N/A |
| OBJ-CTX-018 | SBM-SUITE | Crear sbm-calculation como motor financiero/contable compartido para fórmulas, precios, monedas/tipos de cambio, impuestos, comisiones, provisiones, costos y conciliaciones. | pending | 5 | N/A | FEATURE-enables-sbm-calculation | N/A |
| OBJ-CTX-019 | SBM-SUITE | Crear sbm-security como frontend/control plane de findings, scans, vulnerabilidades, evidencias, aprobaciones e integración con security-agent. | pending | 5 | N/A | FEATURE-enables-sbm-security | N/A |
| OBJ-CTX-020 | SBM-SUITE | Crear sbm-marketing para datos/campañas/redes sociales, Meta API, métricas y operación de marketing-agent. | pending | 5 | N/A | FEATURE-enables-sbm-marketing | N/A |
| OBJ-CTX-021 | SBM-SUITE | Crear sbm-content para assets y workflows de generación/edición de contenido con content-agent e integraciones como Photoshop y Blender. | pending | 5 | N/A | FEATURE-enables-sbm-content | N/A |
| OBJ-CTX-022 | SBM-SUITE | Crear sbm-control como control plane global de SBM Suite: health/status, logs, métricas/reportes, cron/schedulers, workers/colas, Context/Objectives/Documentation, QA, Security, deploys, alertas y backups. | pending | 5 | N/A | FEATURE-enables-sbm-control | N/A |
| OBJ-CTX-023 | SBM-SUITE | Crear sbm-mobile en React Native para SBM User y operaciones administrativas aprobadas. | pending | 5 | N/A | FEATURE-enables-sbm-mobile | N/A |
| OBJ-CTX-024 | SBM-SUITE | Crear ks-store en React como vitrina/commerce pública de Tickets KS bajo dominio propio. | pending | 5 | N/A | FEATURE-enables-ks-store | N/A |
| OBJ-CTX-025 | SBM-SUITE | Crear pc-store en React como canal público de servicios/Tickets PC bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-pc-store | N/A |
| OBJ-CTX-026 | SBM-SUITE | Crear cg-store en React como canal público de servicios/Tickets CG bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-cg-store | N/A |
| OBJ-CTX-027 | SBM-SUITE | Crear ks-mobile en React Native para KS/Franchise User. | pending | 5 | N/A | FEATURE-enables-ks-mobile | N/A |
| OBJ-CTX-028 | SBM-SUITE | Crear pc-mobile en React Native para PC/Franchise User. | pending | 5 | N/A | FEATURE-enables-pc-mobile | N/A |
| OBJ-CTX-029 | SBM-SUITE | Crear cg-mobile en React Native para CG/Franchise User. | pending | 5 | N/A | FEATURE-enables-cg-mobile | N/A |
| OBJ-CTX-030 | SBM-SUITE | Crear ks-client para Client User KS, inicialmente control de inventario/equipos y derivación/visualización de cámara u otras capacidades autorizadas. | pending | 5 | N/A | FEATURE-enables-ks-client | N/A |
| OBJ-CTX-031 | SBM-SUITE | Crear pc-client para Client User PC, incluyendo gestión de operativos/derivaciones, agenda, QR/confirmaciones y conciliación operativa. | pending | 5 | N/A | FEATURE-enables-pc-client | N/A |
| OBJ-CTX-032 | SBM-SUITE | Crear pc-customer para PC Customer: ficha, QR, agendamiento, confirmación y seguimiento del servicio con tratamiento reforzado de datos personales/salud. | pending | 5 | N/A | FEATURE-enables-pc-customer | N/A |
| OBJ-CTX-033 | SBM-SUITE | Crear cg-client para seguimiento de etapas de tramitación, dependencias, documentos faltantes, información general y FAQ. | pending | 5 | N/A | FEATURE-enables-cg-client | N/A |
| OBJ-CTX-034 | SBM-SUITE | Expandir sbm-ai-assistant con sbm-agent como orquestador, dev-agent y agentes de marca ks-agent/pc-agent/cg-agent; integrar marketing-agent/content-agent y preservar objetivos específicos de backlog/QA/security agents. | pending | 5 | N/A | FEATURE-expands-ai-agents | N/A |
| OBJ-CTX-035 | SBM-SUITE | Habilitar almacenamiento de objetos/documentos transversal para archivos, planos, assets, evidencias y contenido, con aislamiento, versionado y políticas de acceso. | pending | 5 | N/A | FEATURE-enables-object-storage | N/A |
| OBJ-CTX-036 | SBM-SUITE | Definir despliegue productivo compartido para KS/PC/CG con gateway/reverse proxy, TLS, backups y separación de servicios públicos/internos; SonarQube permanece QA temporal, no runtime productivo permanente. | pending | 5 | N/A | FEATURE-defines-prod-topology | N/A |
| OBJ-CTX-037 | SBM-SUITE | Corregir objective-git-finalize para gestionar publicación/upstream de la branch objetivo y estados Git válidos antes de commit/merge transversal. | pending | 5 | N/A | BUGFIX-fixes-git-finalizer | N/A |

Rules:

- this section contains only approved objectives not yet started;
- status is always `pending`;
- objectives move to `Active objectives` when implementation begins;
- completed objectives never remain here;
- project-creation objectives remain owned by `SBM-SUITE` until the new repository has its own canonical context;
- database evolution is recorded as SBM-DB objectives and does not imply that the corresponding schema/migration already exists;
- every project objective change must update this section and the project summary.

## 5. Projects and ownership

### Current repositories

| Project | Ownership | Main responsibilities | Source of truth |
|---|---|---|---|
| DP-API | Historical/reference brand business API | Ditaly Pasta real-data reference implementation for Product, Material, Service, Catalog, Ticket, Provider, Price, inventory and reusable brand logic | Project code, project contexts and canonical APIs |
| SBM-MANAGER | Enterprise web frontend | Vue 3 management UI and explicit brand API / SBM-API consumption | Project code, project contexts and frontend API clients |
| SBM-API | Shared platform operations | Authentication, tokens, users, franchise scope, roles, permissions, restrictions and internal platform services | Project code and project contexts |
| SBM-DB | Physical database and migration authority | PostgreSQL schemas, DBML, Flyway migrations, constraints, views and structural seeds; never a runtime query gateway | DBML, Flyway, PostgreSQL runtime and project contexts |
| sbm-ai-assistant | AI/agent and knowledge orchestration | RAG, Tools, agents, embeddings, Qdrant, Slack, Context/Documentation processing | AI repository and indexed Git Markdown |
| SBM-SUITE/context | Global governance | Cross-project Context, Architecture, Business, QA, Security, Data, Decisions and Documentation | Git Markdown |

### Planned project portfolio

| Project | Planned responsibility |
|---|---|
| ks-api | Kiseki Tech sale/import business API |
| pc-api | PortalConvenios service, scheduling, referral and settlement API |
| cg-api | Consorcio y Gestión procedure/document/workflow API |
| sbm-core | Async workflows, scheduler/cron, Celery/Redis, optional Kafka, process flags/state DB |
| sbm-calculation | Shared financial/accounting calculation engine |
| sbm-util | Polyglot deterministic utilities/integrations; Spring Boot candidate/target |
| sbm-ai-manager | Agent control plane/frontend |
| sbm-security | Security process control plane/frontend |
| sbm-marketing | Social/marketing data, campaigns, Meta API and marketing workflows |
| sbm-content | Content/asset workflows and creative-tool integrations |
| sbm-control | Global operational control plane for suite status/logs/jobs/context/QA/security/deploys |
| sbm-mobile | React Native mobile for SBM User |
| ks-store / pc-store / cg-store | React public brand stores/vitrines |
| ks-mobile / pc-mobile / cg-mobile | React Native mobile apps for each brand/franchise user |
| ks-client / pc-client / cg-client | Client-facing applications for brand clients |
| pc-customer | Customer/patient application for PC QR, scheduling and confirmation |

Only current repositories have canonical filesystem/runtime roots. Planned names are architectural targets and must not be treated as existing repositories until onboarding is completed.

## 6. Project objective summaries

| Project/group | Current role | Active objective | Pending direction |
|---|---|---|---|
| DP-API | Historical/reference brand API | N/A in global table | Stabilize reusable brand baseline while preserving Ditaly historical data |
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | QA completion, generic item/package/catalog UI, CG plans/documents module |
| SBM-DB | Flyway/DBML/PostgreSQL authority | `SBM-DB-001` | Lifecycle update plus multibrand, Equipment/Package, Catalog BOM, pricing/FX and KS/PC/CG data evolution |
| SBM-API | Shared identity/platform API | N/A | Multilevel SBM/Franchise/Client/Customer authorization model; rename legacy SBM-API runtime `sbm-core` before onboarding the new project |
| sbm-ai-assistant | AI/agent/RAG orchestration | N/A in global table | sbm-agent, dev-agent, brand agents and existing backlog/QA/security agent roadmap |
| SBM-SUITE/context | Global governance/orchestration | N/A | Project creation, core/util/calculation/control/security/marketing/content, channels, storage and production topology |
| KS | Production-target brand | N/A | `ks-api`, `ks-store`, `ks-mobile`, `ks-client`, `ks-agent` |
| PC | Production-target brand | N/A | `pc-api`, `pc-store`, `pc-mobile`, `pc-client`, `pc-customer`, `pc-agent` |
| CG | Production-target brand | N/A | `cg-api`, `cg-store`, `cg-mobile`, `cg-client`, `cg-agent` |

Ditaly Pasta is not a current production target; it remains the real-data reference used to harden generic behavior before adaptation to active brands.

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
| Transversal QA orchestration | Centralized Context and project QA execution, queueing and evidence aggregation | SBM-SUITE/context |

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
qa-check.sh (when the selected project provides it)
→ execute the configured test and coverage workflow
→ run SonarScanner only when configured and applicable
→ persist bounded evidence in the project QA result file

./scripts/context-deploy.sh <project_name> <lifecycle_phase> '<objectives-json-array>' [user_prompt]
→ execute only from the root of SBM-SUITE/context
→ validate project_name through the backend Project Registry
→ validate the explicit lifecycle phase and objective
→ dispatch lifecycle phases by exact literal equality only
→ request GET /contexts/contract before cleaning exchange directories
→ validate contract version, lifecycle phases, canonical project path and supported patches
→ use SBM-SUITE/context/SYS_PROMPT.md and SBM-SUITE/context/FORMAT_CONTEXT.md
→ execute SBM-SUITE/context/scripts/project-tree.sh and require project-tree.txt
→ collect Git and applicable QA evidence without packaging environment values
→ call POST /contexts/export using the registry-resolved canonical project root
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

### Objective activation

```text
objective-activation
→ activates exactly one existing pending objective
→ preserves objective_id, objective, priority, target_date and branch literally
→ changes only pending → active
→ forbids completed-objective history
```

### Implementation progress

```text
implementation-progress
→ dispatches only by exact lifecycle equality and never falls through to closure
→ requires the selected objective to exist in operational context
→ records only evidence-supported current state
→ preserves the objective as active or pending
→ forbids completed-objective history, active → completed and closure confirmation
→ for sbm-suite-context, resolves optional transversal evidence from QA/output/qa-all-without-sonar-results.md and QA/output/qa-all-without-sonar-queue.tsv
→ includes QA/output/context-qa-results.md when present and requires consistent successful evidence before recording passed
→ normalizes qa-results.md and manifest QA metadata inside the generated context package without turning progress into closure
→ does not apply implementation-closure QA gating during implementation-progress
```

### Implementation closure

```text
implementation-closure
→ dispatches only when the literal lifecycle is exactly implementation-closure
→ requires explicit closure confirmation
→ requires implementation evidence when implementation changes are claimed
→ requires canonical QA status passed when repository-relative scripts/qa-check.sh exists
→ derives not-applicable only when that structural workflow path does not exist and emits deterministic evidence
→ automatically stops using not-applicable if a QA workflow is later added
→ requires the applicable objective and QA synchronization patches
→ removes only the requested objective from operational contexts
→ appends exactly one record to context/COMPLETED_OBJECTIVES.md
```

### Upgrade

```text
context-upgrade.zip
→ context/input
→ ./scripts/context-upgrade.sh from SBM-SUITE/context
→ inspect manifest.json without extracting the archive
→ validate project_name from the trusted manifest through the backend Project Registry
→ reject unsafe, unsupported or phase-incompatible members
→ forbid patches/completed-objectives.json outside implementation-closure
→ require all applicable closure patches only during implementation-closure
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
→ applicable QA validation for the changed project state
→ final Context upgrade and objective closure
→ refresh context.zip after the Context mutation
→ ./scripts/documentation-deploy.sh from SBM-SUITE/context
→ run global Context → Documentation reconciliation across projects
→ RAG from current documentation and updated contexts
→ documentation-package.zip + documentation SYS_PROMPT.md
→ user uploads the generated package to ChatGPT
→ ChatGPT returns documentation-upgrade.zip
→ ./scripts/documentation-upgrade.sh from SBM-SUITE/context
→ validate authorized existing pages, manifest equality and format
→ create the timestamped documentation backup under context/backup
→ replace only authorized Markdown
→ mark the previously loaded context.zip stale and require a fresh export before further state reads
→ print proposed commit message
```

Rules:

- Documentation is global and does not accept project selection or `project_name` in its CLI;
- Git is the primary source of truth during the first stage;
- documentation pages and subpages are modified only when authorized by the documentation format;
- main pages are first-class documents and maintain subpage links;
- automated creation, deletion, rename and structural changes are not allowed initially;
- structural changes require manual updates to the page, documentation format and documentation system prompt;
- Context and Documentation upgrades remain separate;
- Documentation is executed only after implementation closure and never for planning activation or implementation progress;
- later synchronization with Notion may become bidirectional;
- `SBM-SUITE/context/backup/` is the only backup root for both workflows;
- pluralized and workflow-local backup directories must never be used or recreated.

## 12. Current implementation status

Verified current capabilities include:

- Context/Documentation lifecycle orchestration is centralized in `SBM-SUITE/context/scripts/`;
- transversal QA orchestration is implemented and `OBJ-CTX-014` is completed;
- the supplied 2026-08-16 `without-sonar` queue passed DP-API, SBM-MANAGER, SBM-DB, SBM-API and sbm-ai-assistant; Context QA also passed;
- DP-API remains the only implemented brand API in the current repository set and is now classified as historical/reference because Ditaly Pasta is closed;
- SBM-API, SBM-DB, SBM-MANAGER and sbm-ai-assistant remain current shared projects;
- KS/PC/CG APIs, channels and new SBM services listed in pending objectives are planned only and have no canonical repository/runtime path yet;
- database/domain changes for Equipment, Package, Catalog composition, multibrand topology, pricing/FX and KS/PC/CG models are objectives only until implemented in SBM-DB;
- `sbm-core`, `sbm-calculation` and `sbm-util` boundaries are architecturally defined but not yet implemented;
- `sbm-control`, `sbm-security`, `sbm-ai-manager`, `sbm-marketing` and `sbm-content` are planned applications;
- Context remains Git-first; Qdrant is an index and Documentation reconciliation remains a separate workflow.

Current limitations/pending validation:

- Sonar-enabled transversal execution still requires explicit SonarQube readiness; SonarQube is not a permanent production runtime requirement;
- tenant/client/customer isolation, cross-project contracts and new brand flows need implementation-specific QA before production;
- Git-to-Notion synchronization, full async automation and production topology remain future work;
- the Git finalizer upstream/publication behavior identified during `OBJ-CTX-014` finalization remains a pending system fix.

## 13. Validated decisions

1. Git Markdown is the primary source of truth during the manual stage; Qdrant remains a semantic index.
2. Context and Documentation workflows/collections remain separate.
3. Active/pending objectives remain operational state; completed objectives live only in `COMPLETED_OBJECTIVES.md`.
4. SBM-DB/Flyway owns physical business schema evolution and is not a runtime query gateway.
5. Brand-facing operations belong to the responsible brand API; SBM-API owns shared identity/platform operations.
6. Ditaly Pasta is historical/reference; KS, PC and CG are current production-target brands.
7. The authorization/business hierarchy is SBM User → Franchise/Brand User → Client/User → Customer/User when applicable; `franchise` remains the current DB brand scope name.
8. Product, Material, Service, planned Equipment, Catalog and Ticket remain distinct domains; Package is mandatory for item domains including logical Service packages.
9. Catalog is the configurable BOM/recipe/acquisition composition; Ticket is the sold/reported/scheduled commercial unit.
10. `sbm-core` owns async orchestration; `sbm-calculation` owns business calculations; `sbm-util` owns deterministic reusable integrations.
11. `sbm-ai-assistant` owns agent reasoning/orchestration and acts through explicit Tools/APIs.
12. `sbm-ai-manager`, `sbm-security` and `sbm-control` are separate control planes.
13. Brand `*-mobile` apps serve Franchise/Brand Users; `*-client` apps serve Client Users; customer-specific apps are created only when required (`pc-customer`).
14. Kafka is optional and justified by event-stream semantics; it is not mandatory merely because Celery/Redis exist.
15. SonarQube is QA/static-analysis infrastructure and does not require permanent production uptime.
16. Kiseki sale/import is current scope; rental/contracts/technical service/spares are long-term scope.

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
- canonical global `context-deploy.sh` created under `SBM-SUITE/context/scripts/`;
- canonical global `context-upgrade.sh` created under `SBM-SUITE/context/scripts/`;
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
- SBM-MANAGER canonical project context, QA context and deploy context prepared;
- SBM-DB canonical project context, QA context, deploy context and lifecycle scripts prepared;
- section-level patch validation and application implemented;
- project-tree generation integrated into context deployment;
- context export response persistence and completion validation implemented;
- context upgrade input and response validation strengthened;
- QA evidence file generation implemented in `qa-check.sh`;

## 16. Pending work

1. Finish currently active SBM-MANAGER and SBM-DB lifecycle objectives before activating unrelated pending work when feasible.
2. Stabilize DP-API as the reusable historical reference implementation without treating Ditaly Pasta as a current production brand.
3. Create and onboard the production-target brand APIs `ks-api`, `pc-api` and `cg-api`.
4. Implement `sbm-core`, `sbm-calculation` and `sbm-util` with explicit responsibility boundaries.
5. Expand the identity model through SBM User → Franchise/Brand User → Client/User → Customer/User where the business flow requires it.
6. Execute SBM-DB objectives for Equipment, Package, Catalog composition, pricing/FX, procurement/accounting traceability and brand-specific data models; do not infer these changes as implemented before Flyway/DBML evidence exists.
7. Create the control planes `sbm-ai-manager`, `sbm-security` and `sbm-control`.
8. Create `sbm-marketing` and `sbm-content` with their agent/tool integrations.
9. Create brand stores/mobile/client/customer channels according to the pending objective inventory.
10. Add transversal object storage for documents, plans, assets and evidence.
11. Define production topology for KS/PC/CG; keep SonarQube as temporary QA infrastructure rather than permanent production runtime.
12. Correct the pending `objective-git-finalize` upstream/publication behavior.
13. Continue Documentation/RAG/Notion and cross-project automation roadmap after the immediate production foundations are stable.

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
