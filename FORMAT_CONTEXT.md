# FORMAT_CONTEXT.md

> **Purpose**
>
> Canonical structure contract for every SBM Suite context file.
> Context generation and upgrade processes must preserve these formats exactly.

## 1. Global rules

1. Preserve the exact heading names and order defined here.
2. Do not rename, merge, split, reorder or remove required sections.
3. Add content only inside the matching section.
4. Preserve the metadata block at the beginning of each file.
5. Preserve Markdown lists, tables, code blocks and repository-relative paths.
6. Do not duplicate information across sections.
7. Do not create unsupported facts, tests, migrations, deployments, metrics or decisions.
8. When evidence is insufficient, keep existing content unchanged.
9. Structural changes require an explicit update to this file.
10. All dates use `YYYY-MM-DD`.
11. Context updates use section-level patches; complete-file replacement is forbidden.
12. A project `PROJECT_CONTEXT.md` change must update the global `PROJECT_CONTEXT.md`.
13. A project `QA_CONTEXT.md` change must update the global `QA_CONTEXT.md`.
14. Git is the primary source of truth during the manual workflow stage.
15. Objective, implementation, QA, business and documentation state must remain separate.
16. Context and documentation use separate Qdrant collections.
17. Context files reference documentation using repository-relative paths.
18. Completed objectives are removed from operational objective tables and appended only to `SBM-SUITE/context/COMPLETED_OBJECTIVES.md`; discarded objectives are removed from operational tables.
19. Protected files remain read-only unless their workflow explicitly authorizes modification.
20. Every file must preserve its declared document boundary.
21. `FORMAT_CONTEXT.md` is the only authority for context and README structure.
22. The LLM must not infer missing headings, tables, paths, statuses, values or output files.
23. Every generated patch must be validated before it is included in the output ZIP.
24. A patch that cannot be proven valid must be omitted and reported in `EXECUTIVE_README.md`.
25. Input evidence files and protected workflow files are never authorized output files.
26. `manifest.allowed_files` and `manifest.updated_files` must be derived only from valid files actually permitted in the output ZIP.
27. The source manifest must never be copied as the output manifest.
28. Output paths must be exact, repository-relative, unique and free of `..`, absolute paths and symlinks.
29. Every output file except `manifest.json` requires a SHA-256 hash matching its final ZIP content.
30. Any global validation failure must prevent context replacement.
31. Project repositories use repository-relative paths under `SBM-SUITE/<brand>/<project>/`. The suite-scoped lifecycle target `sbm-suite-context` is the explicit exception and resolves directly to `SBM-SUITE/context/`. Canonical routing is defined by the backend Project Registry and must be consumed from the source manifest/contract rather than inferred from `project_name`.
32. Project roots exposed by the context contract are repository-relative and must match the backend Project Registry exactly. Current required mappings include:
    - `dp-api` → `SBM-SUITE/dp/DP-API/`
    - `sbm-manager` → `SBM-SUITE/sbm/SBM-MANAGER/`
    - `sbm-db` → `SBM-SUITE/sbm/SBM-DB/`
    - `sbm-suite-context` → `SBM-SUITE/context/`
   Never change path casing or derive brand/project segments heuristically. `sbm-suite-context` is suite-scoped and must never generate project-scoped targets such as `SBM-SUITE/context/context/...`.
33. All workflow backups are stored below `SBM-SUITE/context/backup/`; no workflow may use or create a pluralized or workflow-local backup directory.
34. For `planning-activation`, the validated source-manifest `objectives[]` array is immutable lifecycle input. Every `objective_id`, `objective`, `status`, `priority`, `target_date` and `branch` value must be copied literally into generated operational objective rows.
35. A context generator must never regenerate, normalize, translate, shorten, slugify, reinterpret or otherwise alter any field already present in a validated `planning-activation` `manifest.objectives[]` item.
36. Lifecycle field values must be plain literal table-cell values. Never wrap `objective_id`, `objective`, `status`, `priority`, `target_date` or `branch` in Markdown formatting such as backticks, bold, italics, links or code spans.
37. `execution_mode` is independent from `lifecycle_phase`. `USER_PROMPT.md` is required only when `execution_mode=user-guided` and forbidden when `execution_mode=evidence`; `planning-activation` alone must never force `USER_PROMPT.md`.
38. `sbm-suite-context` is a suite-scoped lifecycle target. Its operational objective and QA state live directly in global `SBM-SUITE/context/PROJECT_CONTEXT.md` and `SBM-SUITE/context/QA_CONTEXT.md`. Project-scoped patches (`project-context`, `project-qa-context`, `project-deploy-context`, `project-readme`) are forbidden for this target. Global objective rows for this target use `Project = SBM-SUITE`.
39. Every Markdown table must be one continuous block: no blank line is allowed between its header row, separator row or any data rows belonging to that table.
40. When adding rows to an existing Markdown table, all new rows must form one contiguous block immediately after its last existing data row and before any blank line, prose, heading or later section. Never create a second visually similar row block outside the table. This applies to every table and especially to the lifecycle `Pending objectives`, `Active objectives` and `Completed objectives` tables.
41. `SBM-SUITE/context/scripts/` is the sole canonical orchestration point for Context deploy, Context upgrade, Documentation deploy and Documentation upgrade. Project-local scripts are not workflow authorities.
42. The global Context deploy script must accept the selected `project_name`, validate it against the backend Project Registry contract and resolve its real project root only from the published `canonical_project_path`; it must never derive project paths from the project name. Documentation deploy is global and accepts no project selection or project argument.
43. The global Context upgrade script must obtain `project_name` from the trusted input ZIP manifest, validate it against the backend Project Registry contract and apply suite-scoped restrictions only when the selected target is `sbm-suite-context`. Documentation upgrade is global, accepts no project argument and may use only the fixed suite-scoped technical target required for backend compatibility.
44. `SBM-SUITE/context` owns the global workflow contracts and input/output directories, and `SBM-SUITE/context/scripts/project-tree.sh` is its sole canonical Project Tree script. Project Git changes and QA evidence are collected from the Project Registry-selected project root without duplicating those global resources.
45. `planning-activation` is objective creation only. It must reject any `objective_id` already present in active, pending, completed or cancelled lifecycle state.
46. `objective-activation` is the only lifecycle phase for an existing objective transition from `pending` to `active`. It requires exactly one full objective item whose desired `status` is `active`.
47. During `objective-activation`, preserve `objective_id`, `objective`, `priority`, `target_date` and `branch` literally from the existing pending row and change only `status`; reject missing, already-active, completed, duplicated or otherwise invalid objective IDs.
48. `objective-activation` must replace the complete applicable Active objectives and Pending objectives sections, remove exactly the selected pending row and insert exactly one active row. It must never reuse creation/insertion-only behavior or append completed history.

---

## 2. Global `PROJECT_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/PROJECT_CONTEXT.md
```

Required structure:

```text
# PROJECT_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Executive summary
## 2. Suite purpose
## 3. Active objectives
## 4. Pending objectives
## 5. Projects and ownership
## 6. Project objective summaries
## 7. Global architecture
## 8. Shared infrastructure
## 9. Cross-project integrations
## 10. Context deployment and upgrade workflow
## 11. Documentation deployment and upgrade workflow
## 12. Current implementation status
## 13. Validated decisions
## 14. Accepted risks and constraints
## 15. Completed work
## 16. Pending work
## 17. Required behavior
## 18. Historical decisions
## 19. Related documentation
## 20. Document boundary
```

Required table in both `## 3. Active objectives` and `## 4. Pending objectives`:

```text
| ID | Project | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---|---:|---|---|---|
```

Required table in `## 6. Project objective summaries`:

```text
| Project | Purpose | Active objective | Pending objectives | Branch | Main context | QA context | Documentation |
|---|---|---|---|---|---|---|---|
```

Objective rules:

- `Status` must match the owning section: `active` in Active objectives and `pending` in Pending objectives.
- `Priority`: integer from `0` to `5`.
- `Target date`: required lifecycle field; use `YYYY-MM-DD` or `N/A`.
- `Branch`: mandatory before development begins.
- Multiple objectives are allowed.
- `planning-activation` may carry multiple objectives in one `objectives` array.
- Every planning item must contain all six lifecycle fields: ID, objective, status, priority, target date and branch.
- Treat those six values as an immutable tuple supplied by `manifest.objectives[]`; generated project/global rows must match them exactly, character for character for string fields and exactly for numeric fields.
- Never regenerate or normalize an Objective ID, description, status, priority, target date or branch after the batch has been validated.
- Store lifecycle field values as plain literal table-cell values; never wrap `objective_id`, `objective`, `status`, `priority`, `target_date` or `branch` in Markdown formatting such as backticks, bold, italics, links or code spans.
- Reject the complete batch on any missing/invalid field, duplicate ID or collision with current/history IDs.
- A planning batch is atomic: for project-scoped targets every requested objective is synchronized exactly once in both project/global operational contexts; for `sbm-suite-context` it is written exactly once to the global operational context only.
- `objective-activation` accepts exactly one objective already present in Pending objectives and requires the complete desired item with `status=active`.
- During objective activation, preserve ID, objective, priority, target date and branch literally; move exactly one row from Pending objectives to Active objectives and change only status from `pending` to `active`.
- Reject objective activation when the ID is absent, already active, completed, duplicated, inconsistent between applicable project/global contexts or differs in any preserved lifecycle field.
- Every project-scoped objective change must update this global file. `sbm-suite-context` already owns this global file and must not generate a duplicate project-local objective row.
- The global file stores high-level project summaries and is also the direct operational objective context for `sbm-suite-context`.
- Detailed objectives remain in the project context for project-scoped targets.
- This context is the source for roadmap, backlog, epics and issues.
- Objectives assigned for immediate implementation are `active`.
- Objectives recorded for later work are `pending`.
- Completed objectives are removed from this file and appended only to the global completed-objectives register.

Branch nomenclature:

```text
<TYPE>-<slug>
```

Allowed types:

```text
FEATURE
BUGFIX
HOTFIX
```

Slug rules:

- maximum four words;
- lowercase;
- hyphen-separated;
- no spaces, accents or special characters.

Valid examples:

```text
FEATURE-implements-qa-procedure-context
BUGFIX-fixes-product-price-serializer
HOTFIX-restores-auth-token-validation
```


---

## 3. Global `COMPLETED_OBJECTIVES.md`

Required path:

```text
SBM-SUITE/context/COMPLETED_OBJECTIVES.md
```

Required structure:

```text
# COMPLETED_OBJECTIVES.md

> Last updated
> Purpose
> Accuracy note

## 1. Completed objectives by project
## 2. Document boundary
```

Required project grouping heading pattern:

```text
### <project>
```

Required table under each project heading:

```text
| Objective ID | Project | Objective | Final status | Priority | Branch | Started | Completed | Summary | Validation | Documentation | Proposed commit |
|---|---|---|---|---:|---|---|---|---|---|---|---|
```

Rules:

- This is the only completed-objectives file in SBM Suite.
- Do not create project-level completed-objectives files.
- Group completed objectives by project.
- Append only newly completed or cancelled objectives.
- Never include active or pending objectives.
- Do not rewrite unrelated historical records.
- This file is excluded from the operational development context used by Codex.
- Allowed final statuses: `completed`, `cancelled`.
- A completed objective requires explicit closure and canonical QA status `passed` or structurally verified `not-applicable`.
- Explicit implementation evidence is required only when the objective claims source-code, runtime, API, database, architecture or other implementation changes.
- A lifecycle-only or no-op objective may close with an empty Git diff when the objective exists in the current operational context, the requested lifecycle phase is `implementation-closure`, canonical QA is `passed` or structurally verified as `not-applicable`, and no unsupported implementation claim is introduced.
- Objective closure must also remove the objective from both project and global operational objective sections and update both project and global QA contexts in the same upgrade.
- `patches/completed-objectives.json` is allowed only in `implementation-closure`.
- `patches/completed-objectives.json` must contain exactly one operation targeting `## 1. Completed objectives by project`.
- Inspect the complete current `SBM-SUITE/context/COMPLETED_OBJECTIVES.md` source snapshot before choosing the operation, and ignore headings contained inside fenced code blocks.
- Resolve the exact canonical project grouping heading from the Project Registry; for `dp-api`, it is `### DP-API`.
- If the canonical project heading is absent outside fenced code blocks, use `append_to_section` and append exactly one new project heading, the exact required table header and exactly one row for the requested `objective_id`.
- If the canonical project heading exists exactly once, use `replace_section` and return the complete current `## 1. Completed objectives by project` section, preserving all preamble text, project headings, tables and unrelated rows while adding exactly one row under that existing heading.
- Never use `append_to_section` when the canonical project heading already exists.
- Never use `replace_section` to create a missing canonical project heading.
- Reject multiple canonical project heading matches, duplicate Objective IDs and duplicate project grouping headings.
- Existing historical records may be carried unchanged inside a complete `replace_section` snapshot, but they must never be modified, reordered or removed.
- Append exactly the requested `objective_id`; do not also copy it to `Completed work` in a project or global `PROJECT_CONTEXT.md`.


## 4. Global `SUITE_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/SUITE_CONTEXT.md
```

Required structure:

```text
# SUITE_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Suite identity
## 2. Product scope
## 3. Brands and platforms
## 4. Project map
## 5. Applications and services
## 6. Technology inventory
## 7. Runtime architecture
## 8. Data architecture
## 9. API inventory
## 10. Endpoint contracts
## 11. Authentication and authorization
## 12. Integrations and data flows
## 13. Infrastructure and containers
## 14. Shared configuration
## 15. Context and knowledge architecture
## 16. Deployment model
## 17. Security rules
## 18. Operational constraints
## 19. Current suite state
## 20. Context deployment lifecycle
## 21. Documentation lifecycle
## 22. Related documentation
## 23. Document boundary
```

Required tables:

```text
| Brand | Project | Application or service | Type | Description | Language | Framework | Version | Runtime | Owner |
|---|---|---|---|---|---|---|---|---|---|
```

```text
| Brand | Project | Category | Technology | Version | Purpose | Status |
|---|---|---|---|---|---|---|
```

```text
| Brand | API | Owner project | Base path | Audience | Authentication | Description | Status |
|---|---|---|---|---|---|---|---|
```

```text
| Brand | API | Method | Path | Request body | Response | Authentication | Purpose | Status |
|---|---|---|---|---|---|---|---|---|
```

Rules:

- Group data by brand; `SBM` is its own brand.
- Update for application, service, language, framework, version, container, integration or architecture changes.
- Update for endpoint creation, removal, method, path, request body or response changes.
- Use tables for inventories and contracts.
- Store suite relationships and boundaries, not project transcripts.

---

## 5. Global `BUSINESS_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/BUSINESS_CONTEXT.md
```

Required structure:

```text
# BUSINESS_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Business overview
## 2. Product vision
## 3. Business actors
## 4. Brands and franchises
## 5. Brand operational profile
## 6. Enabled modules by brand
## 7. Core business domains
## 8. Business entities
## 9. Business rules
## 10. Commercial flows
## 11. Pricing and fiscal concepts
## 12. Inventory and catalog concepts
## 13. Sales and order concepts
## 14. Provider and branch concepts
## 15. Documentation references
## 16. Terminology
## 17. Validated business decisions
## 18. Business constraints
## 19. Pending business definitions
## 20. Document boundary
```

Required tables:

```text
| Brand ID | Brand | Franchise | Description | Status | Source |
|---|---|---:|---|---|---|
```

```text
| Brand | Locales enabled | Local count | Client count | Product count | Ticket count | Stock tracked | Last updated | Source |
|---|---:|---:|---:|---:|---:|---:|---|---|
```

```text
| Brand | Module | Enabled | Description | Effective date | Source |
|---|---|---:|---|---|---|
```

Rules:

- Boolean values use `1 = true`, `0 = false`.
- Unknown counts use `N/A`.
- Never invent business metrics.
- Update when brands, franchises, business behavior or enabled modules change.
- Technical changes update this context only when business capability changes.

---

## 6. Global `QA_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/QA_CONTEXT.md
```

Required structure:

```text
# QA_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Suite QA overview
## 2. Quality policy
## 3. Quality gates
## 4. Project QA summaries
## 5. Test inventory
## 6. Coverage summary
## 7. Static analysis summary
## 8. Security validation summary
## 9. API validation summary
## 10. Database validation summary
## 11. Deployment validation summary
## 12. Defect classification
## 13. Risk classification
## 14. Release criteria
## 15. Accepted exceptions
## 16. Current QA status
## 17. Pending QA work
## 18. Related documentation
## 19. Document boundary
```

Required tables:

```text
| Project | QA context | Test count | Passed | Failed | Coverage | SonarQube status | Last execution | Overall risk | Evidence |
|---|---|---:|---:|---:|---|---|---|---:|---|
```

```text
| Test ID | Project | Description | Logic type | Components | Risk | Last execution | Result | Evidence |
|---|---|---|---|---|---:|---|---|---|
```

Risk scale:

```text
0 = none
1 = very low
2 = low
3 = medium
4 = high
5 = critical
```

Rules:

- `qa-check.sh` executes tests, coverage and SonarQube.
- `context-deploy` extracts and packages QA evidence.
- `context-upgrade` updates project and global QA contexts.
- New, removed or changed tests update both QA contexts.
- Global QA stores summaries; project QA stores detail.
- In planning mode, proposed tests may be listed only as pending QA work without execution date or result.
- Never invent executed tests, dates, coverage or SonarQube results.
- In closure mode, planned QA entries are reaffirmed or corrected using actual evidence.

---

## 7. Global `SECURITY_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/SECURITY_CONTEXT.md
```

Required structure:

```text
# SECURITY_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Security overview
## 2. Security objectives
## 3. Assets and trust boundaries
## 4. Authentication
## 5. Authorization
## 6. Roles and permissions
## 7. Tenant and brand isolation
## 8. Secrets management
## 9. Data protection
## 10. Network security
## 11. Dependency security
## 12. Secure development lifecycle
## 13. Security testing
## 14. Vulnerability management
## 15. Logging and audit
## 16. Incident response
## 17. Security risks
## 18. Accepted exceptions
## 19. Security roadmap
## 20. Related documentation
## 21. Document boundary
```

Required table:

```text
| Control ID | Domain | Control | Projects | Status | Evidence | Risk | Owner |
|---|---|---|---|---|---|---:|---|
```

Rules:

- Store security architecture, controls, protocols, risks and roadmap.
- Never store secret values.
- Update when authentication, authorization, roles, permissions, tenant isolation, controls, protocols or security tooling change.

---

## 8. Global `DATA_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/DATA_CONTEXT.md
```

Required structure:

```text
# DATA_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Data architecture overview
## 2. Data ownership
## 3. Databases and schemas
## 4. Core entities
## 5. Entity relationships
## 6. Data flows
## 7. Data contracts
## 8. Data classification
## 9. Sensitive data
## 10. Data integrity
## 11. Migration ownership
## 12. Retention and deletion
## 13. Backup and recovery
## 14. Data observability
## 15. Data risks
## 16. Pending data work
## 17. Related documentation
## 18. Document boundary
```

Required tables:

```text
| Database | Schema | Owner project | Brand | Purpose | Migration owner | Status |
|---|---|---|---|---|---|---|
```

```text
| Entity | Owner project | Schema | Brand | Description | Sensitive | Source of truth |
|---|---|---|---|---|---:|---|
```

Rules:

- PostgreSQL and Flyway own business schemas unless explicitly changed.
- Do not infer relationships or classifications without evidence.
- Update for schema, entity, ownership, migration, classification, retention or backup changes.

---

## 9. Global `DECISIONS_CONTEXT.md`

Required path:

```text
SBM-SUITE/context/DECISIONS_CONTEXT.md
```

Required structure:

```text
# DECISIONS_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Decision process
## 2. Active decisions
## 3. Proposed decisions
## 4. Superseded decisions
## 5. Rejected alternatives
## 6. Decision impact
## 7. Decision references
## 8. Document boundary
```

Required table:

```text
| ADR ID | Date | Status | Decision | Context | Alternatives | Consequences | Projects | Documentation |
|---|---|---|---|---|---|---|---|---|
```

Allowed statuses:

```text
proposed
accepted
superseded
rejected
```

Rules:

- Preserve decision history.
- Do not mark a proposal accepted without evidence.
- Link decisions to projects and documentation.

---

## 10. Global `SYS_PROMPT.md`

Required path:

```text
SBM-SUITE/context/SYS_PROMPT.md
```

Required structure:

```text
# SYS_PROMPT.md

## Parameters
## Objective
## Required inputs
## Input meaning
## Execution modes
## Development lifecycle phases
## Evidence priority
## Evidence reliability and hallucination controls
## Allowed target files
## Protected files
## Context format contract
## Mandatory generation procedure
## Input and output separation
## Patch model
## Patch filenames
## Global synchronization rules
## Project context rules
## Completed objectives rules
## Suite context rules
## Business context rules
## QA context rules
## Security context rules
## Data context rules
## Decisions context rules
## README rules
## QA evidence
## Commit nomenclature
## Executive summary
## Database rules
## Output rules
## Manifest
## Manifest construction rules
## Final validation
```

Rules:

- Require compliance with this file.
- Use section-level patches.
- Synchronize project and global project contexts.
- Synchronize project and global QA contexts.
- Update suite, business, security, data and decisions contexts when their trigger rules apply.
- Explicitly list allowed and protected paths.
- Require a deterministic generation sequence before producing any patch.
- Require `context-deploy.sh` to resolve every SYS_PROMPT template variable before delivery.
- Require complete exported source snapshots to be read before any `replace_section` operation.
- Separate input evidence from output artifacts explicitly.
- Require the output manifest to be created from the final valid ZIP contents only.
- Reject unsupported facts, inferred completion, invented QA, invented migrations and invented deployment status.
- Reject unknown, duplicated, reordered or unauthorized headings.
- Reject protected, evidence-only or input-only files from `allowed_files` and `updated_files`.
- Require a complete final validation pass before returning `context-upgrade.zip`.

---

## 11. Project `context/PROJECT_CONTEXT.md`

This section applies only to project-scoped lifecycle targets. It does not apply to `sbm-suite-context`.

Required path pattern:

```text
SBM-SUITE/<brand>/<project>/context/PROJECT_CONTEXT.md
```

Current canonical examples:

```text
SBM-SUITE/dp/DP-API/context/PROJECT_CONTEXT.md
SBM-SUITE/sbm/SBM-MANAGER/context/PROJECT_CONTEXT.md
```

Required structure:

```text
# PROJECT_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Executive summary
## 2. Project purpose
## 3. Active objectives
## 4. Pending objectives
## 5. Scope and ownership
## 6. Architecture
## 7. Runtime and containers
## 8. Configuration
## 9. Modules
## 10. Data model ownership
## 11. API surface
## 12. Authentication and authorization
## 13. Integrations
## 14. Implemented behavior
## 15. Validation evidence
## 16. Database and migration impact
## 17. Security considerations
## 18. Accepted risks and constraints
## 19. Completed work
## 20. Pending work
## 21. Required behavior
## 22. Historical decisions
## 23. Related documentation
## 24. Document boundary
```

Required table in both `## 3. Active objectives` and `## 4. Pending objectives`:

```text
| ID | Objective | Status | Priority | Target date | Branch | Documentation |
|---|---|---|---:|---|---|---|
```

Rules:

- Multiple objectives are allowed.
- `Status` must match the owning section: `active` in Active objectives and `pending` in Pending objectives.
- `Priority`: integer from `0` to `5`.
- `Target date`: optional.
- Branch is mandatory before implementation.
- Branch nomenclature follows section 2.
- Lifecycle field values must remain plain literal table-cell values; do not wrap them in Markdown formatting.
- `planning-activation` creates new objectives only; it never activates an existing pending row.
- `objective-activation` transitions exactly one existing pending objective to active, preserving ID, objective, priority, target date and branch literally and changing only status.
- For `objective-activation`, reject missing, active, completed, duplicate or inconsistent IDs and synchronize the transition in both project/global operational contexts.
- Completed or discarded objectives are removed.
- Completed objectives are appended only to the global `COMPLETED_OBJECTIVES.md`.
- Every objective change updates the global project context.

---

## 12. Project `context/QA_CONTEXT.md`

This section applies only to project-scoped lifecycle targets. It does not apply to `sbm-suite-context`.

Required path pattern:

```text
SBM-SUITE/<brand>/<project>/context/QA_CONTEXT.md
```

Current canonical examples:

```text
SBM-SUITE/dp/DP-API/context/QA_CONTEXT.md
SBM-SUITE/sbm/SBM-MANAGER/context/QA_CONTEXT.md
```

Required structure:

```text
# QA_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Project technical details
## 2. Project QA scope
## 3. Required quality gates
## 4. Test environments
## 5. Test structure
## 6. Test inventory
## 7. Test data and fixtures
## 8. Unit tests
## 9. Integration tests
## 10. API tests
## 11. Database tests
## 12. Security tests
## 13. Static analysis
## 14. Coverage
## 15. SonarQube
## 16. Current validated evidence
## 17. Known defects
## 18. Accepted exceptions
## 19. Pending QA work
## 20. Related documentation
## 21. Document boundary
```

Required technical details table:

```text
| Attribute | Value |
|---|---|
| Project | |
| Language | |
| Framework | |
| Runtime | |
| Test framework | |
| Coverage tool | |
| Static analysis tool | |
| SonarQube project key | |
| QA execution command | |
```

Required test inventory table:

```text
| Test ID | Description | Logic type | Components | Risk | Last execution | Result | Evidence |
|---|---|---|---|---:|---|---|---|
```

Allowed logic types:

```text
unit
integration
api
database
security
static-analysis
coverage
deployment
```

Rules:

- Use the risk scale from section 6.
- Every result requires evidence.
- New, removed or modified tests update project and global QA contexts.
- Preserve relevant historical evidence.

---

## 13. Project `context/DEPLOY_CONTEXT.md`

This section applies only to project-scoped lifecycle targets. It does not apply to `sbm-suite-context`.

Required path pattern:

```text
SBM-SUITE/<brand>/<project>/context/DEPLOY_CONTEXT.md
```

Current canonical examples:

```text
SBM-SUITE/dp/DP-API/context/DEPLOY_CONTEXT.md
SBM-SUITE/sbm/SBM-MANAGER/context/DEPLOY_CONTEXT.md
```

Required structure:

```text
# DEPLOY_CONTEXT.md

> Last updated
> Purpose
> Accuracy note

## 1. Scope and ownership
## 2. Required configuration
## 3. Canonical paths
## 4. Context deploy workflow
## 5. Manual review stage
## 6. Context upgrade workflow
## 7. Atomicity and cleanup
## 8. Rollback
## 9. Validation performed
## 10. Current limitations
```

Rules:

- Never expose secrets.
- Separate environment behavior.
- Do not claim deployment without evidence.

---

## 14. Project and suite `README.md`

README headings are repository-owned.

Required current global README heading sequence:

```text
# SBM Suite context
## Overview
## Purpose
## Architecture
## Requirements
## Configuration
## Installation
## Runtime
## Usage
## API or interfaces
## Development
## Validation
## Security
## Known limitations
## Related documentation
```

Required current DP-API README heading sequence:

```text
# DP-API
## Role within SBM Suite
## Project status
## Technology stack
## Current app ownership
## Architecture
## Database ownership
## Requirements
## Environment configuration
## Build and start
## Runtime operations
## Local URLs
## Main REST resources
## Usage examples
## Authentication and authorization
## Administration
## Reusable components
## QA and code quality
## SonarQube configuration
## AI integration
## Security
## Project documentation
## License
## Context lifecycle
```

Rules:

1. A README patch may target only an H1 or H2 heading that already exists exactly in the target README.
2. Preserve the complete existing H1/H2 heading sequence.
3. Do not add, remove, rename, reorder or duplicate README headings through `context-upgrade`.
4. During `planning-activation` or `objective-activation`, describe an objective only as planned or in development; during `implementation-closure`, describe stable final behavior only.
5. Exclude temporary notes, implementation transcripts and chat history.
6. Use repository-relative documentation paths.
7. Project READMEs list relevant reusable services, `.sh` scripts, models, reusable functional modules, shared utilities and public technical components.
8. Update a project README whenever one of those reusable elements is added, removed, renamed, moved or changed significantly.
9. Keep the global README general: do not inventory every internal service, model or script.
10. Update the global README only for structural, architectural or suite-level functional changes, shared behavior or global workflow changes.
11. After applying a README patch, the backend must validate that the final H1/H2 heading sequence is identical to the original target README heading sequence.

Every project README must contain this exact existing section and table header:

```text
## Reusable components

| File name | Path | Description |
|---|---|---|
```

`## Reusable components` is mandatory for project READMEs. Other README headings may differ between repositories.

---

## 15. Documentation references

Allowed path patterns:

```text
SBM-SUITE/context/documentation/pages/<page>/<page>.md
SBM-SUITE/context/documentation/pages/<page>/subpages/<subpage>.md
```

Rules:

1. Main pages are editable documentation documents.
2. Main pages maintain links to their subpages.
3. Contexts identify affected pages and subpages.
4. Context upgrades do not modify documentation.
5. Documentation changes use the separate documentation workflow.
6. Creating, deleting, renaming or structurally changing pages requires manual updates to documentation formats and prompts.
7. Git is the primary source of truth in the first stage.
8. Notion synchronization is downstream.

---

## 16. `FORMAT_CONTEXT.md`

Required structure:

```text
# FORMAT_CONTEXT.md

## 1. Global rules
## 2. Global PROJECT_CONTEXT.md
## 3. Global COMPLETED_OBJECTIVES.md
## 4. Global SUITE_CONTEXT.md
## 5. Global BUSINESS_CONTEXT.md
## 6. Global QA_CONTEXT.md
## 7. Global SECURITY_CONTEXT.md
## 8. Global DATA_CONTEXT.md
## 9. Global DECISIONS_CONTEXT.md
## 10. Global SYS_PROMPT.md
## 11. Project context/PROJECT_CONTEXT.md
## 12. Project context/QA_CONTEXT.md
## 13. Project context/DEPLOY_CONTEXT.md
## 14. Project and suite README.md
## 15. Documentation references
## 16. FORMAT_CONTEXT.md
## 17. Enforcement rules
## 18. Document boundary
```

---

## 17. Enforcement rules

Every context export and upgrade workflow must:

1. Include this file as a protected format contract.
2. Make it available to RAG retrieval.
3. Include its complete contents in the export package.
4. Never allow ChatGPT to modify it through `context-upgrade`.
5. Validate every section patch against exact target headings.
6. Reject unknown, duplicated or unauthorized headings.
7. Reject complete context or README replacements.
8. Report validation errors before replacement.
9. Keep input ZIPs untouched when validation fails.
10. Apply patches only after all validations pass.
11. Preserve backup, rollback and atomic replacement.
12. Synchronize project and global project contexts.
13. Synchronize project and global QA contexts.
14. Update suite context for API, body, structural, technology, version and integration changes.
15. Update business context for brand, franchise, business behavior and enabled-module changes.
16. Update security, data and decisions contexts when their domains change.
17. Require SHA-256 hashes for every output file except `manifest.json`.
18. Create backups before replacement.
19. Print the proposed commit message after context upgrade.
20. Keep context and documentation collections separate.
21. Preserve the manual workflow until asynchronous database flags are implemented.
22. Validate every patch operation against the exact target file and exact heading defined in this contract.
23. Reject a patch when the target section cannot be identified unambiguously.
24. Reject duplicate operations for the same target file and heading.
25. Reject output manifests copied or partially copied from the input manifest.
26. Reject `allowed_files` entries that are not permitted output paths.
27. Reject `updated_files` entries that are not physically present in the ZIP.
28. Reject ZIP files containing input evidence, protected files, complete context files or complete README files.
29. Reject mismatches among ZIP paths, `allowed_files`, `updated_files` and `content_hashes`.
30. Reject missing, incorrect or duplicate SHA-256 hashes.
31. Reject unsupported facts, invented values and claims not traceable to supplied evidence.
32. Require the LLM to omit unsafe patches instead of guessing.
33. Require all validation failures and omitted changes to be reported in `EXECUTIVE_README.md`.
34. Apply no replacement when any global validation fails.
35. Treat backend validation as mandatory even when the LLM reports successful self-validation.

36. Accept only section-level JSON patch files under `patches/`.
37. Reject complete context and README files inside `context-upgrade.zip`.
38. Require every patch filename to match exactly one authorized target file.
39. Require every patch `target_file` to match its filename mapping exactly.
40. Require `operations` to be a non-empty JSON array.
41. Allow only `replace_section` and `append_to_section`.
42. Require every context operation heading to match an exact target heading defined in this contract; require every README operation heading to match an exact existing heading in the target README.
43. Require `replace_section` content to begin with the exact target heading.
44. Reject operation content containing another same-level heading.
45. Reject duplicate operations for the same target file and heading.
46. Require required tables to preserve exact headers and column order.
47. Require `manifest.updated_files` to equal every physical ZIP file except `manifest.json`.
48. Require `manifest.content_hashes` keys to equal `manifest.updated_files`.
49. Require every physical ZIP file, including `manifest.json`, to appear in `manifest.allowed_files`.
50. Require `manifest.json` at the ZIP root and forbid it only from `manifest.updated_files` and `manifest.content_hashes`.
51. Require at least one valid context or README patch.
52. Validate all patches in memory before creating backups or modifying targets.
53. Apply all validated patches to staged copies before replacing repository files.
54. Validate the complete staged documents against this contract after patch application.
55. Create backups only after ZIP, manifest, hash, patch and staged-document validation succeeds.
56. Replace targets atomically and roll back every replacement if any operation fails.
57. Remove the input ZIP only after the complete upgrade succeeds.
58. Generate exactly one backup directory for each successful `context-upgrade` at `SBM-SUITE/context/backup/<timestamp>_<project>/`.
59. Store original files, `EXECUTIVE_README.md`, `COMMIT_MESSAGE.md` and `BACKUP_MANIFEST.json` in that backup directory.
60. Require `BACKUP_MANIFEST.json` to record `project_name`, `workflow`, `generated_at`, `motivo` and every backed-up file with its original path, backup-relative path and SHA-256 hash.
61. Reject a backup manifest when `workflow` is not `context-upgrade`, a required field is absent, a path escapes the backup directory, or a recorded hash does not match the backed-up bytes.
62. When evidence shows changes to services, `.sh` scripts, models, structure, runtime, configuration or reusable components, require the applicable lifecycle synchronization patches. Project-scoped targets require project-context and project-README plus triggered global synchronization; `sbm-suite-context` requires global project/global README synchronization and forbids project-scoped patches.
63. Require `planning-activation` to create and synchronize the complete validated new-objective batch atomically across project and global operational objectives for project-scoped targets; for `sbm-suite-context`, create the complete batch atomically in global `PROJECT_CONTEXT.md` only. Reject IDs that already exist in any lifecycle state.
64. Require `implementation-closure` to remove the objective from all applicable operational contexts and append it only to global `COMPLETED_OBJECTIVES.md`. Project-scoped targets update project and global QA; `sbm-suite-context` updates global QA only.
65. Reject any project-level `COMPLETED_OBJECTIVES.md` target.
66. Require source-manifest fields `contract_version`, `supported_patch_paths`, repository-relative `canonical_project_path`, `lifecycle_phase` and non-empty `objectives`.
67. Accept only `planning-activation`, `objective-activation`, `implementation-progress` and `implementation-closure` as `lifecycle_phase` values.
68. Never infer `lifecycle_phase` from `qa-results.md`, `git-diff.patch`, `changed-files.txt`, test status or RAG context.
69. Require `objectives` to be a non-empty array with unique valid `objective_id` values. For `planning-activation`, each item requires `objective_id`, `objective`, `status`, `priority`, `target_date` and `branch`; allow multiple new items. Treat every validated planning item as immutable and require all generated operational rows to preserve every field exactly. For `objective-activation`, require exactly one full item with desired `status=active`. For `implementation-progress` and `implementation-closure`, currently require exactly one item.
70. Do not derive `execution_mode` from `lifecycle_phase`. `planning-activation` and `objective-activation` may run in `evidence` or `user-guided` mode. Require `USER_PROMPT.md` only when `execution_mode=user-guided`, forbid it when `execution_mode=evidence`, and never synthesize `USER_PROMPT.md` from `manifest.objectives[]`. Prohibit `patches/completed-objectives.json` for both phases.
71. Dispatch lifecycle phases by exact literal equality only; forbid substring, prefix, suffix, fuzzy and fall-through matching. Require `implementation-progress` to preserve the objective's current operational status and prohibit `patches/completed-objectives.json`, `active → completed`, closure previews, closure confirmation and every other objective-closure behavior.
72. Require `implementation-closure` to include `patches/completed-objectives.json`, `patches/global-project-context.json` and `patches/global-qa-context.json` for every target. Project-scoped targets additionally require `patches/project-context.json` and `patches/project-qa-context.json`; `sbm-suite-context` forbids those project-scoped patches. Determine QA applicability structurally from repository-relative `scripts/qa-check.sh`: when present require executed canonical `passed` evidence; when absent emit canonical `not-applicable` plus deterministic evidence. Never derive `not-applicable` from missing results or user/LLM input. Require explicit closure and copy the complete tooling-generated `qa` object, including the SHA-256 of the exact QA evidence, literally through source and output manifests. Require implementation evidence only when implementation changes are claimed; allow lifecycle-only or no-op closure with an empty Git diff when the objective exists in the current operational context and no implementation claim is generated. `implementation-progress` never acquires closure QA requirements.
73. During closure, remove only `objectives[0].objective_id`, preserve every other objective and append exactly that ID to `COMPLETED_OBJECTIVES.md`.
74. Require every closure QA patch to use explicit `qa-results.md` evidence: successful execution evidence for `passed`, or deterministic structural evidence for `not-applicable`. Missing, empty, invalid or failed evidence for a project that provides `scripts/qa-check.sh` blocks closure. Preserve every unrelated project summary, test row and current QA record. Project-scoped targets require both project/global QA patches; `sbm-suite-context` requires only the global QA patch.
75. Require `replace_section` to return the complete section, preserve all unrelated rows and reject partial tables.
76. Reject any patch that removes another objective, another project from global QA or an unrelated reusable component.
77. Omit a patch when no complete target-section snapshot exists and report the omission in `EXECUTIVE_README.md`.
78. Allow `append_to_section` for `patches/completed-objectives.json` only when the canonical project heading is absent; also allow it for `## 18. Historical decisions` in global `PROJECT_CONTEXT.md` and `## 22. Historical decisions` in project `PROJECT_CONTEXT.md`.
79. Require `patches/completed-objectives.json` to contain exactly one operation targeting `## 1. Completed objectives by project`.
80. Determine the canonical project heading from the complete source snapshot outside fenced code blocks and from the Project Registry.
81. When the canonical project heading is absent during closure, require `append_to_section` with exactly one new project heading, the exact required table header and exactly one row for `objectives[0].objective_id`.
82. When the canonical project heading exists exactly once, require `replace_section` with the complete current history section, preserving every existing project heading and historical row while adding exactly one row under the existing canonical heading.
83. Never allow `append_to_section` when the canonical project heading exists; never allow `replace_section` to create a missing canonical project heading; reject multiple canonical project heading matches.
84. Forbid `append_to_section` for operational objectives, current QA, `SUITE_CONTEXT.md`, README files and all other current-state sections.
85. Reject duplicate Objective IDs, duplicate project grouping headings and modifications, reordering or removal of existing `COMPLETED_OBJECTIVES.md` history.
86. Do not copy a closed objective to `Completed work` in any `PROJECT_CONTEXT.md`.
87. Require `canonical_project_path` to equal the exact repository-relative root published for `project_name` by the backend Project Registry/source contract; never construct host/container absolute paths from `project_name`.
88. Require every project `target_file` to match the exact repository-relative mapping published for the selected project. The patch archive contract below exposes exactly one concrete project mapping set as the backend format-validation anchor; this anchor does not select the runtime project. The actual project mapping for each run comes from the source manifest/backend Project Registry. Current repository roots include `SBM-SUITE/dp/DP-API/` for `dp-api`, `SBM-SUITE/sbm/SBM-MANAGER/` for `sbm-manager`, and `SBM-SUITE/sbm/SBM-DB/` for `sbm-db`. Never derive `target_file` by string manipulation of `canonical_project_path`.
89. Generate only patch files listed in `supported_patch_paths`.
90. Require the output `contract_version` to equal the source manifest `contract_version`.
91. Reject any Markdown table containing a blank line between its header, separator or data rows.
92. Require all new rows added to an existing Markdown table to form one contiguous block immediately after the last existing data row and before any blank line, prose, heading or later section; reject detached or second row blocks, especially in `Pending objectives`, `Active objectives` and `Completed objectives` lifecycle tables.
93. Require `objective-activation` to prove the selected ID exists exactly once with current `status=pending` in every applicable complete operational context and is absent from completed history.
94. During `objective-activation`, require `objective_id`, `objective`, `priority`, `target_date` and `branch` to equal the existing pending row literally, require desired `status=active`, and reject every other transition.
95. Require `objective-activation` to replace both complete operational lifecycle sections, remove exactly one pending row, add exactly one active row, preserve all unrelated rows and continuous tables, and never create or duplicate an objective.
96. Require every manual Context and Documentation workflow to use only the canonical scripts under `SBM-SUITE/context/scripts/`.
97. Require Context deploy to validate its explicit selected `project_name` through the backend Project Registry and Context upgrade to validate the manifest-owned `project_name` through that same registry; reject manually constructed project mappings. Documentation deploy and upgrade must remain global, accept no project argument and use only their fixed suite-scoped technical target for backend compatibility.
98. Require Documentation reconciliation to obtain objective status only from canonical rows in unfenced Markdown tables under the applicable exact Documentation `Current state`, `Pending work` or `Roadmap` section and containing exact `Objective ID` and `Status` columns. Narrative text, headings, lists, examples, code blocks and generic lifecycle words are not status records.
99. Collapse repeated canonical Documentation records only when their literal statuses agree. Reject conflicting canonical statuses for one objective as an explicit source inconsistency rather than a normal synchronization difference.
100. Require a synchronized Documentation deploy to remove stale deploy artifacts, generate no package and write a current no-op response with zero differences and zero functional targets.


### Patch archive contract

Allowed global patch paths and exact target mappings:

```text
patches/global-project-context.json
→ SBM-SUITE/context/PROJECT_CONTEXT.md

patches/suite-context.json
→ SBM-SUITE/context/SUITE_CONTEXT.md

patches/business-context.json
→ SBM-SUITE/context/BUSINESS_CONTEXT.md

patches/global-qa-context.json
→ SBM-SUITE/context/QA_CONTEXT.md

patches/security-context.json
→ SBM-SUITE/context/SECURITY_CONTEXT.md

patches/data-context.json
→ SBM-SUITE/context/DATA_CONTEXT.md

patches/decisions-context.json
→ SBM-SUITE/context/DECISIONS_CONTEXT.md

patches/global-readme.json
→ SBM-SUITE/context/README.md

patches/completed-objectives.json
→ SBM-SUITE/context/COMPLETED_OBJECTIVES.md
```

Project-scoped patch filenames:

```text
patches/project-context.json
patches/project-qa-context.json
patches/project-deploy-context.json
patches/project-readme.json
```

The backend validates `FORMAT_CONTEXT.md` against exactly one concrete canonical project mapping set. This set is a format-validation anchor only; it does not select the project being processed.

Backend format-validation anchor:

```text
patches/project-context.json
→ SBM-SUITE/dp/DP-API/context/PROJECT_CONTEXT.md

patches/project-qa-context.json
→ SBM-SUITE/dp/DP-API/context/QA_CONTEXT.md

patches/project-deploy-context.json
→ SBM-SUITE/dp/DP-API/context/DEPLOY_CONTEXT.md

patches/project-readme.json
→ SBM-SUITE/dp/DP-API/README.md
```

Actual project routing is always resolved from the source manifest/backend Project Registry:

| `project_name` | Canonical repository-relative root |
|---|---|
| `dp-api` | `SBM-SUITE/dp/DP-API/` |
| `sbm-manager` | `SBM-SUITE/sbm/SBM-MANAGER/` |
| `sbm-db` | `SBM-SUITE/sbm/SBM-DB/` |

For a given run, every project-scoped patch must target only the exact repository path belonging to the literal `project_name` selected by the source manifest. The validation anchor above must never be used to override that selected-project routing.

Every patch file must use this JSON structure:

```json
{
  "target_file": "SBM-SUITE/dp/DP-API/context/PROJECT_CONTEXT.md",
  "operations": [
    {
      "operation": "replace_section",
      "heading": "## 3. Active objectives",
      "content": "## 3. Active objectives\n\nComplete Markdown for this section."
    }
  ]
}
```

### Backup contract

Every successful `context-upgrade` must create:

```text
SBM-SUITE/context/backup/<timestamp>_<project>/
├── EXECUTIVE_README.md
├── COMMIT_MESSAGE.md
├── BACKUP_MANIFEST.json
└── <original files preserved under unambiguous backup-relative paths>
```

Minimum manifest structure:

```json
{
  "project_name": "<project>",
  "workflow": "context-upgrade",
  "generated_at": "<timestamp>",
  "motivo": "<reason for the upgrade>",
  "backed_up_files": [
    {
      "original_path": "SBM-SUITE/<brand>/<project>/README.md",
      "backup_path": "previous/SBM-SUITE/<brand>/<project>/README.md",
      "sha256": "<SHA-256>"
    }
  ]
}
```

The backup must contain every original file that will be replaced. The recorded hash is calculated from the exact backed-up bytes. `original_path` and `backup_path` must be repository-relative and must not contain absolute host or container paths. `SBM-SUITE/context/backup/` is the only authorized backup root.

### Output manifest contract

The output manifest must be generated from the final ZIP contents only.

Required lifecycle and routing fields:

```json
{
  "contract_version": "<source contract_version>",
  "supported_patch_paths": [],
  "canonical_project_path": "<repository-relative project path from source manifest/project registry>",
  "lifecycle_phase": "<planning-activation|objective-activation|implementation-progress|implementation-closure>",
  "objectives": [
    {
      "objective_id": "<required objective ID>",
      "objective": "<required for planning-activation and objective-activation>",
      "status": "<active|pending for creation; active for objective-activation>",
      "priority": "<0-5; required for planning-activation and objective-activation>",
      "target_date": "<YYYY-MM-DD|N/A; required for planning-activation and objective-activation>",
      "branch": "<required for planning-activation and objective-activation>"
    }
  ]
}
```

Mandatory ZIP manifest set contract:

- `manifest.json` MUST be physically present at the ZIP root.
- `manifest.json` MUST appear in `manifest.allowed_files`.
- `manifest.json` MUST NOT appear in `manifest.updated_files`.
- `manifest.json` MUST NOT appear in `manifest.content_hashes`.
- `manifest.updated_files` MUST equal exactly the set of physical ZIP files excluding `manifest.json`.
- The keys of `manifest.content_hashes` MUST equal exactly `manifest.updated_files`.
- Every physical ZIP file MUST be authorized in `manifest.allowed_files`.

Allowed non-patch output paths:

```text
EXECUTIVE_README.md
COMMIT_MESSAGE.md
manifest.json
USER_PROMPT.md
```

Rules:

- `USER_PROMPT.md` is allowed only in `user-guided` mode.
- Every other output path must be an exact patch path listed above.
- Input evidence and protected workflow files are forbidden from all output lists.
- `updated_files` contains every physical ZIP file except `manifest.json`.
- `content_hashes` contains exactly the same paths as `updated_files`.
- Every hash is SHA-256 of the exact final UTF-8 file content.
- `allowed_files` contains every physical ZIP file, including `manifest.json`, and only authorized output paths.
- `contract_version` exactly matches the source manifest value.
- `supported_patch_paths` contains every generated patch and only paths authorized by the patch archive contract.
- `canonical_project_path` exactly matches the selected project's repository-relative root from the source manifest/backend Project Registry; every project `target_file` independently matches that project's exact canonical repository-relative mapping.
- `lifecycle_phase` and `objectives` satisfy the applicable lifecycle rules; planning batches are all-or-nothing.
- No output path may be absolute, duplicated, contain `..` or reference a symlink.
- The source manifest must never be copied as the output manifest.

---

## 18. Document boundary

This file defines context structures, objective lifecycle rules, synchronization rules, tables and validation contracts only.

It does not define actual:

- business behavior;
- architecture decisions;
- QA results;
- deployments;
- implementation completion;
- priorities;
- objective statuses;
- metrics;
- coverage;
- SonarQube results;
- documentation content.
