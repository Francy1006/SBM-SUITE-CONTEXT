# SBM Suite context

## Overview

This repository is the Git source of truth for SBM Suite's global context contracts, documentation contracts, objective lifecycle, and manual context/documentation workflows.

## Purpose

It keeps cross-project knowledge synchronized, separates active and pending objectives from completed history, and avoids duplicating each project's internal service, model, script, or implementation inventory.

## Architecture

Canonical suite layout:

```text
SBM-SUITE/
├── context/
│   ├── COMPLETED_OBJECTIVES.md
│   ├── documentation/pages/
│   ├── input/
│   ├── output/
│   ├── backup/
│   ├── QA/
│   │   ├── qa-context.sh
│   │   ├── qa-project.sh
│   │   ├── qa-all.sh
│   │   └── output/
│   ├── scripts/
│   │   ├── git-flow-policy.py
│   │   ├── objective-branches.sh
│   │   ├── context-deploy.sh
│   │   ├── context-upgrade.sh
│   │   ├── documentation-deploy.sh
│   │   ├── documentation-upgrade.sh
│   │   ├── objective-git-finalize.sh
│   │   ├── objective-git-cleanup.sh
│   │   ├── objective-git-state.py
│   │   ├── repos-branches.sh
│   │   ├── repos-changes.sh
│   │   ├── repos-check.sh
│   │   ├── suite-artifacts.py
│   │   ├── suite-repositories.py
│   │   └── project-tree.sh
│   ├── shared/
│   │   ├── artifacts.json
│   │   └── TRANSVERSAL_GOVERNANCE.md
│   ├── SBM_AGENT.md
│   └── project-tree.txt
├── DP/DP-API/
└── SBM/
    ├── SBM-API/
    ├── SBM-DB/
    ├── SBM-MANAGER/
    └── sbm-ai-assistant/
```

Container project roots mirror the brand hierarchy under `/suite/<brand>/<project>`, including `/suite/sbm/SBM-MANAGER` for the web frontend and `/suite/sbm/SBM-DB` for PostgreSQL/Flyway ownership.


### Canonical naming and planned governance

Canonical application/project display names use uppercase; existing filesystem paths and backend registry identifiers remain unchanged unless a dedicated migration renames them. `OBJ-CTX-037` repairs first-push upstream handling; `OBJ-CTX-038` introduces Git Flow; `OBJ-CTX-039` governs controlled `__BASE-*` lineage; `OBJ-CTX-040` creates `SBM-SECURITY-API`; `OBJ-CTX-041` accepts workflow-prefixed upgrade ZIP suffixes; `OBJ-CTX-042` publishes Documentation to Notion; `OBJ-CTX-043` synchronizes Objectives to Jira; `OBJ-CTX-044` standardizes Agent↔API/Tool contracts. `DP-ARCH-001` must complete before `BASE-FRANCHISE-001` generates `__BASE-FRANCHISE-API` from the validated DP-API reference.

## Requirements

- Git working tree access to the current suite.
- Project `.env.dev` defining `SBM_SUITE_ROOT` for deployment scripts.
- The runtime dependencies required by each project-owned workflow.

## Configuration

Global contracts are `FORMAT_CONTEXT.md` and `SYS_PROMPT.md`. Documentation-specific contracts are `documentation/FORMAT_CONTEXT.md` and `documentation/SYS_PROMPT.md`. `PROJECT_CONTEXT.md` stores only active and pending objectives, while `COMPLETED_OBJECTIVES.md` stores the single global history grouped by project. Secret values and `.env` files must never be included in packages, manifests, contexts, or documentation.

## Installation

No standalone installation is required for the Markdown contracts. All manual Context and Documentation workflows use the canonical scripts in this repository; project-local scripts are not orchestration authorities.

## Runtime

`context-deploy` receives a registered project name, validates its canonical path through the backend Project Registry, refreshes the global `project-tree.txt`, gathers Git and QA evidence from that project, and requests the RAG package. `context-upgrade` obtains the project from the ZIP manifest and applies project-scoped or suite-scoped rules accordingly. Documentation deploy is global: it compares the complete active, pending and completed Context lifecycle with all functional Documentation pages, selects real candidates across projects and uses `sbm-suite-context` only as an internal backend identity.

Objective creation uses `planning-activation`. Activating one or more objectives that already exist as pending uses one atomic `objective-activation` with a complete payload per objective expressing desired `status=active`; every transition preserves ID, description, priority and target date, permits an explicit valid branch migration (including a shared branch), and never inserts duplicate objectives.

During `implementation-progress` for `sbm-suite-context`, `context-deploy` can validate the transversal without-Sonar summary and queue, include Context QA evidence when present, and normalize that evidence into the generated context package without changing the objective lifecycle state.

Every 1..N lifecycle batch requires successful complete-suite evidence from `QA/qa-full.sh` after the branch changes and before finalization; fast-track transitions and lifecycle-only changes never bypass Context QA, the all-project with-Sonar queue or Documentation.

## Usage

Use `input/` only for Context upgrade ZIP exchange and `output/` only for generated workflow artifacts. Active and pending objectives remain in project and global `PROJECT_CONTEXT.md` files. Completed objectives are stored only in global `COMPLETED_OBJECTIVES.md`. Documentation pages live only below `documentation/pages/<page>/`, with subpages below `documentation/pages/<page>/subpages/`. Full-object lifecycle batches are serialized by SBM Agent, deterministically gzip-compressed (`mtime=0`), standard-base64 encoded, prefixed with `SBM-GZIP-BASE64-V1`, round-trip verified against the frozen batch and then streamed to the existing `context-deploy.sh` through stdin using `-`. Raw JSON paste is not canonical. The script decodes/validates using internal temporary files and removes them automatically.

Execute from the local repository root `SBM-SUITE/context`:

```bash
./scripts/context-deploy.sh <project_name> <lifecycle_phase> '<small-objectives-json-array>|-' [user_prompt]
./scripts/context-upgrade.sh
./scripts/documentation-deploy.sh
./scripts/documentation-upgrade.sh
./QA/qa-context.sh
./QA/qa-project.sh <project> --without-sonar
./QA/qa-all.sh --without-sonar
./QA/qa-project.sh <project> --with-sonar --sonarqube-ready
./QA/qa-all.sh --with-sonar --sonarqube-ready
./scripts/objective-git-finalize.sh <objective-id> <objective-branch>
./scripts/objective-git-cleanup.sh <objective-id> <objective-branch>
./scripts/objective-branches.sh prepare <objective-branch>
./scripts/objective-branches.sh verify <objective-branch>
./scripts/suite-artifacts.py check all
./scripts/suite-artifacts.py apply <project-or-path> [<project-or-path> ...]
./scripts/repos-check.sh
./scripts/project-tree.sh
```

All Context and Documentation commands and artifact paths are relative to this working directory.

Every temporary branch finalization is fail-safe. It expects
`QA/output/finalization-gate.json` with the exact branch, ordered objective IDs
and `status: "passed"`, plus
`documentation/output/finalization-gate.json` with the same batch and
`status: "updated"`. `QA/qa-full.sh` creates the QA gate only after Context QA
and the sequential all-project Sonar queue pass; `objective-documentation-gate.py`
records the Documentation gate only after a real global Context→Documentation reconciliation reports `synchronized=true`; lifecycle `Documentation` cells are not used as a substitute for reconciliation.

QA modes are intentionally split. Context QA runs the Context regression suite and syntax checks without Sonar. Project `without-sonar` mode uses only project-owned split test/coverage entrypoints and never bypasses Sonar. Project `with-sonar` mode executes canonical `scripts/qa-check.sh` after explicit SonarQube readiness confirmation. The all-project Sonar mode runs sequentially and records its local queue in `QA/output/qa-all-with-sonar-queue.tsv`.

When Documentation is already synchronized, deploy exits successfully with `Documentation already synchronized` and does not create a package that would lead to a metadata-only upgrade.

All Context/Documentation HTTP orchestration uses bounded connect/total timeouts (`AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS`, `AI_ASSISTANT_MAX_TIME_SECONDS`) so a lost backend worker cannot leave lifecycle commands blocked indefinitely.

Supported lifecycle phases are `planning-activation`, `objective-activation`, `objective-registration`, `objective-completion`, `objective-deletion`, `objective-update`, `implementation-progress`, and the compatible legacy `implementation-closure`. Every route accepts an atomic 1..N batch, including explicitly identified multiproject batches routed through `sbm-suite-context`; creation may start directly as `pending`, `active` or `completed`.

Every successful context upgrade writes one backup to `backup/<timestamp>_<project>/`, including original files, `EXECUTIVE_README.md`, `COMMIT_MESSAGE.md`, and `BACKUP_MANIFEST.json`.

`context-upgrade.sh` accepts exactly one ZIP matching `input/context-upgrade*.zip`; `documentation-upgrade.sh` accepts exactly one ZIP matching `documentation/input/documentation-upgrade*.zip`. Client-added suffixes such as `(32)` are accepted without manual renaming. Ambiguous ZIP sets and invalid workflow prefixes are rejected, and the accepted file is normalized internally to the canonical filename before backend validation.

## API or interfaces

The context workflow indexes global and project contexts in `sbm_contexts`. Project requests send `project_root=/suite/<brand>/<project>` to the context export interface.

## Development

Keep this README suite-level. Update it only for structural, architectural, shared functional, or global workflow changes. Reusable component inventories belong in each project's README.

## Validation

Validate exact headings and tables, objective synchronization, completed-objective append-only history, authorized targets, repository-relative paths, manifest/file agreement, SHA-256 hashes, backup contents, and absence of secrets before applying an upgrade.

Before contacting the backend, `documentation-upgrade.sh` rejects any archive unless `manifest.updated_files` equals the complete set of physical non-manifest ZIP files and reports both undeclared physical files and declared paths missing from the ZIP.

## Security

Do not commit or package secrets, tokens, credentials, `.env` files, raw vectors, absolute local paths, or unauthorized project files.

## Known limitations

The workflows remain manually initiated. `main` is the only stable and integration destination. Every `FEATURE-*`, `BUGFIX-*`, `RELEASE-*` or `HOTFIX-*` work branch starts from `main`, requires complete QA and Documentation, merges with `--no-ff` directly into `main`, returns all repositories to `main`, and is then deleted locally/remotely. Objective branch preparation/finalization and cleanup are explicit transversal operations and are never executed implicitly by the agent.

## Target multi-brand portfolio

The current repository governs an expanding suite. Ditaly Pasta/DP remains the historical real-data reference implementation. KS, PC and CG are production-target brands. Planned shared projects include `SBM-CORE`, `SBM-CALCULATION`, `SBM-UTIL`, `SBM-AI-MANAGER`, `SBM-SECURITY`, `SBM-SECURITY-API`, `SBM-MARKETING`, `SBM-CONTENT`, `SBM-CONTROL` and `SBM-MOBILE`. Reusable bases are `__BASE-FRANCHISE-API`, `__BASE-STORE`, `__BASE-MOBILE`, `__BASE-CLIENT` and `__BASE-CUSTOMER`; derived brand channels are listed in `PROJECT_CONTEXT.md` and `SUITE_CONTEXT.md`.

Planned repositories are documentation/backlog targets only until onboarding creates a real repository and canonical Project Registry entry. Database changes listed in global objectives remain pending until implemented and evidenced in SBM-DB through Flyway/DBML/PostgreSQL.

Implemented governance includes `SBM_AGENT.md` as the minimal clean-chat bootstrap over the canonical `INIT_CONTEXT.md` and controlled common-artifact propagation from `SBM-SUITE/context`. `shared/artifacts.json` is the explicit allowlist; `check` is read-only and `apply` performs a global clean-tree preflight before creating or updating managed files. Full project Context files and project-specific scripts are never copied indiscriminately.

## Related documentation

- `SBM_AGENT.md`
- `PROJECT_CONTEXT.md`
- `COMPLETED_OBJECTIVES.md`
- `SUITE_CONTEXT.md`
- `FORMAT_CONTEXT.md`
- `SYS_PROMPT.md`
- `documentation/FORMAT_CONTEXT.md`
- `documentation/SYS_PROMPT.md`

`repos-check.sh` is the single read-only repository-state entrypoint. It lists the current branch and displays `git status --short` for every suite repository including `context`, without modifying Git state. It does not accept or validate an expected branch; objective branch enforcement remains in `objective-branches.sh verify`. Use it immediately after objective branch preparation and again after implementation changes before progress export.
