# QA_CONTEXT.md

> **Last updated:** 2026-08-07
>
> **Purpose**
>
> Transversal QA context for **SBM Suite**. It summarizes quality policy, project QA status, test inventory, coverage, SonarQube, security validation, API validation, database validation, release criteria and accepted risks.
>
> **Accuracy note**
>
> Only explicitly executed and evidenced results may be recorded as validated. Planned QA may be recorded before development only as pending work without execution date or result. Unknown counts, coverage, SonarQube results and dates remain `N/A`.

## 1. Suite QA overview

Global QA applies to:

- frontend-to-API validation;
- API-to-database integration;
- cross-API workflows;
- AI Tool-to-API validation;
- authentication and authorization;
- tenant and brand isolation;
- shared Docker services;
- transversal smoke tests;
- multi-repository regression;
- release acceptance involving more than one project.

Project-specific test plans, fixtures, commands and detailed evidence remain in each project's `context/QA_CONTEXT.md`.

## 2. Quality policy

1. Validate behavior through public contracts.
2. Test the canonical owner.
4. Preserve project and business ownership boundaries.
5. Use real integration boundaries when practical.
6. Keep test data isolated and deterministic.
7. Never mutate production or shared persistent data during QA.
8. Never execute unauthorized migrations from application repositories.
9. Validate success and failure paths.
10. Validate permissions and tenant isolation.
11. Record exact commands, evidence and results.
12. Do not treat passing unit tests as proof of transversal compatibility.
13. Keep project and global QA contexts synchronized.
14. Do not hide code from coverage to improve metrics.
15. Do not mark planned work as executed.
15. Planned QA may be added during objective activation only with `Last execution = N/A`, `Result = pending` and explicit planned evidence.
16. Closing QA updates must replace or reaffirm planned entries using actual execution evidence.
17. Work one validated step at a time.
18. Closure QA uses the canonical semantic states `passed`, `failed` and `not-applicable`; legacy `success` evidence is normalized to `passed`.
19. Derive `not-applicable` only when the selected repository root has no repository-relative `scripts/qa-check.sh`. It is not equivalent to missing, unknown, not-run or failed evidence.
20. If `scripts/qa-check.sh` exists, missing, empty, invalid or failed `qa-results.md` blocks closure and can never be overridden by user or generated manifest text.

## 3. Quality gates

| Gate | Scope | Required evidence | Blocking |
|---|---|---|---:|
| Test execution | Project and transversal | Command, passed, failed, skipped and timestamp | 1 |
| Coverage | Project | Coverage report and threshold result | 1 |
| Static analysis | Project | Tool output and issue count | 1 |
| SonarQube | Project | Quality Gate status and project key | 1 |
| API contract | Affected API | Request, response, status and error validation | 1 |
| Database compatibility | Database-sensitive changes | Schema, Flyway, DBML and model comparison | 1 |
| Security | Protected flows | Authentication, authorization and isolation validation | 1 |
| Integration | Cross-project flow | Consumer-to-provider evidence | 1 |
| Failure paths | Changed behavior | Negative scenarios and rollback behavior | 1 |
| Documentation | Context and documentation lifecycle | Updated authorized artifacts | 1 |

A gate may be bypassed only through a documented accepted exception.

## 4. Project QA summaries

| Project | QA context | Test count | Passed | Failed | Coverage | SonarQube status | Last execution | Overall risk | Evidence |
|---|---|---:|---:|---:|---|---|---|---:|---|
| DP-API | `SBM-SUITE/dp/DP-API/context/QA_CONTEXT.md` | 65 | 65 | 0 | 88% | Quality Gate OK | 2026-08-07 | 3 | `qa-results.md`: 65 tests passed; coverage 88%; SonarScanner exit code 0; Quality Gate OK |
| SBM-API | `SBM-SUITE/sbm/SBM-API/context/QA_CONTEXT.md` | N/A | N/A | N/A | N/A | N/A | N/A | 3 | Project QA context pending |
| SBM-MANAGER | `SBM-SUITE/sbm/SBM-MANAGER/context/QA_CONTEXT.md` | 45 | 45 | 0 | 70.14% | Quality Gate PASSED | 2026-08-14 | 3 | `qa-results.md`: 45 tests passed; coverage 70.14%; SonarScanner exit code 0; server-side Quality Gate PASSED |
| SBM-DB | `SBM-SUITE/sbm/SBM-DB/context/QA_CONTEXT.md` | N/A | N/A | N/A | N/A | Quality Gate PASSED | 2026-08-08 | 4 | `qa-results.md`: Flyway validated 33 sbm_business, 55 ditaly_pasta, 5 cross and 2 analytics migrations; SonarScanner exit code 0; Quality Gate PASSED |
| SBM-AI-ASSISTANT | `SBM-SUITE/sbm/sbm-ai-assistant/context/QA_CONTEXT.md` | N/A | N/A | N/A | N/A | N/A | N/A | 3 | Project QA context pending |
| SBM-SUITE | `SBM-SUITE/context/QA_CONTEXT.md` | N/A | N/A | N/A | N/A | not-applicable | 2026-08-13 | 0 | `qa-results.md`: QA structurally not applicable because `scripts/qa-check.sh` does not exist for `sbm-suite-context` |

Risk scale:

```text
0 = none
1 = very low
2 = low
3 = medium
4 = high
5 = critical
```

## 5. Test inventory

| Test ID | Project | Description | Logic type | Components | Risk | Last execution | Result | Evidence |
|---|---|---|---|---|---:|---|---|---|
| QA-CONTEXT-001 | SBM Suite | Validate project QA context synchronization with global QA context | integration | context-deploy, context-upgrade, QA contexts | 4 | N/A | pending | No execution evidence |
| QA-CONTEXT-002 | SBM Suite | Validate project context synchronization with global project context | integration | project contexts, context-upgrade | 4 | N/A | pending | No execution evidence |
| QA-CONTEXT-003 | SBM Suite | Validate section patch structure and authorized paths | security | manifest, ZIP, patch validator | 5 | N/A | pending | No execution evidence |
| QA-CONTEXT-004 | SBM Suite | Validate context backup and atomic rollback | integration | context-upgrade, filesystem | 5 | N/A | pending | No execution evidence |
| QA-DOC-001 | SBM Suite | Validate documentation package authorized Markdown paths | security | documentation-upgrade, manifest | 5 | N/A | pending | Workflow not implemented |
| QA-DOC-002 | SBM Suite | Validate documentation backup and replacement | integration | documentation-upgrade, filesystem | 4 | N/A | pending | Workflow not implemented |
| QA-API-001 | SBM Suite | Validate frontend-to-canonical API routing | api | SBM-MANAGER, DP-API, SBM-API | 4 | N/A | pending | No transversal evidence |
| QA-AI-001 | SBM Suite | Validate AI Tool uses canonical API without direct database access | security | SBM-AI-ASSISTANT, Tools, APIs | 5 | N/A | pending | Tool integration pending |
| QA-TENANT-001 | SBM Suite | Deny cross-tenant read and write operations | security | authentication, authorization, APIs | 5 | N/A | pending | No transversal evidence |
| QA-DB-001 | SBM Suite | Validate application models against PostgreSQL, Flyway and DBML | database | DP-API, SBM-API, SBM-DB | 5 | N/A | pending | No transversal evidence |

Planning and closure rules:

- During the first context upgrade for an objective, proposed tests may be added as `pending` with no execution date.
- Proposed tests must be directly tied to the active or pending objective.
- During the closing context upgrade, planned tests must be reaffirmed, corrected or removed using actual `qa-results.md` evidence.
- Executed tests require command, date, result and evidence.
- A completed objective must not retain unresolved mandatory QA entries unless an accepted exception is recorded.

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

## 6. Coverage summary

| Project | Tool | Coverage | Threshold | Status | Last execution | Evidence |
|---|---|---|---|---|---|---|
| DP-API | pytest-cov | 88% | N/A | recorded | 2026-08-02 | `qa-results.md`; `coverage.xml` generated; exit code 0 |
| SBM-API | N/A | N/A | N/A | not validated | N/A | No coverage evidence supplied |
| SBM-MANAGER | Vitest / V8 | N/A | lines/statements/functions 70%; branches 60% | not validated | N/A | Project QA configuration present; fresh `qa-results.md` pending |
| SBM-DB | N/A | N/A | N/A | N/A | N/A | Coverage is not applicable to the database/migration repository |
| SBM-AI-ASSISTANT | N/A | N/A | N/A | not validated | N/A | No coverage evidence supplied |

Coverage rules:

- `qa-check.sh` generates coverage evidence after implementation.
- Planning upgrades may define required coverage checks, but must not record percentages or pass/fail state.
- Coverage must use the real project configuration.
- Exclusions require documented justification.
- Coverage percentage alone does not prove contract or integration quality.

## 7. Static analysis summary

| Project | Tool | Project key | Status | Issues | Last execution | Evidence |
|---|---|---|---|---:|---|---|
| DP-API | SonarQube | DP-API | analysis successful | N/A | 2026-08-02 | `qa-results.md`; scanner exit code 0; analysis uploaded; execution successful |
| SBM-API | SonarQube | N/A | not validated | N/A | N/A | No SonarQube evidence supplied |
| SBM-MANAGER | SonarQube | SBM-MANAGER | not validated | N/A | N/A | Project SonarQube configuration present; fresh server-side Quality Gate evidence pending |
| SBM-DB | SonarQube Community Build | SBM-DB | Quality Gate PASSED | N/A | 2026-08-08 | `qa-results.md`; scanner exit code 0; server-side Quality Gate PASSED; Flyway SQL excluded from SonarQube Community Build |
| SBM-AI-ASSISTANT | SonarQube | N/A | not validated | N/A | N/A | No SonarQube evidence supplied |

Rules:

- Quality Gate status must come from actual server output.
- Planning upgrades may require SonarQube validation, but must not record a status before execution.
- Scanner failure is not equivalent to a failed Quality Gate.
- Project keys, URLs and credentials must not be invented or exposed.
- For SBM-DB, PL/SQL/Flyway SQL is not a Community Build static-analysis gate; database correctness must be evidenced through Flyway/PostgreSQL validation.

## 8. Security validation summary

Required transversal checks:

- unauthenticated requests;
- invalid or expired credentials;
- authenticated but unauthorized requests;
- wrong tenant or brand;
- missing module;
- insufficient role;
- object-level restrictions;
- client versus internal permissions;
- AI-triggered actions using identical authorization rules;
- ZIP path traversal;
- symlinks;
- absolute paths;
- unauthorized patch targets;
- secret leakage.

Current status:

```text
No suite-wide security validation evidence supplied.
```

## 9. API validation summary

Required checks:

- canonical API owner;
- HTTP method and path;
- request body;
- response body;
- status codes;
- public error contract;
- authentication;
- authorization;
- pagination and filtering;
- idempotency;
- compatibility with existing consumers.

Any method, path, request body or response contract change must update `SUITE_CONTEXT.md` and corresponding QA records.

Current status:

```text
No complete transversal API validation evidence supplied.
```

## 10. Database validation summary

Mandatory comparison:

```text
current PostgreSQL schema
↔ current Flyway scripts
↔ current DBML
↔ application model
↔ serializer and public contract
```

Required checks:

- field names and types;
- nullability;
- foreign keys;
- constraints and indexes;
- generated identifiers;
- triggers;
- transactions;
- logical deletion;
- audit and version fields;
- unmanaged model configuration;
- absence of unauthorized migrations.

Current status:

```text
SBM-DB project-level Flyway validation is current and passing for sbm_business, ditaly_pasta, cross and analytics.
Complete transversal validation across application models, DBML, serializers and public contracts remains pending.
```

## 11. Deployment validation summary

Required checks:

- required containers are running;
- container names and ports do not conflict;
- internal services resolve through Docker;
- dependencies become ready;
- health checks respond;
- environment variables load from the expected source;
- failure of one dependency produces a controlled error;
- rollback and backup behavior work;
- no secret values appear in logs or generated packages.

Known shared network:

```text
sbm-network
```

Current status:

```text
No complete transversal deployment validation evidence supplied.
```

## 12. Defect classification

| Severity | Name | Definition | Release effect |
|---:|---|---|---|
| 0 | none | No observed defect | none |
| 1 | very low | Cosmetic or negligible operational effect | normally non-blocking |
| 2 | low | Limited non-critical behavior affected | may be accepted |
| 3 | medium | Relevant feature degradation with workaround | requires explicit decision |
| 4 | high | Major capability, security or integration failure | blocking |
| 5 | critical | Data loss, privilege bypass, cross-tenant access or system-wide failure | blocking |

Every defect must include:

- affected project;
- description;
- reproduction evidence;
- severity;
- owner;
- status;
- accepted workaround if applicable.

## 13. Risk classification

| Risk | Meaning | Expected action |
|---:|---|---|
| 0 | none | no action |
| 1 | very low | monitor |
| 2 | low | plan correction |
| 3 | medium | explicit owner and mitigation |
| 4 | high | block unless accepted |
| 5 | critical | mandatory block |

Risk values must be integers from `0` to `5`.

## 14. Release criteria

Release statuses:

```text
PASS
→ all required criteria validated

PASS WITH ACCEPTED RISK
→ required criteria validated except documented non-blocking risks

BLOCKED
→ dependency, environment or source unavailable

FAIL
→ observed behavior violates the accepted contract
```

Objective closure requires:

- implementation evidence when implementation changes are claimed;
- applicable planned QA updated with actual results;
- canonical QA status `passed` when `scripts/qa-check.sh` exists, or tooling-verified `not-applicable` when it does not;
- successful SonarQube validation when applicable;
- synchronized project and global QA contexts;
- removal of the objective from active and pending contexts;
- append of the completed objective to `SBM-SUITE/context/COMPLETED_OBJECTIVES.md`.

A release requires:

- applicable project quality gates;
- transversal integration checks when relevant;
- security validation;
- failure-path validation;
- database impact statement;
- migration statement;
- coverage and static-analysis evidence when configured;
- updated contexts;
- updated documentation when required;
- no unaccepted high or critical risk.

## 15. Accepted exceptions

| Exception ID | Scope | Description | Risk | Reason | Owner | Expiration | Status |
|---|---|---|---:|---|---|---|---|
| N/A | N/A | No accepted QA exceptions currently evidenced | 0 | N/A | N/A | N/A | none |

An exception must never be inferred from missing evidence.

## 16. Current QA status

Current suite QA state:

```text
Status: PARTIALLY VALIDATED
Reason: DP-API and SBM-MANAGER supplied successful current test, coverage, SonarScanner execution and server-side Quality Gate evidence; other projects and transversal gates remain incomplete.
```

Closure applicability for the Context orchestration repository:

```text
Project: sbm-suite-context
QA status: not-applicable
Structural reason: scripts/qa-check.sh does not currently exist at the selected repository root
Effect: closure tooling emits explicit deterministic evidence; adding that path automatically makes QA applicable
```

Verified DP-API closure evidence:

```text
Generated at: 2026-08-07T04:29:30Z
65 tests passed
0 tests failed
88% configured pytest coverage
coverage.xml generated
SonarScanner exit code 0
ANALYSIS SUCCESSFUL
EXECUTION SUCCESS
Quality Gate: OK
```

Verified SBM-MANAGER implementation-closure evidence:

```text
Generated at: 2026-08-14T16:05:03Z
45 tests passed
0 tests failed
Coverage: 70.14%
SonarScanner exit code: 0
Scanner execution result: success
Server-side Quality Gate: PASSED
Runtime: Docker
```

Tenant isolation, object permissions, cross-project integration, deployment and database compatibility remain outside the validated scope.

Closure evidence for `OBJ-CTX-013`:

```text
Project: sbm-suite-context
Objective: OBJ-CTX-013
QA status: not-applicable
QA applicable: false
QA workflow: scripts/qa-check.sh
Evidence file: qa-results.md
Evidence SHA-256: ce4d484d05fe0748e278c64df4d97671aee4f603f0bfd4f9d0d49ca83dbe3469
Reason: no applicable QA workflow is currently defined for sbm-suite-context: scripts/qa-check.sh does not exist
```

## 17. Pending QA work

1. Define project-specific coverage thresholds.
2. Define mandatory server-side SonarQube Quality Gate checks.
3. Build and maintain test inventories for remaining projects.
4. Validate section-patch import security and rollback behavior end to end.
5. Implement documentation upgrade QA.
6. Add transversal tenant-isolation tests.
7. Add frontend-to-API contract tests.
8. Add AI Tool-to-API authorization tests.
9. Add API-to-database compatibility tests.
10. Create QA contexts for remaining projects.

## 18. Related documentation

Relevant documentation domains include:

- QA and Testing;
- Security and DevSecOps;
- Development;
- Roadmap;
- Observability;
- DevOps;
- SBM Suite.

Paths must use:

```text
SBM-SUITE/context/documentation/pages/<page>/<page>.md
SBM-SUITE/context/documentation/pages/<page>/subpages/<subpage>.md
```

Specific paths will be added when the documentation format and tree are finalized.

## 19. Document boundary

This file stores transversal QA policy, planned and executed test inventory, summarized project status, quality gates, evidence state, risks and release criteria.

It does not replace:

- detailed project test plans;
- project fixtures;
- project commands;
- raw coverage reports;
- SonarQube reports;
- deployment instructions;
- security architecture;
- database schema definitions;
- documentation page content.

Detailed evidence remains in each project QA context and generated QA artifacts.
