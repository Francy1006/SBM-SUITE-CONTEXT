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
│   │   ├── context-deploy.sh
│   │   ├── context-upgrade.sh
│   │   ├── documentation-deploy.sh
│   │   ├── documentation-upgrade.sh
│   │   ├── objective-git-finalize.sh
│   │   ├── objective-git-cleanup.sh
│   │   ├── repos-branches.sh
│   │   ├── repos-changes.sh
│   │   ├── repos-check.sh
│   │   ├── suite-repositories.py
│   │   └── project-tree.sh
│   └── project-tree.txt
├── dp/DP-API/
└── sbm/
    ├── SBM-API/
    ├── SBM-DB/
    ├── SBM-MANAGER/
    └── sbm-ai-assistant/
```

Container project roots mirror the brand hierarchy under `/suite/<brand>/<project>`, including `/suite/sbm/SBM-MANAGER` for the web frontend and `/suite/sbm/SBM-DB` for PostgreSQL/Flyway ownership.

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

Objective creation uses `planning-activation`. Activating an objective that already exists as pending uses `objective-activation` with the complete objective payload expressing desired `status=active`; that transition preserves ID, description, priority, target date and branch and never inserts a second objective.

During `implementation-progress` for `sbm-suite-context`, `context-deploy` can validate the transversal without-Sonar summary and queue, include Context QA evidence when present, and normalize that evidence into the generated context package without changing the objective lifecycle state.

During `implementation-closure`, QA applicability is derived structurally from the selected repository's `scripts/qa-check.sh`: absence produces canonical `not-applicable` evidence, while presence requires validated successful execution evidence.

## Usage

Use `input/` and `output/` for the global context workflow. Active and pending objectives remain in project and global `PROJECT_CONTEXT.md` files. Completed objectives are stored only in global `COMPLETED_OBJECTIVES.md`. Documentation pages live only below `documentation/pages/<page>/`, with subpages below `documentation/pages/<page>/subpages/`.

Execute from the local repository root `SBM-SUITE/context`:

```bash
./scripts/context-deploy.sh <project_name> <lifecycle_phase> '<objectives-json-array>' [user_prompt]
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
./scripts/repos-check.sh
./scripts/project-tree.sh
```

All Context and Documentation commands and artifact paths are relative to this working directory.

QA modes are intentionally split. Context QA runs the Context regression suite and syntax checks without Sonar. Project `without-sonar` mode uses only project-owned split test/coverage entrypoints and never bypasses Sonar. Project `with-sonar` mode executes canonical `scripts/qa-check.sh` after explicit SonarQube readiness confirmation. The all-project Sonar mode runs sequentially and records its local queue in `QA/output/qa-all-with-sonar-queue.tsv`.

When Documentation is already synchronized, deploy exits successfully with `Documentation already synchronized` and does not create a package that would lead to a metadata-only upgrade.

Supported lifecycle phases are `planning-activation` (new objectives), `objective-activation` (one existing `pending → active` transition), `implementation-progress`, and `implementation-closure`.

Every successful context upgrade writes one backup to `backup/<timestamp>_<project>/`, including original files, `EXECUTIVE_README.md`, `COMMIT_MESSAGE.md`, and `BACKUP_MANIFEST.json`.

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

The workflows remain manually initiated. Objective branch preparation/finalization and post-finalization branch cleanup are automated by explicit transversal scripts, but are never executed implicitly by the agent. Documentation creation, deletion, rename, and structural moves require explicit manual contract updates.

## Target multi-brand portfolio

The current repository governs an expanding suite. Ditaly Pasta/DP remains the historical real-data reference implementation. KS, PC and CG are production-target brands. Planned shared projects include `sbm-core`, `sbm-calculation`, `sbm-util`, `sbm-ai-manager`, `sbm-security`, `sbm-marketing`, `sbm-content`, `sbm-control` and `sbm-mobile`; planned brand channels are listed in `PROJECT_CONTEXT.md` and `SUITE_CONTEXT.md`.

Planned repositories are documentation/backlog targets only until onboarding creates a real repository and canonical Project Registry entry. Database changes listed in global objectives remain pending until implemented and evidenced in SBM-DB through Flyway/DBML/PostgreSQL.

## Related documentation

- `PROJECT_CONTEXT.md`
- `COMPLETED_OBJECTIVES.md`
- `SUITE_CONTEXT.md`
- `FORMAT_CONTEXT.md`
- `SYS_PROMPT.md`
- `documentation/FORMAT_CONTEXT.md`
- `documentation/SYS_PROMPT.md`

`repos-check.sh` is the single read-only repository-state entrypoint. It lists the current branch and displays `git status --short` for every suite repository including `context`, without modifying Git state. It does not accept or validate an expected branch; objective branch enforcement remains in `objective-branches.sh verify`. Use it immediately after objective branch preparation and again after implementation changes before progress export.
