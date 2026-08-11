# FORMAT_CONTEXT.md

> **Last updated:** 2026-08-10
>
> **Purpose:**
>
> Canonical structure contract for all SBM Suite documentation pages and subpages.
>
> Documentation generation and upgrade workflows must preserve these formats exactly.
>
> **Accuracy note:**
>
> This file defines documentation structure only. It does not define implementation status, business truth, QA evidence or deployment completion.

## 1. Global rules

1. Preserve exact heading names and order.
2. Do not rename, merge, split, reorder or remove required sections.
3. Add content only inside the matching section.
4. Preserve the metadata block at the beginning of each file.
5. Preserve Markdown tables, lists, code blocks and repository-relative paths.
6. Do not duplicate information across pages or sections.
7. Do not invent implementation, QA, architecture, deployment or business facts.
8. When evidence is insufficient, keep the existing content unchanged.
9. Structural changes require an explicit manual update to this file.
10. Documentation upgrades use complete Markdown replacements only for authorized files, and every generated replacement requires the complete current source snapshot of that exact target in the input package.
11. Documentation files must remain readable without access to chat history.
12. Documentation may include active or pending objectives only in authorized planning, roadmap or pending-work sections. Only completed and validated work may appear as implemented current state.
13. Context files remain the authoritative source for current implementation state.
14. Git is the primary documentation source of truth during the manual workflow stage.
15. Notion synchronization is downstream and must not override Git silently.
16. All dates use `YYYY-MM-DD`.
17. All documentation references use repository-relative paths.
18. Main pages are first-class documents and must maintain links to their subpages.
19. Subpages must link back to their parent page.
20. Documentation must not expose secrets, tokens, credentials or unrestricted personal data.
21. A generated documentation file must preserve its exact authorized path.
22. Documentation files may not modify context files through the documentation workflow.
23. The raw project tree may be used as evidence but must not be copied verbatim into documentation.
24. Temporary implementation notes and chat transcripts are prohibited.
25. Every file must preserve its document boundary.
26. `FORMAT_CONTEXT.md` is the only authority for documentation structure.
27. The LLM must not infer missing headings, tables, links, paths, statuses, values or output files.
28. Every generated replacement must be validated before inclusion in the output ZIP.
29. A replacement that cannot be proven valid must be omitted and reported in `EXECUTIVE_README.md`.
30. Input evidence files and protected workflow files are never authorized output files.
31. `manifest.allowed_files` and `manifest.updated_files` must be derived only from valid files actually permitted in the output ZIP.
32. The source manifest must never be copied as the output manifest.
33. Output paths must be exact, repository-relative, unique and free of `..`, absolute paths and symlinks.
34. Every output file except `manifest.json` requires a SHA-256 hash matching its final ZIP content.
35. Any global validation failure must prevent documentation replacement.

36. Metadata labels are exact literals and must preserve punctuation.
37. Every documentation file requires `> **Last updated:**`, `> **Purpose:**` and `> **Source of truth:**`.
38. Every subpage additionally requires `> **Parent page:**`.
39. Variants without the final colon are invalid.
40. Metadata labels must appear exactly once and in the order defined for the page type.
41. Documentation files live only below `SBM-SUITE/context/documentation/pages/`.
42. Workflow backups use the suite-wide `SBM-SUITE/context/backup/` root; documentation-local and alternate backup roots are forbidden.
43. Global Context is the canonical source for the current objective lifecycle state across every registered project. Documentation may lag behind Context temporarily, and a Context objective missing from Documentation does not invalidate Context.
44. Every `documentation-deploy` must reconcile authorized Documentation candidates against the complete current global Context objective state, including active, pending and completed objectives from all projects, regardless of which project originated the current execution.
45. Context-to-Documentation reconciliation must be safe and idempotent: preserve all unrelated documentation, update only evidenced lifecycle differences and produce no replacement for a page that is already synchronized.
46. Lifecycle values copied into Documentation must remain literal and must not be wrapped in Markdown formatting.
47. Every Markdown table must remain one continuous block with no blank line between its header, separator or data rows. All new rows must form one contiguous block immediately after the last existing row and before any blank line, prose, heading or later section; detached or second row blocks are forbidden.
48. Manual Context and Documentation orchestration remains synchronous under `SBM-SUITE/context`; do not introduce flags, queues or asynchronous processing.
49. Build `manifest.updated_files` only after every final non-manifest output file has been selected and assigned its exact repository-relative ZIP path.
50. For `documentation-upgrade.zip`, require `set(manifest.updated_files) == set(all physical ZIP files except manifest.json)`; subset or superset relationships are invalid.
51. `COMMIT_MESSAGE.md`, `EXECUTIVE_README.md`, optional `USER_PROMPT.md` and every Documentation page are ordinary non-manifest ZIP files for this equality and must never be omitted from `updated_files` when included.
52. Reject duplicate, normalized, flattened, case-altered or otherwise inconsistent ZIP and manifest paths.
53. Functional Documentation candidates are complete existing files below `SBM-SUITE/context/documentation/pages/`; `FORMAT_CONTEXT.md` and `SYS_PROMPT.md` are protected contracts and never satisfy the candidate requirement.
54. When Context-to-Documentation differences exist, `documentation-deploy` must select at least one real functional candidate and package its complete source snapshot.
55. Every real `documentation-upgrade.zip` must contain at least one generated file below `documentation/pages/`; root metadata files and protected workflow contracts are invalid substitutes.
56. When no Context-to-Documentation difference exists, report `Documentation already synchronized` and do not generate or instruct a metadata-only upgrade.


---

## 2. Documentation root structure

Required root:

```text
SBM-SUITE/context/documentation/
```

Required workflow files:

```text
SBM-SUITE/context/documentation/FORMAT_CONTEXT.md
SBM-SUITE/context/documentation/SYS_PROMPT.md
```

Documentation-deploy package requirements:

1. Read `SBM-SUITE/context/documentation/SYS_PROMPT.md`.
2. Replace every `{{PROJECT_NAME}}` token with the validated project name.
3. Fail when any unresolved template token remains.
4. Include the complete rendered file in `documentation-package.zip` as `SYS_PROMPT.md`.
5. Include this complete protected contract in `documentation-package.zip` as `FORMAT_CONTEXT.md`.
6. Use Qdrant/RAG chunks only to select relevant documentation candidates; retrieved chunks are not complete source documents.
7. For every RAG-selected documentation candidate, include the complete current UTF-8 Markdown source snapshot at its exact `documentation/...` archive path.
8. Fail export when a RAG-selected candidate cannot be mapped to one complete authorized source snapshot.
9. `documentation-files.txt` must list exactly the complete candidate snapshots included in the package.
10. Record each candidate snapshot in `manifest.documentation_files` with `archive_path`, `complete=true`, `selected_by_rag=true` and its SHA-256 `content_hash`.
11. Set `manifest.snapshot_policy` to `rag-selected-complete`.
12. Record both workflow contract files in the source package manifest.
13. Do not require a separate user upload of either workflow file.
14. Treat workflow contracts and packaged source snapshots as input evidence for `documentation-upgrade`; source snapshots are never copied unchanged into the output ZIP.
15. Include the complete current global active, pending and completed objective state from Context as reconciliation evidence, independent of the selected origin project.
16. Select complete source snapshots for every existing authorized roadmap or pending-work candidate needed to reconcile accumulated objective differences across projects.

Required workflow directories:

```text
SBM-SUITE/context/documentation/input/
SBM-SUITE/context/documentation/output/
```

Shared backup root:

```text
SBM-SUITE/context/backup/
```

Documentation page pattern:

```text
SBM-SUITE/context/documentation/pages/<page>/<page>.md
```

Documentation subpage pattern:

```text
SBM-SUITE/context/documentation/pages/<page>/subpages/<subpage>.md
```

Example:

```text
SBM-SUITE/context/documentation/pages/qa-and-testing/qa-and-testing.md
SBM-SUITE/context/documentation/pages/qa-and-testing/subpages/dp-api.md
```

Rules:

- `<page>` and `<subpage>` use lowercase kebab-case.
- Folder and Markdown filename must match.
- Main pages use the same slug as their folder.
- Subpages live only under `subpages/`.
- New pages, new subpages, renames and deletions require manual authorization.
- The documentation workflow may modify only existing authorized files.

---

## 3. Main documentation page

Required structure:

```text
# <Page title>

> **Last updated:** YYYY-MM-DD
>
> **Purpose:**
>
> <Purpose statement>
>
> **Source of truth:**
>
> <Authoritative contexts, repositories or systems>

## 1. Overview
## 2. Scope
## 3. Current state
## 4. Core concepts
## 5. Architecture or operating model
## 6. Components
## 7. Workflows
## 8. Configuration
## 9. Security
## 10. Validation
## 11. Known limitations
## 12. Roadmap
## 13. Related pages
## 14. Subpages
## 15. Document boundary
```

### Section rules

- `Overview`: concise description of the documentation domain.
- `Scope`: what this page covers and excludes.
- `Current state`: validated current state only.
- `Core concepts`: terms and principles required to understand the domain.
- `Architecture or operating model`: structure, responsibilities and boundaries.
- `Components`: projects, services, modules or tools.
- `Workflows`: ordered operational or development flows.
- `Configuration`: configuration names and behavior without secret values.
- `Security`: relevant controls and restrictions.
- `Validation`: QA, checks or evidence required.
- `Known limitations`: current confirmed restrictions and gaps.
- `Roadmap`: may include active or pending objectives as planning only; never represent them as implemented or completed.
- `Related pages`: repository-relative links to related main pages.
- `Subpages`: complete list of authorized subpages.
- `Document boundary`: information intentionally excluded.

### Required related-pages table

`## 13. Related pages` must contain:

```text
| Page | Path | Relationship |
|---|---|---|
```

### Required subpages table

`## 14. Subpages` must contain:

```text
| Subpage | Path | Description | Status |
|---|---|---|---|
```

Allowed status values:

```text
active
planned
deprecated
```

Rules:

- Every existing subpage must be listed.
- Do not list a subpage that does not exist unless its status is `planned` and creation has been explicitly approved.
- Paths must be repository-relative.
- Main pages must remain useful even when subpages are not opened.

---

## 4. Documentation subpage

Required structure:

```text
# <Subpage title>

> **Last updated:** YYYY-MM-DD
>
> **Parent page:**
>
> `<repository-relative parent path>`
>
> **Purpose:**
>
> <Purpose statement>
>
> **Source of truth:**
>
> <Authoritative contexts, repositories or systems>

## 1. Overview
## 2. Scope
## 3. Current state
## 4. Detailed design or procedure
## 5. Inputs and prerequisites
## 6. Execution or usage
## 7. Outputs and evidence
## 8. Security considerations
## 9. Validation
## 10. Known limitations
## 11. Pending work
## 12. Related documentation
## 13. Parent page
## 14. Document boundary
```

### Section rules

- `Overview`: concise subtopic summary.
- `Scope`: exact boundaries of the subpage.
- `Current state`: verified implementation or operating status.
- `Detailed design or procedure`: complete domain-specific content.
- `Inputs and prerequisites`: requirements before execution.
- `Execution or usage`: commands, APIs or steps when applicable.
- `Outputs and evidence`: generated artifacts, results and evidence.
- `Security considerations`: access, secrets and risk constraints.
- `Validation`: required checks and acceptance criteria.
- `Known limitations`: current confirmed limitations.
- `Pending work`: may include active or pending objectives as planning only; never represent them as implemented or completed.
- `Related documentation`: links to sibling or external project documentation.
- `Parent page`: mandatory link back to the main page.
- `Document boundary`: information intentionally excluded.

### Required related-documentation table

`## 12. Related documentation` must contain:

```text
| Document | Path | Relationship |
|---|---|---|
```

### Required parent-page link

`## 13. Parent page` must contain exactly one primary parent path:

```text
[Return to <Parent page title>](../<parent-page>.md)
```

Adjust the relative path only when required by the actual folder structure.

---

## 5. Roadmap documentation

Documentation may be updated during objective planning/activation and after objective closure. Planning updates must remain strictly separated from implemented current state.

A roadmap main page or subpage must use the applicable main-page or subpage format.

Rules:

- newly created `active` or `pending` objectives may be added only to authorized roadmap, planning or pending sections;
- preserve their evidenced status exactly as `active` or `pending`;
- preserve existing roadmap sections and tables required by the page format;
- completed objectives may be reflected as delivered capabilities, milestones or historical outcomes only when closure evidence exists;
- `SBM-SUITE/context/COMPLETED_OBJECTIVES.md` is historical closure evidence only and is never a documentation target;
- branch names and objective IDs must match finalized contexts and closure evidence;
- documentation paths remain repository-relative;
- discarded or cancelled work must include explicit evidence and reason before documentation is changed.

When a roadmap table is already part of an authorized page, preserve its existing exact column structure unless this format contract explicitly defines it.


---

## 6. Architecture documentation

Architecture pages must include, inside their applicable sections:

### Required component table

```text
| Component | Project | Responsibility | Technology | Runtime | Owner | Status |
|---|---|---|---|---|---|---|
```

### Required integration table

```text
| Source | Target | Contract | Data | Authentication | Purpose | Status |
|---|---|---|---|---|---|---|
```

### Required decision table

```text
| ADR ID | Decision | Status | Consequences | Projects | Reference |
|---|---|---|---|---|---|
```

Rules:

- Do not duplicate full project contexts.
- Only validated architecture belongs in `Current state`.
- Proposed architecture belongs in `Roadmap` or a clearly marked proposed subsection.
- Architecture diagrams must use Mermaid or text unless an approved image is maintained in Git.

---

## 7. API documentation

API documentation pages must include:

### Required API table

```text
| API | Owner project | Base path | Audience | Authentication | Status |
|---|---|---|---|---|---|
```

### Required endpoint table

```text
| Method | Path | Request | Response | Authentication | Authorization | Purpose | Status |
|---|---|---|---|---|---|---|---|
```

### Endpoint detail format

```text
### <Endpoint title>

**Method**

```text
POST
```

**Path**

```text
/api/resource/
```

**Purpose**

<Description>

**Authentication**

<Requirement>

**Authorization**

<Requirement>

**Request**

```json
{}
```

**Response**

```json
{}
```

**Errors**

| Status | Meaning |
|---:|---|
```

Rules:

- Never invent request or response fields.
- Use exact verified method and path.
- State `N/A` when a contract is unknown.
- Mark planned endpoints clearly.
- Internal endpoints must not be documented as client-facing.

---

## 8. QA and testing documentation

QA documentation pages must include:

### Required project QA table

```text
| Project | Test count | Passed | Failed | Coverage | SonarQube | Last execution | Status | Evidence |
|---|---:|---:|---:|---|---|---|---|---|
```

### Required test inventory table

```text
| Test ID | Project | Description | Logic type | Components | Risk | Last execution | Result | Evidence |
|---|---|---|---|---|---:|---|---|---|
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

- Never invent tests, counts, coverage or SonarQube results.
- Planned tests may be referenced only in planning or pending-work sections during planning activation. Executed test results belong in QA/current-state sections only when explicit QA evidence exists.
- Raw reports remain outside documentation.
- Documentation summarizes evidence from QA contexts.

---

## 9. Security documentation

Security pages must include:

### Required control table

```text
| Control ID | Domain | Control | Projects | Status | Evidence | Risk | Owner |
|---|---|---|---|---|---|---:|---|
```

### Required risk table

```text
| Risk ID | Description | Projects | Status | Risk | Mitigation | Owner |
|---|---|---|---|---:|---|---|
```

Rules:

- Never include secrets.
- Security evidence must come from contexts, scans or validated reports.
- Unknown controls remain `N/A` or `pending`.
- Accepted exceptions must include owner and reason.

---

## 10. Data documentation

Data pages must include:

### Required schema table

```text
| Database | Schema | Owner project | Brand | Purpose | Migration owner | Status |
|---|---|---|---|---|---|---|
```

### Required entity table

```text
| Entity | Owner project | Schema | Brand | Description | Sensitive | Source of truth |
|---|---|---|---|---|---:|---|
```

### Required data-flow table

```text
| Source | Destination | Data | Contract | Owner | Security | Status |
|---|---|---|---|---|---|---|
```

Rules:

- PostgreSQL and Flyway remain authoritative for business schemas.
- Do not infer relationships from filenames.
- Sensitive classifications require evidence.
- Retention, deletion, backup and recovery must be explicit when known.

---

## 11. DevOps and deployment documentation

Deployment pages must include:

### Required environment table

```text
| Environment | Purpose | Runtime | Configuration source | Deployment method | Status |
|---|---|---|---|---|---|
```

### Required service table

```text
| Service | Project | Container | Internal port | Host port | Network | Health check | Status |
|---|---|---|---:|---:|---|---|---|
```

### Required deployment flow

```text
build
→ validate
→ deploy
→ health check
→ smoke test
→ monitor
→ rollback when required
```

Rules:

- Never expose secret values.
- Do not claim a deployment occurred without evidence.
- Separate local, development, staging and production.
- Rollback requirements must be explicit.

---

## 12. AI engineering documentation

AI pages must include:

### Required model and provider table

```text
| Provider | Model | Purpose | Interface | Status | Constraints |
|---|---|---|---|---|---|
```

### Required collection table

```text
| Collection | Source | Content | Embedding model | Dimensions | Filters | Status |
|---|---|---|---|---:|---|---|
```

### Required Tool table

```text
| Tool | Owner API | Method | Path | Authentication | Approval | Status |
|---|---|---|---|---|---|---|
```

Rules:

- AI uses APIs and explicit Tools.
- AI must not write directly to PostgreSQL.
- Separate `sbm_docs`, `sbm_contexts` and `sbm_documentation`.
- Never expose raw vectors or secrets.
- Planned Tools may be documented only in planning or roadmap sections and must never be represented as implemented.

---

## 13. Context and documentation workflow pages

Workflow documentation must include:

### Required workflow table

```text
| Step | Component | Input | Action | Output | Validation |
|---:|---|---|---|---|---|
```

### Required artifact table

```text
| Artifact | Workflow | Producer | Consumer | Path | Required | Description |
|---|---|---|---|---|---:|---|
```

### Required collection mapping

```text
| Workflow | Qdrant collection | Source of truth | Generated package | Upgrade output |
|---|---|---|---|---|
```

Current mapping:

```text
Context workflow
→ sbm_contexts

Documentation workflow
→ sbm_documentation

Confluence assistant knowledge
→ sbm_docs
```

Rules:

- Keep context and documentation workflows separate.
- Context upgrades may not modify documentation.
- Documentation upgrades may not modify contexts.
- Documentation deployment and upgrade may occur after planning activation/context upgrade for planning-only updates, and after implementation closure/final context upgrade for implemented-state updates.
- Both workflows require manifest, hashes, backup and validation.
- `project-tree.txt` is context evidence only unless explicitly required by documentation generation.

---

## 14. Commands and code blocks

Command rules:

- Use fenced code blocks.
- Use the correct language identifier where practical.
- Commands must be executable from the documented working directory.
- State the working directory when ambiguous.
- Do not include secret values.
- Use placeholders for credentials.
- Do not claim a command was validated unless evidence exists.

Example:

```bash
./scripts/documentation-deploy.sh
```

API paths and methods must remain separate when documenting an endpoint.

---

## 15. Links and references

Use repository-relative Markdown links.

Main page to subpage:

```markdown
[DP-API QA](subpages/dp-api.md)
```

Subpage to parent:

```markdown
[Return to QA and Testing](../qa-and-testing.md)
```

Cross-page link:

```markdown
[Security and DevSecOps](../security-and-devsecops/security-and-devsecops.md)
```

Rules:

- Do not use absolute local filesystem paths.
- Do not use broken or speculative paths.
- Update parent and related-page tables when links change.
- Renaming a page requires manual format and prompt updates before execution.

---

## 16. Documentation upgrade authorization

The documentation workflow may modify only files explicitly listed as complete RAG-selected source snapshots in the input manifest and `documentation-files.txt`. RAG chunks alone never authorize a replacement.

Required validation:

1. path is repository-relative;
2. path remains under `SBM-SUITE/context/documentation/pages/`;
3. extension is `.md`;
4. file already exists unless creation is explicitly authorized;
5. no absolute path;
6. no `..`;
7. no symlink;
8. SHA-256 hash matches;
9. required headings are present and ordered;
10. parent and subpage links remain valid;
11. no protected workflow file is modified;
12. all files pass before replacement;
13. backup exists before replacement;
14. replacement is atomic or fully rolled back.
15. when documenting implemented current state, the related objective has implementation and successful QA closure evidence;
16. active or pending objectives may be documented only in authorized planning, roadmap or pending-work sections;
17. planning intent must never be represented as implemented current state.

18. required metadata labels exist exactly once;
19. metadata labels preserve the required final colon;
20. metadata labels remain in the required order for the page type;
21. the input package contains the complete current source snapshot for the exact target path and its hash matches `manifest.documentation_files`;
22. the replacement is derived from that complete snapshot plus supported change evidence, never reconstructed from RAG chunks.


Protected files:

```text
SBM-SUITE/context/documentation/FORMAT_CONTEXT.md
SBM-SUITE/context/documentation/SYS_PROMPT.md
```

These files require manual modification.

---

## 17. `FORMAT_CONTEXT.md`

Required structure:

```text
# FORMAT_CONTEXT.md

## 1. Global rules
## 2. Documentation root structure
## 3. Main documentation page
## 4. Documentation subpage
## 5. Roadmap documentation
## 6. Architecture documentation
## 7. API documentation
## 8. QA and testing documentation
## 9. Security documentation
## 10. Data documentation
## 11. DevOps and deployment documentation
## 12. AI engineering documentation
## 13. Context and documentation workflow pages
## 14. Commands and code blocks
## 15. Links and references
## 16. Documentation upgrade authorization
## 17. FORMAT_CONTEXT.md
## 18. Enforcement rules
## 19. Document boundary
```

---

## 18. Enforcement rules

Every documentation export and upgrade workflow must:

1. Include this file as the protected documentation format contract.
2. Make it available to documentation RAG retrieval.
3. Include its complete contents in the export package.
4. Never allow ChatGPT to modify it through `documentation-upgrade`.
5. Validate complete generated Markdown files against their required structure.
6. Reject missing, renamed, duplicated or reordered headings.
7. Reject unauthorized top-level sections.
8. Validate parent and subpage relationships.
9. Validate authorized paths and extensions.
10. Reject absolute paths, `..` and symlinks.
11. Validate SHA-256 hashes.
12. Report all errors before replacement.
13. Keep the input ZIP untouched when validation fails.
14. Create timestamped backups before replacement.
15. Replace files only after all files pass.
16. Preserve rollback behavior.
17. Return a proposed commit message.
18. Distinguish documentation and context backup records by their manifest `workflow` value while storing both below `SBM-SUITE/context/backup/`.
19. Keep `sbm_documentation` separate from `sbm_contexts` and `sbm_docs`.
20. Preserve the manual workflow until asynchronous orchestration is implemented.
21. Never create, delete, rename or move a documentation page without explicit manual authorization.
22. Never modify context files.
23. Never include secret values.
24. Preserve Git as the primary source of truth.
25. Validate every generated file against the exact page type and all applicable domain-specific rules.
26. Reject missing, renamed, duplicated, reordered or unauthorized headings.
27. Reject missing or reordered required table columns.
28. Reject incomplete Markdown replacements, fragments, patches and summaries.
29. Reject output manifests copied or partially copied from the input manifest.
30. Reject `allowed_files` entries that are not permitted output paths.
31. Require `updated_files` to contain all and only the physical ZIP files except `manifest.json`; reject both undeclared physical files and declared paths absent from the ZIP.
32. Reject ZIP files containing input evidence, protected files, context files or workflow contracts.
33. Reject mismatches among ZIP paths, `allowed_files`, `updated_files` and `content_hashes`.
34. Reject missing, incorrect or duplicate SHA-256 hashes.
35. Reject unsupported facts, invented values and claims not traceable to supplied evidence.
36. Require the LLM to omit unsafe replacements instead of guessing.
37. Require every omitted or failed replacement to be reported in `EXECUTIVE_README.md`.
38. Apply no replacement when any global ZIP, manifest, authorization, path or hash validation fails.
39. Treat backend validation as mandatory even when the LLM reports successful self-validation.
40. Preserve unchanged content whenever supplied evidence does not justify modification.
41. Preserve planning, current, completed and deprecated states distinctly; active or pending objective content is allowed only in authorized planning, roadmap or pending-work sections.
42. Validate parent-page and subpage relationships before replacement.
43. Validate every documentation path against the authorized source file list.

44. Reject missing, duplicated, renamed or reordered metadata labels.
45. Reject `Purpose`, `Source of truth`, `Parent page` or `Last updated` labels without the required final colon.
46. Validate metadata before creating backups or replacing files.
47. Require `documentation-deploy` to include rendered `SYS_PROMPT.md` and complete `FORMAT_CONTEXT.md`.
48. Require all `{{PROJECT_NAME}}` tokens to be resolved before packaging.
49. Reject a documentation package containing unresolved template tokens.
50. Record `SYS_PROMPT.md` and `FORMAT_CONTEXT.md` in the source package manifest.
51. Treat workflow contracts as input-only files that cannot appear in `documentation-upgrade.zip`.
52. Never create or use a backup directory below `SBM-SUITE/context/documentation/`.
53. Allow documentation generation for an `active` or `pending` objective only when every generated change is confined to authorized planning, roadmap or pending-work sections.
54. Require implementation evidence, successful QA evidence and completed objective closure before documenting the current change as implemented current state.
55. Treat `SBM-SUITE/context/COMPLETED_OBJECTIVES.md` only as historical closure evidence and never as an output target.
56. Require RAG to select documentation candidates only; never treat retrieved chunks as complete source files.
57. Require `documentation-deploy` to package the complete current snapshot of every RAG-selected candidate under its exact `documentation/...` path.
58. Require `manifest.snapshot_policy` to equal `rag-selected-complete`.
59. Require every `manifest.documentation_files` entry to declare `complete=true`, `selected_by_rag=true` and a SHA-256 `content_hash` matching the packaged snapshot.
60. Fail export when any RAG-selected candidate lacks a complete authorized source snapshot.
61. Require every generated documentation replacement to have a corresponding complete source snapshot in the input package; never reconstruct missing sections, tables, metadata or links from RAG chunks.
62. A lifecycle-only/no-op closure may update QA, validation, roadmap or workflow documentation when supported by closure evidence, but must not introduce implementation-state claims without implementation evidence.
63. Treat global Context as authoritative for objective lifecycle state and permit Documentation to be temporarily behind it; never reject a valid Context objective merely because Documentation does not yet contain it.
64. Require every documentation deployment to reconcile active, pending and completed objectives from the complete current global Context, not only objectives owned by the project that originated the workflow.
65. Require reconciliation to preserve unrelated documentation and omit already synchronized files from the upgrade ZIP.
66. Reject formatted or altered lifecycle values copied from Context.
67. Reject any Markdown table split by a blank line or any new table rows that do not form one contiguous block immediately after the last existing row.
68. Preserve synchronous manual orchestration and forbid new flags, queues or asynchronous processing.
69. Construct `updated_files` from the frozen final non-manifest ZIP member list, never from a candidate, partial, source-manifest or pre-validation list.
70. Require `COMMIT_MESSAGE.md` and `EXECUTIVE_README.md` in `updated_files` for every valid Documentation upgrade and require `USER_PROMPT.md` there whenever it is physically included.
71. Require every generated `documentation/...` replacement physically included in the ZIP to appear exactly once in `updated_files` with the identical archive path.
72. Reject a Documentation upgrade locally and in the backend whenever the `updated_files` set differs from the physical non-manifest ZIP member set.
73. Detect objective lifecycle differences globally, including missing objectives, `pending → active`, `active → completed` and accumulated differences across multiple projects.
74. Require global candidate selection to remain independent from the internal technical `project_name` used for backend compatibility.
75. Require at least one functional `documentation/pages/...` candidate whenever reconciliation differences exist; protected workflow contracts do not count.
76. Require at least one generated `documentation/pages/...` replacement in every real Documentation upgrade.
77. Reject metadata-only upgrades even when their manifest, hashes and root metadata are otherwise structurally valid.
78. Treat a fully synchronized state as a successful no-op: emit `Documentation already synchronized`, produce no deploy package and do not instruct an upgrade.


---

## 19. Document boundary

This file defines documentation structure, lifecycle gates, tables, links, paths, validation and workflow authorization only.

It does not define:

- actual documentation content;
- implementation completion;
- business truth;
- architecture approval;
- QA execution results;
- security validation results;
- database state;
- deployment completion;
- real roadmap priority;
- Notion synchronization status.
