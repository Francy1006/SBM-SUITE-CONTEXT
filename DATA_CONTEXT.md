# DATA_CONTEXT.md

> **Last updated:** 2026-08-16
>
> **Purpose**
>
> Persistent transversal data context for **SBM Suite**. It defines data ownership, databases, schemas, core entities, relationships, contracts, classification, lifecycle, integrity, migrations, retention, backup, recovery and observability.
>
> **Accuracy note**
>
> Only verified schemas, entities, relationships, classifications and lifecycle rules may be recorded as implemented. Unknown values remain `N/A`.

## 1. Data architecture overview

SBM Suite uses PostgreSQL as the primary relational data platform.

Canonical ownership:

```text
Physical schema
→ SBM-DB

Versioned database changes
→ Flyway

Application access
→ responsible brand API or SBM-API

AI access
→ approved API Tools only

Vector search
→ Qdrant
```

Application repositories consume the schema but do not own business-schema migrations unless explicitly authorized.

## 2. Data ownership

| Data domain | Source of truth | Operational owner | Schema owner | Access path |
|---|---|---|---|---|
| Brand business data | PostgreSQL | Brand API (`DP-API` reference; `KS-API`/`PC-API`/`CG-API` planned) | SBM-DB | Responsible brand API |
| Internal platform data | PostgreSQL | SBM-API | SBM-DB | SBM-API |
| Physical schema and migrations | Flyway / DBML | SBM-DB | SBM-DB | Flyway |
| Global contexts | Git Markdown | SBM-SUITE | SBM-SUITE | Context workflow |
| Project contexts | Git Markdown | Project owner | SBM-SUITE / project | Context workflow |
| Documentation | Git Markdown | SBM-SUITE | SBM-SUITE | Documentation workflow |
| Confluence knowledge | Confluence | Documentation owner | Confluence | SBM-AI-ASSISTANT |
| Vector indexes | Qdrant | SBM-AI-ASSISTANT | SBM-AI-ASSISTANT | Vector API |
| QA evidence | Generated artifacts | Project owner | Project owner | QA workflow |

## 3. Databases and schemas

| Database/platform | Schema/logical domain | Owner project | Brand/domain | Purpose | Migration owner | Status |
|---|---|---|---|---|---|---|
| PostgreSQL | `ditaly_pasta` | SBM-DB | Ditaly Pasta | Historical/reference brand operational/commercial data | Flyway | active-reference |
| PostgreSQL | `sbm_business` | SBM-DB | SBM | Shared platform/business reference data | Flyway | active |
| PostgreSQL | `public` | SBM-DB | SBM | Shared technical objects where applicable | Flyway | active |
| PostgreSQL | TBD | future KS domain | KS | Brand operational/commercial data | SBM-DB/Flyway | planned |
| PostgreSQL | TBD | future PC domain | PC | Service/scheduling/client/customer data | SBM-DB/Flyway | planned |
| PostgreSQL | TBD | future CG domain | CG | Procedure/document/workflow data | SBM-DB/Flyway | planned |
| PostgreSQL | TBD | SBM-CORE | SBM | Async process flags/job/workflow state | SBM-CORE schema contract + approved migration ownership | planned |
| PostgreSQL | TBD | SBM-SECURITY-API | SBM | Security runs/findings/evidence/policies/approvals/audit | SBM-SECURITY-API migrations/schema contract | planned |
| PostgreSQL | N/A | SonarQube infrastructure | SBM | QA/static-analysis persistence only | SonarQube stack | QA-only |
| Qdrant | `sbm_docs` | SBM-AI-ASSISTANT | SBM | Confluence documentation vectors | SBM-AI-ASSISTANT | active |
| Qdrant | `sbm_contexts` | SBM-AI-ASSISTANT | SBM | Global/project context vectors | SBM-AI-ASSISTANT | active |
| Qdrant | `sbm_documentation` | SBM-AI-ASSISTANT | SBM | Git documentation vectors | SBM-AI-ASSISTANT | planned |

Exact KS/PC/CG physical database/schema names are intentionally `TBD` until the SBM-DB topology objective is implemented.

## 4. Core entities

| Entity | Operational owner | Data state | Description | Sensitive |
|---|---|---|---|---:|
| Product | Brand API | DP implemented/reference; reusable | Purchased item intended for resale | 0 |
| Material | Brand API | DP implemented/reference; reusable | Operational/production input not primarily sold | 0 |
| Service | Brand API | existing concept + planned extension | Contracted/performed service, fee, commission or logistics component | depends |
| Equipment | Brand API | planned | Retained/fixed asset; future rental/maintenance/spares | 0 |
| Package | Brand API / SBM-DB | normalization planned | Mandatory item packaging/logistics relation; Service uses logical package | 0 |
| Catalog | Brand API | existing concept + planned composition | BOM/recipe/acquisition composition | 0 |
| CatalogComponent | Brand API | planned | Typed component reference with quantity/dosage/unit/cost semantics | 0 |
| Ticket | Brand API | existing concept + generalized semantics | Sold/reported/scheduled commercial unit | depends |
| Price | Brand API / SBM-CALCULATION | existing + planned extension | Versioned monetary state, tax, currency and FX reference | 0 |
| ExchangeRate | SBM-UTIL / calculation consumers | planned | Authoritative observed rate and source/time metadata | 0 |
| Provider | Brand API | existing | Supplier/service provider | 1 |
| Branch | Brand API | existing | Physical/operational location | 1 |
| Agreement | Brand API | existing | Commercial/contractual conditions | 1 |
| Franchise | SBM-API | existing | Canonical brand/business authorization scope | 1 |
| Client | Brand API | existing/brand evolution | Direct customer organization/person of a brand | 1 |
| Customer | Brand API | planned generic; required PC | Downstream beneficiary/end customer | 1 |
| User/Role/Permission/Restriction | SBM-API + scoped brand auth | existing/evolving | Authentication/authorization structures | 1 |
| Schedule/Referral/QR | PC-API | planned | PC event/referral and confirmation lifecycle | 1 |
| Document/Plan/WorkflowStage | CG-API | planned | CG procedure files/plans/dependencies/stages | 1 |
| AsyncJob/ProcessFlag | SBM-CORE | planned | Durable async execution state | 0/1 |
| SecurityRun/Finding/Evidence/Approval | SBM-SECURITY-API | planned | Security execution, tool result, risk, evidence and human/agent gate decision | 1 |
| Context/Documentation | SBM-SUITE | existing | Governed Git knowledge | 0/1 |
| Vector chunk | SBM-AI-ASSISTANT | existing | Rebuildable embedded fragment | depends on source |

`planned` rows do not assert current PostgreSQL tables.

## 5. Entity relationships

Validated/current authorization baseline:

```text
Franchise/brand scope
→ users
→ roles
→ permissions
→ restrictions
```

Target business hierarchy:

```text
SBM User
→ Franchise/Brand User
→ Client / Client User
→ Customer / Customer User when applicable
```

Target commercial composition:

```text
Product / Material / Service / Equipment
→ mandatory Package
→ CatalogComponent(quantity/dosage/unit)
→ Catalog
→ Ticket
→ Price/version/currency/tax
```

Brand-specific extensions:

```text
KS Catalog/acquisition → purchase-specific import Service instances → provision vs actual cost
PC Ticket → schedule/referral/QR confirmation → commission/subscription settlement
CG Ticket/Catalog → Service components → documents/plans/workflow stages/dependencies
```

Physical relationships remain subject to PostgreSQL/Flyway/DBML evidence and must not be inferred from this target model alone.

## 6. Data flows

Brand operation:

```text
Brand/Client/Customer channel
→ responsible brand API
→ PostgreSQL business domain
```

Shared platform operation:

```text
SBM/admin channel
→ SBM-API
→ shared platform data
```

Async flow target:

```text
API/event/schedule
→ SBM-CORE
→ durable state/queue/worker
→ authorized service/API
```

Financial calculation target:

```text
Brand API
→ SBM-CALCULATION
→ deterministic result
→ brand-owned persistence/transaction
```

External deterministic integration target:

```text
Authorized service/agent
→ SBM-UTIL
→ email / external API / exchange-rate provider / file utility
```

AI-assisted operation:

```text
Authorized caller
→ SBM-AI-ASSISTANT
→ Tool/agent
→ responsible API/service
→ no direct PostgreSQL write
```

Context/documentation/Qdrant flows remain governed by the existing Context and Documentation workflows.

## 7. Data contracts

Every public data contract must define:

- owning project;
- endpoint;
- HTTP method;
- request schema;
- response schema;
- authentication;
- authorization;
- tenant scope;
- nullable fields;
- identifiers;
- versioning behavior;
- error contract;
- audit behavior.

Any endpoint, method, request body or response change must update:

```text
SUITE_CONTEXT.md
project PROJECT_CONTEXT.md
project QA_CONTEXT.md
global QA_CONTEXT.md when applicable
```

## 8. Data classification

| Classification | Description | Examples | Required handling |
|---|---|---|---|
| public | Safe for public disclosure | Public documentation | Normal integrity controls |
| internal | Internal operational information | Contexts, project structure | Access-controlled |
| confidential | Client or business information | Products, prices, providers | Tenant-scoped access |
| restricted | Highly sensitive operational data | Credentials, audit, personal data | Least privilege and encryption |
| secret | Authentication or infrastructure secrets | Tokens, passwords, private keys | Never stored in Git or Qdrant |

## 9. Sensitive data

Sensitive data may include:

- names;
- email addresses;
- phone numbers;
- addresses;
- geographic data;
- banking information;
- user identifiers;
- roles and permissions;
- audit records;
- credentials and tokens;
- provider contacts;
- branch contacts;
- support ticket contents;
- PC patient identity, health/prevision and appointment data;
- CG SII/business documents, plans and procedure records;
- KS client/device/camera access metadata where applicable.

Rules:

1. Minimize collection.
2. Restrict access by tenant and role.
3. Exclude secrets from logs and embeddings.
4. Do not place unrestricted personal data in context files.
5. Protect exports and backups.
6. Record classification and owner.
7. Apply retention and deletion rules.
8. Use secure transport outside trusted local environments.

## 10. Data integrity

Required controls:

- primary and foreign keys;
- constraints;
- transactional writes;
- exact decimal handling;
- logical deletion where defined;
- version fields;
- confirmation state;
- audit metadata;
- idempotency;
- concurrency control;
- rollback on failure;
- schema compatibility validation.

Mandatory verification:

```text
PostgreSQL
↔ Flyway
↔ DBML
↔ application model
↔ serializer
↔ public API contract
```

## 11. Migration ownership

Canonical rules:

- SBM-DB owns physical database changes and Flyway/DBML evolution; it is not a runtime query gateway.
- Flyway owns versioned business-schema migrations.
- DBML represents the high-level relational design.
- Application repositories map existing business tables.
- Django migrations must not modify Flyway-owned business schemas.
- A project may own a migration only through an explicit architecture decision.
- Migration execution must be evidenced before being marked complete.

Migration change workflow:

```text
business or technical requirement
→ SBM-DB change
→ Flyway migration
→ DBML update
→ application mapping update
→ tests
→ context synchronization
```

## 12. Retention and deletion

Required distinctions:

```text
logical deletion
physical deletion
retention expiration
archive
backup retention
vector index deletion
```

Rules:

- physical deletion requires explicit authorization;
- logical deletion preserves auditability;
- deleted source documents must be removed or deactivated in vector indexes;
- context version retention must preserve at least the current and required historical versions;
- backup retention must be defined per environment;
- personal and sensitive data must not be retained indefinitely without business or legal justification.

Current exact retention periods:

```text
N/A
```

## 13. Backup and recovery

Required backup scopes:

- PostgreSQL databases;
- Flyway migrations;
- DBML;
- Git repositories;
- context files;
- documentation files;
- Qdrant collections when operationally required;
- QA evidence where required for audit.

Recovery principles:

1. Test restoration.
2. Preserve timestamps and versions.
3. Protect backup credentials.
4. Encrypt sensitive backups.
5. Validate integrity after recovery.
6. Document recovery point and recovery time targets.
7. Treat Qdrant as rebuildable when source documents remain available.

Current RPO and RTO:

```text
N/A
```

## 14. Data observability

Required observability fields where applicable:

- correlation ID;
- project;
- endpoint or job;
- user or service;
- tenant or brand;
- entity;
- action;
- timestamp;
- result;
- row or item count;
- validation errors;
- retry count;
- duration;
- source and destination;
- non-sensitive diagnostic details.

Data observability must not expose secrets or unrestricted personal data.

## 15. Data risks

| Risk ID | Domain | Description | Projects | Status | Evidence | Risk | Owner |
|---|---|---|---|---|---|---:|---|
| DATA-001 | Ownership | Application and database assumptions may diverge | DP-API, SBM-API, SBM-DB | open | Manual verification required | 5 | SBM-DB and API owners |
| DATA-002 | Tenant isolation | Queries may expose another tenant's data | DP-API, SBM-API, SBM-AI-ASSISTANT | open | Complete transversal evidence unavailable | 5 | API owners |
| DATA-003 | Migration control | Unauthorized Django migrations may alter Flyway-owned schemas | DP-API, SBM-API | open | Context rule only | 5 | API owners |
| DATA-004 | Legacy data | Shared or inconsistent historical records may violate current assumptions | DP-API, SBM-DB | open | Known legacy concern | 4 | DP-API / SBM-DB |
| DATA-005 | Vector data | Sensitive content may enter Qdrant without filtering | SBM-AI-ASSISTANT | open | Complete classification controls unavailable | 5 | SBM-AI-ASSISTANT |
| DATA-006 | Retention | Exact deletion and retention periods are undefined | All | open | No approved retention policy | 4 | SBM Suite |
| DATA-007 | Backup recovery | Recovery objectives and restoration tests are undefined | All | open | No complete evidence | 4 | Infrastructure owners |

## 16. Pending data work

1. Validate all current schemas against Flyway and DBML.
2. Complete entity ownership mapping.
3. Define authoritative identifiers.
4. Define tenant and brand columns per entity.
5. Define personal and sensitive data classification.
6. Define retention periods.
7. Define physical versus logical deletion rules.
8. Define backup RPO and RTO.
9. Test database restoration.
10. Define Qdrant deletion and reindex procedures.
11. Add data integrity and migration tests.
12. Define audit and correlation standards.
13. Add authoritative metrics endpoints for business counts.
14. Document complete sales and order data models.
15. Execute the approved SBM-DB objectives for multibrand isolation, Equipment/Package, Catalog BOM, pricing/FX and acquisition/accounting traceability.
16. Define PC restricted-data retention/access rules before production.
17. Define CG document/plan storage metadata and object-storage linkage.
18. Define SBM-CORE job/flag persistence independently from business calculation data.

## 17. Related documentation

Relevant documentation domains include:

- Data Architecture;
- Database;
- Development;
- Security and DevSecOps;
- QA and Testing;
- Observability;
- DevOps;
- Cloud;
- Roadmap;
- SBM Suite.

Paths must use:

```text
SBM-SUITE/context/documentation/pages/<page>/<page>.md
SBM-SUITE/context/documentation/pages/<page>/subpages/<subpage>.md
```

Specific page paths will be added after the documentation structure is finalized.

## 18. Planned multi-brand data evolution — 2026-08-16

No schema listed below is considered implemented until its SBM-DB objective is delivered through DBML/Flyway/PostgreSQL evidence.

### Brand/data topology

- Preserve `ditaly_pasta` historical data as reference/test evidence subject to security rules.
- Add isolated KS, PC and CG logical data domains with independent credentials/authorization boundaries.
- Prefer one manageable PostgreSQL service initially with explicit logical isolation; do not introduce one database container per brand solely for application separation.
- Cross-brand/transversal reads must use approved APIs, events or a dedicated analytics/read model; SBM-DB does not query brands as an application service.
- `SBM-CORE` owns its own operational state/flag/job persistence when created.

### Planned core entities/relations

| Entity/capability | State | Purpose |
|---|---|---|
| Equipment | planned | Retained/fixed asset; future rental/service/spares |
| Package canonical relation | planned-normalization | Mandatory association for Product, Material, Service, Equipment, Catalog and Ticket; Service uses logical package |
| CatalogComponent/BOM | planned | Product/Material/Service/Equipment composition, quantity, dosage and unit conversion |
| ExchangeRate | planned | Versioned source currency/rate observations such as USD, future EUR/UF |
| Procurement/document trace | planned | PO, invoice, purchase VAT, dispatch guide, transfer, sale and accounting references |
| Provision vs actual cost | planned | Import/logistics/warranty and other estimated-versus-paid costs |
| Customer | planned generic | Downstream customer/beneficiary; PC requires person/org variants |
| Schedule/Referral/QR confirmation | planned PC | PC operational event/referral lifecycle |
| Document/Plan/WorkflowStage | planned CG | Procedure documentation, plans, dependencies and stage/calendar state |
| AsyncJob/ProcessFlag | planned SBM-CORE | Durable workflow state, retries, scheduler and worker coordination |

### Sensitive brand-specific data

- PC may process patient identity, health/prevision and appointment information: classify as restricted and minimize exposure/logging/embedding.
- CG may store SII/business documentation, plans and client records: classify per document and restrict object access.
- KS client/device/camera integrations may expose operational/device information: require explicit authorization and secure transport.

### Price/currency target

Price evolution must preserve `base_net_amount`, calculated `net_amount`, VAT, additional taxes/retentions, `gross_amount`, currency and exchange-rate reference/history. `SBM-UTIL` may ingest authoritative external rates; `SBM-CALCULATION` owns deterministic calculation rules; brand APIs remain the business operation boundary.

### `__BASE-FRANCHISE-API` data contract

`SBM-DB-011` must define the reusable data contract only after DP-API + SBM-API stabilization. Shared models/migrations must be compatible with `__BASE-FRANCHISE-API`; franchise-specific structures remain explicit extensions/configuration and must not leak DP-only assumptions into the base. Derived APIs retain independent business configuration while shared schema evolution is propagated through controlled BASE lineage and validated migrations.


### Base-project lineage metadata

Derived project onboarding records at least `base_project`, `base_version_or_commit`, `last_inherited_version_or_commit`, `inheritance_status`, `explicit_divergences` and `last_sync_at`. This lineage belongs to project/context governance and must not be inferred from repository similarity.

### Security operational data boundary

`SBM-SECURITY-API` owns its PostgreSQL operational domain for Security runs, pentests/scans, tool executions, findings, evidence references, policies, mitigation/prevention plans, approvals/rejections and audit history. `SBM-CORE` may persist scheduling/job state only and must not own Security findings or Security policy.

## 19. Document boundary

This file defines transversal data ownership, schemas, entities, flows, classification, integrity, lifecycle, migration ownership, backup and risks.

It does not replace:

- live PostgreSQL inspection;
- Flyway migrations;
- DBML;
- project models;
- API schemas;
- security implementation;
- raw backup configurations;
- legal retention policy;
- QA execution evidence;
- documentation page content.

Verified database and repository evidence always takes precedence over stale context.
