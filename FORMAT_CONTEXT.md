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
31. Project repositories use repository-relative paths under `SBM-SUITE/<brand>/<project>/`. Canonical project routing is defined by the backend Project Registry and must be consumed from the source manifest/contract rather than inferred from `project_name`.
32. Container project roots use canonical runtime paths under `/suite/<brand>/<project>` and must match the backend Project Registry exactly. Current required mappings include:
    - `dp-api` → `/suite/dp/DP-API` → `SBM-SUITE/dp/DP-API/`
    - `sbm-manager` → `/suite/sbm/SBM-MANAGER` → `SBM-SUITE/sbm/SBM-MANAGER/`
    - `sbm-db` → `/suite/sbm/SBM-DB` → `SBM-SUITE/sbm/SBM-DB/`
   Never change path casing or derive brand/project segments heuristically.
33. All workflow backups are stored below `SBM-SUITE/context/backup/`; no workflow may use or create a pluralized or workflow-local backup directory.

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
- `Target date`: optional, format `YYYY-MM-DD`.
- `Branch`: mandatory before development begins.
- Multiple objectives are allowed.
- Every project objective change must update this global file.
- The global file stores only high-level project summaries.
- Detailed objectives remain in the project context.
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
- A completed objective requires explicit closure and successful current QA evidence.
- Explicit implementation evidence is required only when the objective claims source-code, runtime, API, database, architecture or other implementation changes.
- A lifecycle-only or no-op objective may close with an empty Git diff when the objective exists in the current operational context, the requested lifecycle phase is `implementation-closure`, current QA passes, and no unsupported implementation claim is introduced.
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
- Completed or discarded objectives are removed.
- Completed objectives are appended only to the global `COMPLETED_OBJECTIVES.md`.
- Every objective change updates the global project context.

---

## 12. Project `context/QA_CONTEXT.md`

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
4. During `planning-activation`, describe an objective only as planned or in development; during `implementation-closure`, describe stable final behavior only.
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
62. When evidence shows changes to services, `.sh` scripts, models, structure, runtime, configuration or reusable components, require the applicable project-context and project-README patches; also apply every global synchronization rule triggered by the change.
63. Require `planning-activation` to synchronize project and global operational objectives.
64. Require `implementation-closure` to remove the objective from both operational contexts, append it only to global `COMPLETED_OBJECTIVES.md`, and update project and global QA contexts with actual validation evidence.
65. Reject any project-level `COMPLETED_OBJECTIVES.md` target.
66. Require source-manifest fields `contract_version`, `supported_patch_paths`, `canonical_project_path`, `lifecycle_phase` and `objective_id`.
67. Accept only `planning-activation`, `implementation-progress` and `implementation-closure` as `lifecycle_phase` values.
68. Never infer `lifecycle_phase` from `qa-results.md`, `git-diff.patch`, `changed-files.txt`, test status or RAG context.
69. Require a non-empty `objective_id` for every lifecycle phase.
70. Require `planning-activation` to include `USER_PROMPT.md` and prohibit `patches/completed-objectives.json`.
71. Require `implementation-progress` to prohibit `patches/completed-objectives.json` and objective closure.
72. Require `implementation-closure` to include `patches/completed-objectives.json`, `patches/global-project-context.json`, `patches/project-context.json`, `patches/global-qa-context.json` and `patches/project-qa-context.json`, plus successful current QA and explicit closure. Require implementation evidence only when implementation changes are claimed; allow lifecycle-only or no-op closure with an empty Git diff when the objective exists in the current operational context and no implementation claim is generated.
73. During closure, remove only the requested `objective_id`, preserve every other objective and append exactly that ID to `COMPLETED_OBJECTIVES.md`.
74. Require both closure QA patches to use explicit successful `qa-results.md` evidence and preserve every unrelated project summary, test row and current QA record.
75. Require `replace_section` to return the complete section, preserve all unrelated rows and reject partial tables.
76. Reject any patch that removes another objective, another project from global QA or an unrelated reusable component.
77. Omit a patch when no complete target-section snapshot exists and report the omission in `EXECUTIVE_README.md`.
78. Allow `append_to_section` for `patches/completed-objectives.json` only when the canonical project heading is absent; also allow it for `## 18. Historical decisions` in global `PROJECT_CONTEXT.md` and `## 22. Historical decisions` in project `PROJECT_CONTEXT.md`.
79. Require `patches/completed-objectives.json` to contain exactly one operation targeting `## 1. Completed objectives by project`.
80. Determine the canonical project heading from the complete source snapshot outside fenced code blocks and from the Project Registry.
81. When the canonical project heading is absent, require `append_to_section` with exactly one new project heading, the exact required table header and exactly one row for `objective_id`.
82. When the canonical project heading exists exactly once, require `replace_section` with the complete current history section, preserving every existing project heading and historical row while adding exactly one row under the existing canonical heading.
83. Never allow `append_to_section` when the canonical project heading exists; never allow `replace_section` to create a missing canonical project heading; reject multiple canonical project heading matches.
84. Forbid `append_to_section` for operational objectives, current QA, `SUITE_CONTEXT.md`, README files and all other current-state sections.
85. Reject duplicate Objective IDs, duplicate project grouping headings and modifications, reordering or removal of existing `COMPLETED_OBJECTIVES.md` history.
86. Do not copy a closed objective to `Completed work` in any `PROJECT_CONTEXT.md`.
87. Require `canonical_project_path` to equal the exact runtime root published for `project_name` by the backend Project Registry/source contract; never construct runtime or repository paths from `project_name` or alter path casing.
88. Require every project `target_file` to match the exact repository-relative mapping published for the selected project. The patch archive contract below exposes exactly one concrete project mapping set as the backend format-validation anchor; this anchor does not select the runtime project. The actual project mapping for each run comes from the source manifest/backend Project Registry. Current repository roots include `SBM-SUITE/dp/DP-API/` for `dp-api`, `SBM-SUITE/sbm/SBM-MANAGER/` for `sbm-manager`, and `SBM-SUITE/sbm/SBM-DB/` for `sbm-db`. Never derive `target_file` by string manipulation of `canonical_project_path`.
89. Generate only patch files listed in `supported_patch_paths`.
90. Require the output `contract_version` to equal the source manifest `contract_version`.


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

| `project_name` | Canonical runtime root | Canonical repository root |
|---|---|---|
| `dp-api` | `/suite/dp/DP-API` | `SBM-SUITE/dp/DP-API/` |
| `sbm-manager` | `/suite/sbm/SBM-MANAGER` | `SBM-SUITE/sbm/SBM-MANAGER/` |
| `sbm-db` | `/suite/sbm/SBM-DB` | `SBM-SUITE/sbm/SBM-DB/` |

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
  "canonical_project_path": "<exact runtime path from source manifest/project registry>",
  "lifecycle_phase": "<planning-activation|implementation-progress|implementation-closure>",
  "objective_id": "<required objective ID>"
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
- `canonical_project_path` exactly matches the selected project's runtime root from the source manifest/backend Project Registry; every project `target_file` independently matches that project's exact canonical repository-relative mapping.
- `lifecycle_phase` and `objective_id` satisfy the applicable lifecycle rules.
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
