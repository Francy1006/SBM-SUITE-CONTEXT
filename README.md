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
│   ├── project-tree.sh
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

No standalone installation is required for the Markdown contracts. Project-owned scripts consume this repository from the suite root.

## Runtime

`context-deploy` validates the lifecycle phase and objective batch, refreshes `project-tree.txt`, gathers bounded evidence, and requests the RAG package. For `sbm-suite-context`, `SBM-SUITE/context` is the suite-scoped lifecycle target: planning objectives are synchronized directly in global `PROJECT_CONTEXT.md`, and project-scoped lifecycle patches are not used. The closing upgrade reconciles applicable QA state, removes the objective from operational context, and appends it to `COMPLETED_OBJECTIVES.md`. Documentation uses a separate deploy/upgrade flow only after implementation closure.

## Usage

Use `input/` and `output/` for the global context workflow. Active and pending objectives remain in project and global `PROJECT_CONTEXT.md` files. Completed objectives are stored only in global `COMPLETED_OBJECTIVES.md`. Documentation pages live only below `documentation/pages/<page>/`, with subpages below `documentation/pages/<page>/subpages/`.

Every successful context upgrade writes one backup to `backup/<timestamp>_<project>/`, including original files, `EXECUTIVE_README.md`, `COMMIT_MESSAGE.md`, and `BACKUP_MANIFEST.json`.

## API or interfaces

The context workflow indexes global and project contexts in `sbm_contexts`. Project requests send `project_root=/suite/<brand>/<project>` to the context export interface.

## Development

Keep this README suite-level. Update it only for structural, architectural, shared functional, or global workflow changes. Reusable component inventories belong in each project's README.

## Validation

Validate exact headings and tables, objective synchronization, completed-objective append-only history, authorized targets, repository-relative paths, manifest/file agreement, SHA-256 hashes, backup contents, and absence of secrets before applying an upgrade.

## Security

Do not commit or package secrets, tokens, credentials, `.env` files, raw vectors, absolute local paths, or unauthorized project files.

## Known limitations

The workflows remain manually initiated. Git branch creation, commit and push are not automated. Documentation creation, deletion, rename, and structural moves require explicit manual contract updates.

## Related documentation

- `PROJECT_CONTEXT.md`
- `COMPLETED_OBJECTIVES.md`
- `SUITE_CONTEXT.md`
- `FORMAT_CONTEXT.md`
- `SYS_PROMPT.md`
- `documentation/FORMAT_CONTEXT.md`
- `documentation/SYS_PROMPT.md`
