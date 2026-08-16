# DECISIONS_CONTEXT.md

> **Last updated:** 2026-08-16
>
> **Purpose**
>
> Persistent decision context for **SBM Suite**. It records proposed, accepted, superseded and rejected architecture or product decisions, including context, alternatives, consequences, affected projects and related documentation.
>
> **Accuracy note**
>
> A decision may be marked as accepted only when explicit evidence exists. Proposals must not be represented as approved.

## 1. Decision process

Every material architecture or product decision must include:

- a unique ADR ID;
- date;
- status;
- decision statement;
- business or technical context;
- evaluated alternatives;
- consequences;
- affected projects;
- related documentation.

Allowed statuses:

```text
proposed
accepted
superseded
rejected
```

Decision lifecycle:

```text
proposed
→ reviewed
→ accepted or rejected
→ superseded when replaced
```

Rules:

1. Preserve historical decisions.
2. Do not delete superseded or rejected records.
3. Do not convert a proposal into an accepted decision without explicit evidence.
4. Link material changes to affected project contexts.
5. Link roadmap or documentation pages when available.
6. Use repository-relative paths.
7. Record consequences, including risks and migration impact.
8. Keep implementation status separate from decision status.

## 2. Active decisions

| ADR ID | Date | Status | Decision | Context | Alternatives | Consequences | Projects | Documentation |
|---|---|---|---|---|---|---|---|---|
| ADR-001 | 2026-07-30 | accepted | Git Markdown is the primary source of truth for contexts and documentation during the manual stage | Context and documentation require versioning, review and rollback | Database-first, Notion-first, Qdrant-first | Git controls history; Qdrant remains rebuildable; Notion synchronization is downstream | SBM-SUITE, SBM-AI-ASSISTANT | Roadmap / Context workflow |
| ADR-002 | 2026-07-30 | accepted | Qdrant collections remain separated by knowledge domain | Contexts, Confluence and documentation have different lifecycle and retrieval requirements | One shared collection | Uses `sbm_docs`, `sbm_contexts` and `sbm_documentation`; reduces retrieval contamination | SBM-AI-ASSISTANT | AI Engineering / Context workflow |
| ADR-003 | 2026-07-30 | accepted | Context upgrades use section-level patches instead of complete-document replacement | Full Markdown replacement increases token usage and unsafe reconstruction risk | Complete file replacement, unified diff | Lower token usage; exact heading validation required; synchronization rules become mandatory | SBM-SUITE, SBM-AI-ASSISTANT, DP-API | Context workflow |
| ADR-004 | 2026-07-30 | accepted | Project context changes synchronize with global project context | Suite roadmap requires current state from every project | Independent project-only updates | Global objective and project summaries remain current | All projects | Roadmap / Project context |
| ADR-005 | 2026-07-30 | accepted | Project QA context changes synchronize with global QA context | Transversal QA status requires summarized project evidence | Independent project QA only | Global QA remains current; project evidence remains detailed locally | All projects | QA and Testing |
| ADR-006 | 2026-07-30 | accepted | Context and documentation workflows remain separate | Their formats, sources, permissions, backups and outputs differ | One unified workflow | Separate scripts, prompts, Qdrant collections and backups | SBM-SUITE, SBM-AI-ASSISTANT, DP-API | Context workflow / Documentation workflow |
| ADR-007 | 2026-07-30 | accepted | SBM-DB and Flyway own physical business schema changes | Multiple APIs consume shared PostgreSQL schemas | Django migrations per application | Prevents schema divergence; application models remain mappings unless explicitly authorized | SBM-DB, DP-API, SBM-API | Data Architecture |
| ADR-008 | 2026-07-30 | accepted | DP-API owns client-facing business operations and SBM-API owns internal platform operations | Client and internal responsibilities require clear boundaries | Single shared API, ownership by physical table location | Reduces authorization ambiguity and duplicated ownership | DP-API, SBM-API, SBM-MANAGER, SBM-AI-ASSISTANT | SBM Suite architecture |
| ADR-009 | 2026-07-30 | accepted | SBM-AI-ASSISTANT uses explicit Tools and canonical APIs, never direct PostgreSQL writes | AI operations must preserve validation, identity, permissions and auditability | Direct database access, duplicated business logic | AI remains orchestrator; APIs remain authoritative | SBM-AI-ASSISTANT, DP-API, SBM-API | AI Engineering / Security |
| ADR-010 | 2026-07-30 | accepted | Product, Material, Service, Catalog and Ticket remain independent domains | Shared fields do not imply shared lifecycle or ownership | Unified generic item module | Each domain keeps explicit lifecycle, ownership and rules | DP-API, SBM-DB, SBM-MANAGER | Business modules |
| ADR-011 | 2026-07-30 | accepted | Project structure evidence is generated recursively and included in context deployment | RAG needs current project structure without manually copying trees | Manual tree descriptions, literal full `ls -ltrah` output | Adds `project-tree.txt`; excludes generated, secret and dependency paths; used only as structural evidence | DP-API, SBM-AI-ASSISTANT, all future projects | Context workflow |
| ADR-012 | 2026-07-30 | accepted | Context and documentation upgrades require backup, validation and atomic replacement | Generated ZIPs must not partially corrupt Git sources | Direct overwrite, manual copy without validation | Hash, path and structure validation precede replacement; rollback remains available | SBM-AI-ASSISTANT, DP-API, SBM-SUITE | Context workflow / Documentation workflow |

| ADR-017 | 2026-08-16 | accepted | Ditaly Pasta becomes historical/reference while KS, PC and CG are production-target brands | DP has one year of real operational data but the business is closed | Delete DP, treat DP as production | Preserve real data and reusable baseline; avoid production assumptions | DP-API, KS/PC/CG future projects | SBM Suite / Business |
| ADR-018 | 2026-08-16 | accepted | Use SBM User → Franchise/Brand User → Client/User → Customer/User when applicable; retain `franchise` as current DB brand scope | Brands require multiple operational audiences | Rename franchise now, flatten users | Preserves current schema naming while clarifying authorization levels | SBM-API, brand APIs, channels | Security / SBM Suite |
| ADR-019 | 2026-08-16 | accepted | Every item domain uses Package; Service uses an explicit logical/non-physical Package rather than NULL | Uniform item/package contracts are required | Nullable Package for Service | Simplifies generic item handling while preserving service semantics | SBM-DB, brand APIs, SBM-MANAGER | Data / Business |
| ADR-020 | 2026-08-16 | accepted | Catalog is the configurable BOM/recipe/acquisition composition; Ticket is the sold/reported/scheduled commercial unit | DP/KS/PC/CG reuse the same composition pattern with different semantics | Treat Catalog as simple publication list; merge Ticket and Catalog | Enables dosage, import cost composition, service scheduling and consistent reporting | SBM-DB, brand APIs, stores | Business / Commerce |
| ADR-021 | 2026-08-16 | accepted | SBM-DB remains Flyway/DBML/schema authority and is not a runtime cross-brand query gateway | Multi-brand data must stay isolated and authoritative | One PostgreSQL container per brand by default; query through SBM-DB | Initial shared PostgreSQL can use logical isolation; transversal reads use APIs/events/read models | SBM-DB, all APIs | Data Architecture |
| ADR-022 | 2026-08-16 | accepted | Separate SBM-CORE infrastructure/workflow orchestration from SBM-CALCULATION business financial logic | Async scheduling/queues and financial rules have different ownership | Put calculation engine inside SBM-CORE | Cleaner boundaries, independent scaling/testing, reusable calculation service | SBM-CORE, SBM-CALCULATION, brand APIs | Automation / Finance |
| ADR-023 | 2026-08-16 | accepted | SBM-UTIL may use Java Spring Boot as a polyglot deterministic integration service | Portfolio and decoupling benefit from technology diversity when responsibility remains clear | Implement every service in Python | Demonstrates interoperability without duplicating agent/business logic | SBM-UTIL, SBM-AI-ASSISTANT, SBM-CORE | Technologies / Integration |
| ADR-024 | 2026-08-16 | accepted | Use separate control planes: SBM-AI-MANAGER for agents, SBM-SECURITY for security processes and SBM-CONTROL for suite operations | Agent/security/operations responsibilities differ | One oversized administration frontend | Keeps UI ownership and permissions bounded | SBM Suite | Operations / Security / AI |
| ADR-025 | 2026-08-16 | accepted | Separate channel audiences: SBM-MOBILE for SBM User, brand `*-mobile` for Franchise User, `*-client` for Client User, and customer-specific apps only when needed | KS/PC/CG require different actors | One mobile app for every audience | Allows shared patterns without conflating permissions/business flows | Mobile/client projects | Digital Channels |
| ADR-026 | 2026-08-16 | accepted | Kafka is used only when durable event-streaming/integration semantics justify it; Celery/Redis remains appropriate for task execution | Async stack must not add infrastructure without purpose | Always deploy Kafka with Celery | Lower operational overhead and clearer event/task boundaries | SBM-CORE | Automation / DevOps |
| ADR-027 | 2026-08-16 | accepted | SonarQube is QA infrastructure and does not need permanent production runtime | Static analysis is development/release validation, not business runtime | Keep SonarQube 24x7 in production | Lower steady-state resource use; start Sonar only when QA requires it | QA / Infrastructure | DevOps / Cloud |

| ADR-029 | 2026-08-16 | accepted | Generalize client-facing ownership from DP-API to the responsible brand API; DP-API remains the historical/reference implementation | KS/PC/CG require independent business APIs while SBM-API remains shared platform authority | Keep all brands behind DP-API; use SBM-API for brand business logic | Preserves domain ownership and allows brand specialization without cross-brand coupling | DP-API, KS-API, PC-API, CG-API, SBM-API | SBM Suite architecture |

| ADR-030 | 2026-08-16 | accepted | Canonical application/project display names are uppercase; existing filesystem/runtime/registry identifiers remain literal until explicitly migrated | Architecture discussions need one naming convention without breaking current paths | Rename repositories immediately; retain mixed display casing | Clear canonical names while avoiding accidental path/runtime changes | All projects | SBM Suite / Context |
| ADR-031 | 2026-08-16 | accepted | Reusable project families use `__BASE-*` repositories with tracked lineage and controlled agent-validated inheritance; `__BASE-FRANCHISE-API` is generated only after DP-API + SBM-API are stabilized, using validated DP-API as the seed and registering DP-API as the first derived API | Brand/channel projects repeat architecture but require a proven reference, optional/configurable modules and safe propagation | Clone DP-API ad hoc; generate BASE before stabilization; manual copy; shared monolith | Adds prerequisite sequencing, base version/commit metadata, feature configuration, derived divergences and controlled sync/rollback; Yeoman may scaffold initial projects but does not own ongoing inheritance | Base and derived brand/channel projects | SBM Suite / DevOps |
| ADR-032 | 2026-08-16 | accepted | Security is isolated behind SBM-SECURITY-API (Go/Gin/PostgreSQL); named Security agents live in SBM-AI-ASSISTANT; SBM-SECURITY is the human front; SBM-CORE schedules jobs only | Security findings/policy/evidence should not be owned by the generic async platform | Put Security domain logic in SBM-CORE; scanners write directly to UI | Stronger boundary, independent persistence/audit and safer tool orchestration | SBM-SECURITY-API, SBM-SECURITY, SBM-AI-ASSISTANT, SBM-CORE | Security / SBM Suite |
| ADR-033 | 2026-08-16 | accepted | SBM-MARKETING is a Node.js/TypeScript/NestJS API owning marketing operations and social data | Marketing requires persistent workflows, webhooks, scheduling, campaigns and operational records | Python-only utility; agent-only tools | Adds a real Node.js API while keeping domain ownership deterministic | SBM-MARKETING, SBM-AI-ASSISTANT | Marketing / Technologies |
| ADR-034 | 2026-08-16 | accepted | SBM-CONTENT uses Python/FastAPI for content/asset production workflows and AI/creative-tool integrations | Content workflows benefit from the Python AI/media ecosystem | Fold content into Marketing API; frontend-only asset management | Keeps content production independently evolvable while integrating with named creative agents | SBM-CONTENT, SBM-AI-ASSISTANT | Marketing / Content / Technologies |
| ADR-035 | 2026-08-16 | accepted | The named-agent catalog is canonical and agents are activated on demand; APIs/services/jobs remain the default automation mechanism | Large specialist catalog must not imply permanent LLM execution or uncontrolled cross-domain access | Always-on agents; generic agent roles only | Preserves specialization while minimizing cost/risk and enforcing hierarchy/permissions | SBM-AI-ASSISTANT, SBM-CORE, control planes | AI Engineering / Governance |
| ADR-036 | 2026-08-16 | accepted | Adopt Git Flow as the target transversal Git lifecycle after repairing the current objective finalizer | Current objective branches merge directly to main and need stronger release/branch governance | Keep direct-to-main permanently; ad-hoc branches | Introduces develop/feature/bugfix/hotfix/release semantics with QA/Security gates and controlled migration | All Git repositories | DevOps / Context |
| ADR-037 | 2026-08-16 | accepted | Upgrade input discovery will accept exactly one workflow-prefixed ZIP (`context-upgrade*.zip` or `documentation-upgrade*.zip`) while keeping the canonical manifest workflow/output contract | ChatGPT/client downloads may append suffixes such as `(32)`, forcing unnecessary manual renames | Require exact physical filename forever; accept arbitrary ZIP names | Removes manual rename friction without weakening workflow, manifest, ambiguity or ZIP validation | SBM-SUITE/context | Context workflow / Documentation workflow |
| ADR-014 | 2026-08-16 | accepted | Implement controlled one-way Git/Markdown → Notion synchronization first; Git Markdown remains the documentation source of truth and bidirectional synchronization is deferred | Documentation is versioned and reviewed in Git but needs Notion publication/consumption | Git-only; Notion-first; immediate bidirectional sync | Requires stable page identity, hierarchy mapping, change detection and audit while avoiding conflict-resolution complexity in the first iteration | SBM-SUITE, SBM-UTIL, SBM-AI-ASSISTANT | Documentation workflow |
| ADR-038 | 2026-08-16 | accepted | Project Objectives are synchronized to Jira as Project → Epic → Issue/Task backlog with stable Objective ID↔Jira ID mapping; Context remains canonical initially and Scrum Agent becomes the future backlog operator | Backlog needs operational Jira visibility without duplicating or losing Context objective identity | Jira-only source of truth now; manual duplicate backlog; agent-only backlog | Requires deterministic mapping, state/priority/dependency synchronization and duplicate prevention | SBM-SUITE, SBM-UTIL, SBM-AI-ASSISTANT | Objectives / Backlog / Jira |
| ADR-039 | 2026-08-16 | accepted | New-chat bootstrap uses a minimal `SBM_AGENT.md` that consumes `INIT_CONTEXT.md`; INIT_CONTEXT remains the operational contract | A clean ChatGPT session needs a small stable entry artifact without duplicating the large lifecycle specification | Rename/remove INIT_CONTEXT; keep planned SBM_AGENT_INIT; duplicate full prompt | Separates bootstrap from lifecycle contract and reduces drift | SBM-SUITE/context, SBM-AI-ASSISTANT | Context workflow |

## 3. Proposed decisions

| ADR ID | Date | Status | Decision | Context | Alternatives | Consequences | Projects | Documentation |
|---|---|---|---|---|---|---|---|---|
| ADR-028 | 2026-08-16 | proposed | Add Kiseki rental domain later with contracts, Equipment inventory, technical service and spare-parts inventory | Current KS priority is sale/import, not rental | Implement rental now | Keeps immediate production scope smaller while preserving Equipment evolution path | KS-API, SBM-DB, future KS channels | Roadmap |
| ADR-013 | 2026-07-30 | proposed | Move workflow orchestration to database flags and asynchronous processing | Current context and documentation workflow is manual | Keep manual scripts permanently, scheduler-only processing | Enables automatic status control, retries and multi-project orchestration; requires persistence and workers | SBM-AI-ASSISTANT, SBM-DB, all projects | Roadmap / Automation |

| ADR-015 | 2026-07-30 | proposed | Introduce asynchronous DP-API to SBM-API orchestration for selected workflows | Some client operations may require internal platform actions | Direct synchronous call, shared database write | Requires durable queue, retries, idempotency and audit | DP-API, SBM-API | Architecture / Roadmap |
| ADR-016 | 2026-07-30 | proposed | Standardize context and documentation metadata across Git, Qdrant and future database records | Retrieval, synchronization and conflict handling require stable identity | Path-only identity, ad hoc metadata | Adds objective ID, project, source of truth, content hash, paths and timestamps | SBM-SUITE, SBM-AI-ASSISTANT, SBM-DB | Data Architecture / Context workflow |

## 4. Superseded decisions

| ADR ID | Date | Status | Decision | Context | Alternatives | Consequences | Projects | Documentation |
|---|---|---|---|---|---|---|---|---|
| ADR-S001 | 2026-07-30 | superseded | Context upgrade replaces complete Markdown files | Initial implementation exported complete authorized files | Section-level patches | Replaced by ADR-003 due to token usage and reconstruction risk | SBM-SUITE, SBM-AI-ASSISTANT, DP-API | Context workflow |
| ADR-S002 | 2026-07-30 | superseded | QA contexts remain protected from context upgrade | Initial workflow avoided modifying QA without complete evidence | Synchronized QA patches based on generated evidence | Replaced by ADR-005; QA updates now require explicit evidence and global synchronization | All projects | QA and Testing |
| ADR-S003 | 2026-07-30 | superseded | Global project context lives at `SBM-SUITE/PROJECT_CONTEXT.md` | Early path definition placed it at suite root | `SBM-SUITE/context/PROJECT_CONTEXT.md` | Canonical path is now under `context/` | SBM-SUITE, SBM-AI-ASSISTANT | Context workflow |

## 5. Rejected alternatives

| ADR ID | Date | Status | Decision | Context | Alternatives | Consequences | Projects | Documentation |
|---|---|---|---|---|---|---|---|---|
| ADR-R001 | 2026-07-30 | rejected | Use Qdrant as the primary source of truth | Vector storage is optimized for retrieval, not authoritative versioning | Git Markdown | Rejected because indexes must remain rebuildable | SBM-AI-ASSISTANT, SBM-SUITE | Context workflow |
| ADR-R002 | 2026-07-30 | rejected | Allow AI to write directly to PostgreSQL | Direct writes appear simpler for automation | Explicit Tools through canonical APIs | Rejected due to validation, authorization, ownership and audit risks | SBM-AI-ASSISTANT, APIs | Security / AI Engineering |
| ADR-R003 | 2026-07-30 | rejected | Merge Product, Material and Service into one generic item domain | Entities share several fields | Independent domain apps | Rejected because lifecycle, pricing and ownership differ | DP-API, SBM-DB | Business modules |
| ADR-R004 | 2026-07-30 | rejected | Use one Qdrant collection for all knowledge | Simplifies initial infrastructure | Separate collections | Rejected due to retrieval contamination and different lifecycle rules | SBM-AI-ASSISTANT | AI Engineering |
| ADR-R005 | 2026-07-30 | rejected | Use literal recursive `ls -ltrah` output as permanent context content | User requested complete project structure visibility | Filtered `project-tree.txt` structural evidence | Rejected because raw output creates excessive noise and may expose secrets or generated paths | All projects | Context workflow |

## 6. Decision impact

| ADR ID | Architecture | Business | Security | Data | QA | Deployment |
|---|---|---|---|---|---|---|
| ADR-001 | Git-first lifecycle | none | reviewable changes | Git as source | traceable evidence | manual stage |
| ADR-002 | separate retrieval domains | none | lowers cross-domain leakage | separate indexes | independent validation | extra collection management |
| ADR-003 | patch-based upgrade | none | restricted targets | section-level updates | validator tests required | atomic patch application |
| ADR-004 | global synchronization | roadmap visibility | none | global summaries | synchronization tests | workflow update |
| ADR-005 | QA synchronization | release visibility | security evidence included | QA metadata | central summary | workflow update |
| ADR-006 | separate workflows | clearer documentation lifecycle | separate allowlists | separate sources | separate test suites | separate scripts and backups |
| ADR-007 | database ownership | stable business schema | fewer unauthorized changes | Flyway authority | migration tests | migration process |
| ADR-008 | API ownership | clear client/internal responsibility | reduced privilege ambiguity | controlled access paths | contract tests | separate services |
| ADR-009 | API-mediated AI | safe AI operations | preserves authorization | no direct DB access | Tool tests | API dependencies |
| ADR-010 | domain separation | explicit business capabilities | scoped permissions | independent entities | domain test suites | independent modules |
| ADR-011 | structural evidence | none | exclusions required | no source-of-truth change | export tests required | new script execution |
| ADR-012 | safe upgrades | none | path/hash validation | protected Git files | rollback tests | backup and atomic replacement |
| ADR-030 | canonical naming | none | none | no path mutation | documentation consistency | explicit migration required for real renames |
| ADR-031 | reusable base/derived project lineage | faster project onboarding | agent/QA/Security-gated propagation | lineage metadata | inheritance regression required | controlled base sync/rollback |
| ADR-032 | isolated Security API/control plane | release risk governance | stronger tool/policy boundary | dedicated Security DB | Security gate follows QA | reject returns to Development |
| ADR-033 | Node.js Marketing API | marketing operations ownership | scoped social/payment/provider permissions | marketing operational persistence | API/integration tests | independent service deployment |
| ADR-034 | Python Content API/service | content production ownership | asset/tool permissions | content metadata/storage references | media/workflow tests | independent service deployment |
| ADR-035 | named on-demand agents | automated specialist workflows | least privilege/activation governance | audited agent state | agent/eval tests | controlled activation |
| ADR-036 | Git Flow target | predictable release lifecycle | Security gate before protected merges | Git metadata only | QA gates on branch transitions | develop/release/main governance |
| ADR-037 | workflow-prefixed upgrade ZIP discovery | no business impact | strict one-file + manifest validation | no source-of-truth change | filename-discovery regression tests | no manual rename required |
| ADR-014 | Git→Notion documentation projection | shared documentation visibility | controlled API credentials/scopes | Git remains canonical | sync/idempotency tests | downstream Notion publication |
| ADR-038 | Context→Jira backlog synchronization | operational backlog visibility | scoped Jira permissions/audit | stable Objective↔Jira mapping | sync/duplicate regression tests | future Scrum Agent operation |
| ADR-039 | SBM_AGENT.md bootstrap | cleaner new-chat startup | no new privilege boundary | INIT_CONTEXT remains canonical | bootstrap contract tests | no runtime deployment impact |

## 7. Decision references

Decision references must use repository-relative paths.

Relevant context files:

```text
SBM-SUITE/context/PROJECT_CONTEXT.md
SBM-SUITE/context/SUITE_CONTEXT.md
SBM-SUITE/context/BUSINESS_CONTEXT.md
SBM-SUITE/context/QA_CONTEXT.md
SBM-SUITE/context/SECURITY_CONTEXT.md
SBM-SUITE/context/DATA_CONTEXT.md
SBM-SUITE/context/DECISIONS_CONTEXT.md
```

Relevant documentation domains:

- Architecture;
- Roadmap;
- Development;
- AI Engineering;
- Data Architecture;
- Security and DevSecOps;
- QA and Testing;
- DevOps;
- Automation;
- SBM Suite.

Specific documentation paths will be added when the documentation tree is finalized.

## 8. Document boundary

This file stores summarized architecture and product decisions.

It does not define:

- implementation completion;
- current QA results;
- live database state;
- source code behavior;
- deployment status;
- business metrics;
- secret values;
- full ADR discussion transcripts;
- documentation page content.

Detailed evidence remains in Git history, project contexts, QA artifacts, database sources and related documentation.
