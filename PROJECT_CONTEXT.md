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

SBM-AI-ASSISTANT
→ AI orchestration, agents, RAG, context/documentation processing

SBM-SUITE/context
→ global governance, objectives, QA, security, data, decisions and documentation
```

Target production expansion:

```text
Brand APIs       → KS-API / PC-API / CG-API, cloned/adapted from __BASE-FRANCHISE-API
Async platform   → SBM-CORE
Calculation      → SBM-CALCULATION
Deterministic integrations → SBM-UTIL
Agent UI         → SBM-AI-MANAGER
Security UI      → SBM-SECURITY
Security API     → SBM-SECURITY-API
Marketing API    → SBM-MARKETING
Content API      → SBM-CONTENT
Operations UI    → SBM-CONTROL
SBM mobile       → SBM-MOBILE
Stores           → KS-STORE / PC-STORE / CG-STORE, derived from __BASE-STORE
Brand-user mobile→ KS-MOBILE / PC-MOBILE / CG-MOBILE, derived from __BASE-MOBILE
Client channels  → KS-CLIENT / PC-CLIENT / CG-CLIENT, derived from __BASE-CLIENT
Customer channel → PC-CUSTOMER, derived from __BASE-CUSTOMER
Base projects    → __BASE-FRANCHISE-API / __BASE-STORE / __BASE-MOBILE / __BASE-CLIENT / __BASE-CUSTOMER
```

Ditaly Pasta is closed operationally but retains one year of real historical data and remains the reference implementation used to stabilize reusable business logic before adapting/cloning it for active brands. Kiseki Tech, PortalConvenios.cl and Consorcio y Gestión are the current production-target brands.

## 3. Active objectives

| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
| SBM-MANAGER-001 | SBM-MANAGER | Integrar SBM-MANAGER completamente a SBM Suite, incluyendo contextos, lifecycle scripts, QA/SonarQube, registro en SBM-AI-ASSISTANT, sincronización global y actualización del diagrama canónico de arquitectura en SUITE_CONTEXT.md. | active | 5 | 2026-08-07 | FEATURE-integrates-sbm-manager | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |
| SBM-DB-001 | SBM-DB | habilitación de SBM-DB | active | 5 | 2026-08-07 | FEATURE-enables-sbm-db | `context/documentation/pages/🤖 AI Architect Roadmap/🏢 SBM-Suite 3a50bde8acd580d0a068d6abc3542603.md` |
| OBJ-CTX-038 | SBM-SUITE | Habilitar Git Flow transversal para repos SBM: main/develop, branches feature/bugfix/hotfix/release, asociación Objective→branch, gates QA/Security, finalización/merge/cleanup multi-repo y migración controlada desde el flujo actual directo a main. | active | 5 | N/A | FEATURE-standardizes-suite-governance | N/A |
| OBJ-CTX-012 | SBM-SUITE | Mantener INIT_CONTEXT.md como contrato operativo y crear SBM_AGENT.md como archivo inicial mínimo para un ChatGPT limpio; SBM_AGENT.md debe cargar/consumir INIT_CONTEXT y conducir el bootstrap sin duplicar sus reglas. | active | 5 | N/A | FEATURE-standardizes-suite-governance | N/A |
| OBJ-CTX-002 | SBM-SUITE | Habilitar tooling transversal desde SBM-SUITE/context para crear, propagar y actualizar scripts, contratos y archivos Context comunes sobre uno o varios proyectos registrados, con detección de diferencias y ejecución controlada desde la raíz de Context. | active | 5 | N/A | FEATURE-standardizes-suite-governance | N/A |

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
| SBM-MANAGER-006 | SBM-MANAGER | Definir navegación y autorización multi-brand/multi-role para SBM User y Brand User, consumiendo SBM-API y Franchise APIs mediante contratos estables sin acoplar la UI a DP-API. | pending | 5 | N/A | FEATURE-enables-multibrand-navigation | N/A |
| SBM-API-001 | SBM-API | Consolidar identidad/autorización multinivel para SBM User, Franchise/Brand User, Client User y Customer User cuando aplique, preservando franchise como alcance canónico de marca y roles/permisos/restricciones backend. | pending | 5 | N/A | FEATURE-expands-identity-model | N/A |
| SBM-API-002 | SBM-API | Renombrar el runtime/container legacy `sbm-core` usado actualmente por SBM-API para liberar el nombre del futuro proyecto `SBM-CORE` y evitar colisión de servicio/red. | pending | 5 | N/A | BUGFIX-renames-sbm-api-runtime | N/A |
| SBM-API-003 | SBM-API | Formalizar el contrato transversal SBM-API ↔ Franchise APIs para autenticación/autorización, franchise/brand scope, propagación de identidad, errores y límites de ownership, evitando dependencias específicas de DP. | pending | 5 | N/A | FEATURE-defines-franchise-api-contract | N/A |
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
| SBM-DB-011 | SBM-DB | Definir contratos/migraciones compatibles con __BASE-FRANCHISE-API y sus derivados, separando estructuras comunes de extensiones/configuración por franchise y evitando dependencias de datos específicas de DP en la base reusable. | pending | 5 | N/A | FEATURE-defines-base-data-contract | N/A |
| DP-ARCH-001 | DP-API | Estabilizar satisfactoriamente DP-API trabajando con SBM-API como implementación funcional de referencia, preservando datos/comportamiento Ditaly y cerrando contratos de integración antes de extraer cualquier base reusable. | pending | 5 | N/A | FEATURE-stabilizes-dp-sbm-integration | N/A |
| OBJ-CTX-003 | SBM-SUITE | Separar QA y Context mediante una estructura específica por proyecto. | pending | 5 | N/A | FEATURE-separates-qa-context | N/A |
| OBJ-CTX-004 | SBM-SUITE | Crear SBM-CORE para scheduler/cron, PostgreSQL de flags/estado, Celery, Redis, retries/idempotency y Kafka solo donde el patrón event-driven lo justifique; sin lógica financiera ni de seguridad de dominio. | pending | 5 | N/A | FEATURE-enables-sbm-core | N/A |
| OBJ-CTX-005 | SBM-SUITE | Crear SBM-UTIL como servicio reutilizable Java/Spring Boot para email, archivos, APIs externas, conectores determinísticos, transformaciones técnicas y tipos de cambio oficiales consumidos por servicios/agentes. | pending | 5 | N/A | FEATURE-enables-sbm-util | N/A |
| OBJ-CTX-006 | SBM-SUITE | Habilitar Scrum Agent para administrar el backlog Jira sincronizado por OBJ-CTX-043, priorizar Epic/Issue/Task, coordinar dependencias, procesos asíncronos y activaciones IA mediante SBM-CORE/Control API. | pending | 5 | N/A | FEATURE-enables-scrum-agent | N/A |
| OBJ-CTX-007 | SBM-SUITE | Habilitar Igor Agent como responsable técnico de QA automation, DevOps/SRE, infraestructura y troubleshooting, integrándolo a CI/CD y a los gates técnicos sin mezclar QA con Security. | pending | 5 | N/A | FEATURE-enables-igor-agent | N/A |
| OBJ-CTX-008 | SBM-SUITE | Habilitar el Security Gate posterior a QA y previo a release: ejecución automatizada, evidencias, findings, mitigación/prevención, aprobación humana en SBM-SECURITY y retorno obligatorio a Development cuando Security rechace. | pending | 5 | N/A | FEATURE-enables-security-flow | N/A |
| OBJ-CTX-009 | SBM-SUITE | Evolucionar la capacidad security-agent hacia la célula nombrada en SBM-AI-ASSISTANT liderada por Batman Agent e integrada por Alfred, Robin, Gotham, Joker, Queen, Darth Maul, Cerberus y Hercules, usando SBM-SECURITY-API y herramientas locales/dockerizadas/externas bajo autorización. | pending | 5 | N/A | FEATURE-enables-security-agents | N/A |
| OBJ-CTX-010 | SBM-SUITE | Crear SBM-AI-MANAGER como frontend/control plane para registrar, visualizar, configurar y operar agentes; tecnología .NET/Blazor queda como candidata a validar al activar. | pending | 5 | N/A | FEATURE-enables-ai-manager | N/A |
| OBJ-CTX-011 | SBM-SUITE | Estandarizar el onboarding de proyectos nuevos o existentes en SBM-SUITE: repositorio/remoto, ubicación local, Project Registry, Context, Documentation, QA, Security, Git/Git Flow y relación __BASE-* cuando corresponda. | pending | 5 | N/A | FEATURE-completes-project-onboarding | N/A |
| OBJ-CTX-015 | SBM-SUITE | Crear KS-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para venta/importación KS: Product/Material/Service/Catalog/Ticket, inventario, costos de importación, pricing multimoneda y trazabilidad; arriendo queda fuera del alcance inmediato. | pending | 5 | N/A | FEATURE-enables-ks-api | N/A |
| OBJ-CTX-016 | SBM-SUITE | Crear PC-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para operativos y derivaciones: agendamiento, Client/Customer, QR, confirmación, comisión, conciliación y suscripción mensual. | pending | 5 | N/A | FEATURE-enables-pc-api | N/A |
| OBJ-CTX-017 | SBM-SUITE | Crear CG-API clonando/adaptando __BASE-FRANCHISE-API en Python/Django REST para trámites, documentos, etapas, dependencias, calendarización, proveedores y planos. | pending | 5 | N/A | FEATURE-enables-cg-api | N/A |
| OBJ-CTX-018 | SBM-SUITE | Crear SBM-CALCULATION en Python/FastAPI con pandas, scikit-learn y statsmodels para fórmulas, precios, FX, impuestos, comisiones, provisiones, costos, conciliaciones, regresiones y capacidades ML autorizadas. | pending | 5 | N/A | FEATURE-enables-sbm-calculation | N/A |
| OBJ-CTX-019 | SBM-SUITE | Crear SBM-SECURITY como frontend humano de Security: findings, scans, vulnerabilidades, evidencias, riesgos, protocolos, planes de mitigación/prevención, reportes y aprobación/rechazo del Security Gate consumiendo SBM-SECURITY-API. | pending | 5 | N/A | FEATURE-enables-sbm-security | N/A |
| OBJ-CTX-020 | SBM-SUITE | Crear SBM-MARKETING como API Node.js/TypeScript/NestJS para datos de redes, SEO, campañas, métricas, calendarizaciones, sesiones foto/video, pago de promociones, arriendo de equipos, contratación de servicios e integraciones sociales. | pending | 5 | N/A | FEATURE-enables-sbm-marketing | N/A |
| OBJ-CTX-021 | SBM-SUITE | Crear SBM-CONTENT en Python/FastAPI para assets y workflows de producción, generación y edición de contenido, integrando DaVinci/Medici y herramientas creativas autorizadas como Photoshop y Blender. | pending | 5 | N/A | FEATURE-enables-sbm-content | N/A |
| OBJ-CTX-022 | SBM-SUITE | Crear SBM-CONTROL como control plane global de SBM Suite: health/status, logs, métricas/reportes, cron/schedulers, workers/colas, Context/Objectives/Documentation, QA, Security, deploys, alertas y backups. | pending | 5 | N/A | FEATURE-enables-sbm-control | N/A |
| OBJ-CTX-023 | SBM-SUITE | Crear SBM-MOBILE en React Native para SBM User y operaciones administrativas aprobadas. | pending | 5 | N/A | FEATURE-enables-sbm-mobile | N/A |
| OBJ-CTX-024 | SBM-SUITE | Crear KS-STORE clonando/adaptando __BASE-STORE como vitrina/commerce pública de Tickets KS bajo dominio propio. | pending | 5 | N/A | FEATURE-enables-ks-store | N/A |
| OBJ-CTX-025 | SBM-SUITE | Crear PC-STORE clonando/adaptando __BASE-STORE como canal público de servicios/Tickets PC bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-pc-store | N/A |
| OBJ-CTX-026 | SBM-SUITE | Crear CG-STORE clonando/adaptando __BASE-STORE como canal público de servicios/Tickets CG bajo dominio propio cuando corresponda. | pending | 5 | N/A | FEATURE-enables-cg-store | N/A |
| OBJ-CTX-027 | SBM-SUITE | Crear KS-MOBILE clonando/adaptando __BASE-MOBILE en React Native para KS/Franchise User. | pending | 5 | N/A | FEATURE-enables-ks-mobile | N/A |
| OBJ-CTX-028 | SBM-SUITE | Crear PC-MOBILE clonando/adaptando __BASE-MOBILE en React Native para PC/Franchise User. | pending | 5 | N/A | FEATURE-enables-pc-mobile | N/A |
| OBJ-CTX-029 | SBM-SUITE | Crear CG-MOBILE clonando/adaptando __BASE-MOBILE en React Native para CG/Franchise User. | pending | 5 | N/A | FEATURE-enables-cg-mobile | N/A |
| OBJ-CTX-030 | SBM-SUITE | Crear KS-CLIENT clonando/adaptando __BASE-CLIENT para Client User KS, inicialmente control de inventario/equipos y capacidades autorizadas de monitoreo/operación. | pending | 5 | N/A | FEATURE-enables-ks-client | N/A |
| OBJ-CTX-031 | SBM-SUITE | Crear PC-CLIENT clonando/adaptando __BASE-CLIENT para Client User PC, incluyendo operativos/derivaciones, agenda, QR/confirmaciones y conciliación operativa. | pending | 5 | N/A | FEATURE-enables-pc-client | N/A |
| OBJ-CTX-032 | SBM-SUITE | Crear PC-CUSTOMER clonando/adaptando __BASE-CUSTOMER para PC Customer: ficha, QR, agendamiento, confirmación y seguimiento del servicio con tratamiento reforzado de datos personales/salud. | pending | 5 | N/A | FEATURE-enables-pc-customer | N/A |
| OBJ-CTX-033 | SBM-SUITE | Crear CG-CLIENT clonando/adaptando __BASE-CLIENT para seguimiento de etapas de tramitación, dependencias, documentos faltantes, información general y FAQ. | pending | 5 | N/A | FEATURE-enables-cg-client | N/A |
| OBJ-CTX-034 | SBM-SUITE | Expandir SBM-AI-ASSISTANT con el catálogo canónico de agentes nombrados, jerarquías/gobierno, permisos, herramientas y activación bajo demanda; Scrum Agent/SBM Agent coordinan y por defecto se prefieren APIs, jobs y servicios determinísticos antes de ejecutar IA. | pending | 5 | N/A | FEATURE-expands-named-agents | N/A |
| OBJ-CTX-035 | SBM-SUITE | Habilitar almacenamiento de objetos/documentos transversal para archivos, planos, assets, evidencias y contenido, con aislamiento, versionado y políticas de acceso. | pending | 5 | N/A | FEATURE-enables-object-storage | N/A |
| OBJ-CTX-036 | SBM-SUITE | Definir despliegue productivo compartido para KS/PC/CG con gateway/reverse proxy, TLS, backups y separación de servicios públicos/internos; SonarQube permanece QA temporal y SBM-SECURITY-API/SECURITY tooling se aísla del runtime de negocio. | pending | 5 | N/A | FEATURE-defines-prod-topology | N/A |
| OBJ-CTX-037 | SBM-SUITE | Corregir objective-git-finalize.sh para preflight multi-repo, commit/push de branch FEATURE/BUGFIX, ejecutar git push --set-upstream origin <branch> cuando la primera publicación no tenga upstream, merge --no-ff a main, push de main y normalización segura; sin force-push ni borrado de ramas. | pending | 5 | N/A | BUGFIX-fixes-git-finalizer | N/A |
| OBJ-CTX-039 | SBM-SUITE | Habilitar el framework __BASE-* con lineage/versionado, features opcionales/configurables, creación controlada de derivados y propagación BASE→derivados mediante diff/adaptación validada por agentes, QA y Security; Yeoman puede usarse para scaffolding inicial, nunca como mecanismo de sincronización posterior. | pending | 5 | N/A | FEATURE-enables-base-project-inheritance | N/A |
| OBJ-CTX-040 | SBM-SUITE | Crear SBM-SECURITY-API en Go/Gin/PostgreSQL como backend aislado de Security para pentests/scans, tool runs, findings, evidencias, políticas, riesgos y approvals; integra herramientas locales/dockerizadas/externas y usa SBM-CORE solo para scheduling/jobs, sin lógica Security en Core. | pending | 5 | N/A | FEATURE-enables-security-api | N/A |
| BASE-FRANCHISE-001 | __BASE-FRANCHISE-API | Después de completar DP-ARCH-001, generar __BASE-FRANCHISE-API desde la implementación validada de DP-API, remover/configurar comportamiento específico DP, estandarizar módulos opcionales y registrar DP-API como primer derivado controlado del BASE. | pending | 5 | N/A | FEATURE-creates-franchise-base-from-dp | N/A |
| OBJ-CTX-042 | SBM-SUITE | Integrar Documentation Markdown con Notion mediante sincronización Git→Notion controlada, preservando Git/Markdown como source of truth, estructura de páginas, IDs estables, trazabilidad y detección de cambios; bidireccionalidad queda fuera del alcance inicial. | pending | 5 | N/A | FEATURE-syncs-documentation-to-notion | N/A |
| OBJ-CTX-043 | SBM-SUITE | Integrar Objectives con Jira como backlog organizado por Proyecto→Epic→Issue/Task, manteniendo mapping Objective ID↔Jira ID, estado, prioridad y dependencias sin duplicados; inicialmente operado por SBM Agent/SBM-UTIL y futuramente administrado por Scrum Agent. | pending | 5 | N/A | FEATURE-syncs-objectives-to-jira | N/A |
| OBJ-CTX-044 | SBM-SUITE | Estandarizar contratos Agent↔API/Tool en SBM-AI-ASSISTANT para request/response, scopes/permisos, approvals, auditoría, idempotencia, errores y evidencias, evitando integraciones ad hoc específicas por agente. | pending | 5 | N/A | FEATURE-standardizes-agent-tool-contracts | N/A |
| OBJ-CTX-045 | SBM-SUITE | Implementar Xavier Agent como coordinador de conversaciones humanas y reuniones multiagente, gestionando sesiones, participantes, turnos, contexto conversacional, incorporación y retiro dinámico de agentes, permisos y auditoría. | pending | 5 | N/A | FEATURE-adds-suite-objectives | N/A |
| OBJ-CTX-046 | SBM-SUITE | Diseñar e implementar SBM Voice Interface incluyendo STT/TTS, Voice Registry, identidad de voz por agente, wake word, dispositivo físico, integración textual con SBM-MANAGER, autenticación humana/dispositivo, autorización por sesión, anti-spoofing/replay y auditoría. | pending | 5 | N/A | FEATURE-adds-suite-objectives | N/A |
| OBJ-CTX-047 | SBM-SUITE | Diseñar arquitectura Local/Cloud AI Runtime con ejecución local opcional de agentes, RAG, embeddings, Vector DB, context cache y fallback seguro hacia proveedores cloud. | pending | 5 | N/A | FEATURE-adds-suite-objectives | N/A |
| OBJ-CTX-048 | SBM-SUITE | Corregir la integración de Confluence de SBM-AI-ASSISTANT, restaurando y validando credenciales/configuración requeridas para ingestión y sincronización sin modificar innecesariamente la implementación existente. | pending | 5 | N/A | FEATURE-adds-suite-objectives | N/A |

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
| DP-API | Historical/reference brand business API | Ditaly Pasta real-data reference implementation and source for reusable franchise patterns | Project code, project contexts and canonical APIs |
| SBM-MANAGER | Enterprise web frontend | Vue 3 management UI and explicit brand API / SBM-API consumption | Project code, project contexts and frontend API clients |
| SBM-API | Shared platform operations | Authentication, tokens, users, franchise scope, roles, permissions, restrictions and internal platform services | Project code and project contexts |
| SBM-DB | Physical database and migration authority | PostgreSQL schemas, DBML, Flyway migrations, constraints, views and structural seeds; never a runtime query gateway | DBML, Flyway, PostgreSQL runtime and project contexts |
| SBM-AI-ASSISTANT | AI/agent/RAG orchestration | N/A in global table | Named-agent governance plus standard Agent↔API/Tool contracts (OBJ-CTX-034/044) |
| SBM-SUITE/context | Global governance | Cross-project Context, Architecture, Business, QA, Security, Data, Decisions and Documentation | Git Markdown |

Canonical project display names are uppercase. Existing filesystem paths, Docker names and backend registry IDs remain literal operational identifiers until a specific migration renames them.

### Planned project portfolio

| Project | Planned responsibility |
|---|---|
| __BASE-FRANCHISE-API | Python/Django REST reusable base for brand/franchise APIs and controlled inheritance |
| __BASE-STORE | Reusable public store/web baseline |
| __BASE-MOBILE | Reusable React Native brand-user mobile baseline |
| __BASE-CLIENT | Reusable client-facing application baseline |
| __BASE-CUSTOMER | Reusable customer-facing application baseline where needed |
| KS-API / PC-API / CG-API | Brand APIs cloned/adapted from `__BASE-FRANCHISE-API` |
| SBM-CORE | Async workflows, scheduler/cron, Celery/Redis, optional Kafka, process flags/state DB |
| SBM-CALCULATION | Python/FastAPI calculation, regression and ML service |
| SBM-UTIL | Java/Spring Boot deterministic utilities/integrations |
| SBM-AI-MANAGER | Agent control plane/frontend |
| SBM-SECURITY | Human Security control plane/frontend |
| SBM-SECURITY-API | Go/Gin/PostgreSQL isolated Security backend |
| SBM-MARKETING | Node.js/TypeScript/NestJS marketing operations API |
| SBM-CONTENT | Python/FastAPI content production API/service |
| SBM-CONTROL | Global operational control plane |
| SBM-MOBILE | React Native mobile for SBM User |
| KS-STORE / PC-STORE / CG-STORE | Public stores derived from `__BASE-STORE` |
| KS-MOBILE / PC-MOBILE / CG-MOBILE | Brand-user mobile apps derived from `__BASE-MOBILE` |
| KS-CLIENT / PC-CLIENT / CG-CLIENT | Client-facing apps derived from `__BASE-CLIENT` |
| PC-CUSTOMER | Customer/patient app derived from `__BASE-CUSTOMER` |

Only current repositories have canonical filesystem/runtime roots. Planned names are architectural targets and must not be treated as existing repositories until onboarding is completed. Base/derived relationships are design state until `OBJ-CTX-039` is implemented.

## 6. Project objective summaries

| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
| DP-API | Historical/reference brand API | N/A in global table | `DP-ARCH-001` | N/A | `dp/DP-API/context/PROJECT_CONTEXT.md` | `dp/DP-API/context/QA_CONTEXT.md` | N/A |
| SBM-MANAGER | Enterprise management frontend | `SBM-MANAGER-001` | `SBM-MANAGER-003`, `SBM-MANAGER-004`, `SBM-MANAGER-005`, `SBM-MANAGER-006` | FEATURE-integrates-sbm-manager | `SBM/SBM-MANAGER/context/PROJECT_CONTEXT.md` | `SBM/SBM-MANAGER/context/QA_CONTEXT.md` | N/A |
| SBM-DB | Flyway/DBML/PostgreSQL authority | SBM-DB-001 | `SBM-DB-002`, `SBM-DB-003`, `SBM-DB-004`, `SBM-DB-005`, `SBM-DB-006`, `SBM-DB-007`, `SBM-DB-008`, `SBM-DB-009`, `SBM-DB-010`, `SBM-DB-011` | FEATURE-enables-sbm-db | `SBM/SBM-DB/context/PROJECT_CONTEXT.md` | `SBM/SBM-DB/context/QA_CONTEXT.md` | N/A |
| SBM-API | Shared identity/platform API | N/A | `SBM-API-001`, `SBM-API-002`, `SBM-API-003` | N/A | `SBM/SBM-API/context/PROJECT_CONTEXT.md` | `SBM/SBM-API/context/QA_CONTEXT.md` | N/A |
| SBM-AI-ASSISTANT | AI/agent/RAG orchestration | N/A in global table | `OBJ-CTX-034`, `OBJ-CTX-044` | N/A | `SBM/sbm-ai-assistant/context/PROJECT_CONTEXT.md` | `SBM/sbm-ai-assistant/context/QA_CONTEXT.md` | N/A |
| SBM-SUITE/context | Global governance/orchestration | `OBJ-CTX-038`, `OBJ-CTX-012`, `OBJ-CTX-002` | `OBJ-DOC-001`, `OBJ-CTX-003`, `OBJ-CTX-004`, `OBJ-CTX-005`, `OBJ-CTX-006`, `OBJ-CTX-007`, `OBJ-CTX-008`, `OBJ-CTX-009`, `OBJ-CTX-010`, `OBJ-CTX-011`, `OBJ-CTX-015`, `OBJ-CTX-016`, `OBJ-CTX-017`, `OBJ-CTX-018`, `OBJ-CTX-019`, `OBJ-CTX-020`, `OBJ-CTX-021`, `OBJ-CTX-022`, `OBJ-CTX-023`, `OBJ-CTX-024`, `OBJ-CTX-025`, `OBJ-CTX-026`, `OBJ-CTX-027`, `OBJ-CTX-028`, `OBJ-CTX-029`, `OBJ-CTX-030`, `OBJ-CTX-031`, `OBJ-CTX-032`, `OBJ-CTX-033`, `OBJ-CTX-034`, `OBJ-CTX-035`, `OBJ-CTX-036`, `OBJ-CTX-037`, `OBJ-CTX-039`, `OBJ-CTX-040`, `OBJ-CTX-042`, `OBJ-CTX-043`, `OBJ-CTX-044`, `OBJ-CTX-045`, `OBJ-CTX-046`, `OBJ-CTX-047`, `OBJ-CTX-048` | FEATURE-standardizes-suite-governance | `context/PROJECT_CONTEXT.md` | `context/QA_CONTEXT.md` | N/A |
| __BASE-FRANCHISE-API | Reusable Franchise API template | N/A | `BASE-FRANCHISE-001` | N/A | N/A | N/A | N/A |
| KS | Production-target brand | N/A | `KS-API`, `KS-STORE`, `KS-MOBILE`, `KS-CLIENT`, `KS Agent` derived/governed through canonical bases | N/A | N/A | N/A | N/A |
| PC | Production-target brand | N/A | `PC-API`, `PC-STORE`, `PC-MOBILE`, `PC-CLIENT`, `PC-CUSTOMER`, `PC Agent` derived/governed through canonical bases | N/A | N/A | N/A | N/A |
| CG | Production-target brand | N/A | `CG-API`, `CG-STORE`, `CG-MOBILE`, `CG-CLIENT`, `CG Agent` derived/governed through canonical bases | N/A | N/A | N/A | N/A |

Ditaly Pasta is not a current production target; it remains the real-data reference used to harden generic behavior before adaptation to active brands.

## 7. Global architecture

Current context architecture:

```text
Git Markdown contexts
→ context-deploy.sh
→ SBM-AI-ASSISTANT
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
→ SBM-AI-ASSISTANT
→ embeddings
→ Qdrant sbm_documentation
→ RAG documentation package
→ ChatGPT updated authorized documentation Markdown
→ documentation-upgrade.sh
→ documentation backup and replacement
→ controlled Git→Notion synchronization (OBJ-CTX-042)
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
| Qdrant | Semantic indexes | SBM-AI-ASSISTANT |
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

SBM-AI-ASSISTANT
→ canonical APIs and indexed Markdown
→ never writes directly to PostgreSQL

SBM-SUITE/context
→ global synchronization of project objectives and QA summaries
→ transversal Context/script propagation and standardized project onboarding

Documentation Markdown
→ SBM-UTIL / Notion API
→ Notion projection; Git remains source of truth

Objectives
→ SBM-UTIL / Jira API
→ Project → Epic → Issue/Task backlog
→ Scrum Agent manages later after OBJ-CTX-006
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

./scripts/context-deploy.sh <project_name> <lifecycle_phase> '<small-objectives-json-array>|-' [user_prompt]
→ execute only from the root of SBM-SUITE/context
→ validate project_name through the backend Project Registry
→ validate the explicit lifecycle phase and objective
→ accept compact `SBM-GZIP-BASE64-V1` full-object envelopes through stdin with objectives argument `-`, validate gzip CRC/base64/UTF-8/JSON/lifecycle fidelity through internal temporary files and never use `input/`/`output/` as objective transport
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

- Upgrade input discovery accepts exactly one workflow-prefixed ZIP for Context and Documentation (`context-upgrade*.zip` or `documentation-upgrade*.zip`), including client-generated suffixes such as `(32)`; ambiguous ZIP sets and invalid prefixes remain rejected, and the selected file is normalized internally to the canonical filename before backend validation.

- Context/Documentation lifecycle orchestration is centralized in `SBM-SUITE/context/scripts/`;
- transversal QA orchestration is implemented and `OBJ-CTX-014` is completed;
- the supplied 2026-08-16 `without-sonar` queue passed DP-API, SBM-MANAGER, SBM-DB, SBM-API and SBM-AI-ASSISTANT; Context QA also passed;
- DP-API remains the only implemented brand API in the current repository set and is now classified as historical/reference because Ditaly Pasta is closed;
- SBM-API, SBM-DB, SBM-MANAGER and SBM-AI-ASSISTANT remain current shared projects;
- KS/PC/CG APIs, channels and new SBM services listed in pending objectives are planned only and have no canonical repository/runtime path yet;
- database/domain changes for Equipment, Package, Catalog composition, multibrand topology, pricing/FX and KS/PC/CG models are objectives only until implemented in SBM-DB;
- `SBM-CORE`, `SBM-CALCULATION` and `SBM-UTIL` boundaries are architecturally defined but not yet implemented;
- `SBM-CONTROL`, `SBM-SECURITY`, `SBM-AI-MANAGER`, `SBM-MARKETING` and `SBM-CONTENT` are planned applications;
- Context remains Git-first; Qdrant is an index and Documentation reconciliation remains a separate workflow.

Current limitations/pending validation:

- Sonar-enabled transversal execution still requires explicit SonarQube readiness; SonarQube is not a permanent production runtime requirement;
- tenant/client/customer isolation, cross-project contracts and new brand flows need implementation-specific QA before production;
- Git→Notion Documentation sync, Context→Jira Objective sync, full async automation and production topology remain future work;
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
10. `SBM-CORE` owns async orchestration; `SBM-CALCULATION` owns business calculations; `SBM-UTIL` owns deterministic reusable integrations.
11. `SBM-AI-ASSISTANT` owns agent reasoning/orchestration and acts through explicit Tools/APIs.
12. `SBM-AI-MANAGER`, `SBM-SECURITY` and `SBM-CONTROL` are separate control planes.
13. Brand `*-mobile` apps serve Franchise/Brand Users; `*-client` apps serve Client Users; customer-specific apps are created only when required (`PC-CUSTOMER`).
14. Kafka is optional and justified by event-stream semantics; it is not mandatory merely because Celery/Redis exist.
15. SonarQube is QA/static-analysis infrastructure and does not require permanent production uptime.
16. Kiseki sale/import is current scope; rental/contracts/technical service/spares are long-term scope.
17. `__BASE-FRANCHISE-API` is generated only after DP-API + SBM-API stabilization; DP-API becomes the first controlled derived API and common capabilities remain optional/configurable per franchise.
18. Git Markdown remains Documentation source of truth for the first Notion integration; Notion is a controlled downstream projection.
19. Context Objectives remain canonical initially; Jira is the synchronized Project→Epic→Issue/Task backlog and Scrum Agent becomes its future operator.
20. `SBM_AGENT.md` is the minimal clean-chat bootstrap and consumes `INIT_CONTEXT.md`, which remains the sole operational contract.
21. Transversal Git Flow and common-artifact propagation are controlled only from `SBM-SUITE/context`; repository inventory remains dynamically owned by `scripts/suite-repositories.py`.

## 14. Accepted risks and constraints

- The current workflow is manual.
- Context and documentation consistency depends on completing both workflows when required.
- RAG retrieval may omit required source sections; unsafe patches must then be omitted.
- Project contexts for remaining repositories may not yet exist or may be incomplete.
- Documentation format and page authorization are not yet implemented.
- Notion and Jira synchronization are not yet implemented.
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
3. Create and onboard the production-target brand APIs `KS-API`, `PC-API` and `CG-API`.
4. Implement `SBM-CORE`, `SBM-CALCULATION` and `SBM-UTIL` with explicit responsibility boundaries.
5. Expand the identity model through SBM User → Franchise/Brand User → Client/User → Customer/User where the business flow requires it.
6. Execute SBM-DB objectives for Equipment, Package, Catalog composition, pricing/FX, procurement/accounting traceability and brand-specific data models; do not infer these changes as implemented before Flyway/DBML evidence exists.
7. Create the control planes `SBM-AI-MANAGER`, `SBM-SECURITY` and `SBM-CONTROL`.
8. Create `SBM-MARKETING` and `SBM-CONTENT` with their agent/tool integrations.
9. Create brand stores/mobile/client/customer channels according to the pending objective inventory.
10. Add transversal object storage for documents, plans, assets and evidence.
11. Define production topology for KS/PC/CG; keep SonarQube as temporary QA infrastructure rather than permanent production runtime.
12. Correct the pending `objective-git-finalize` upstream/publication behavior.
13. Implement controlled Documentation→Notion and Objectives→Jira synchronization, then hand backlog operation to Scrum Agent when OBJ-CTX-006 is activated.
14. Standardize project onboarding, transversal Context/script propagation and SBM_AGENT.md bootstrap before multiplying new repositories.
15. Create __BASE-FRANCHISE-API only after DP-ARCH-001 proves DP-API + SBM-API integration; then register DP-API as the first controlled derived API.

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
