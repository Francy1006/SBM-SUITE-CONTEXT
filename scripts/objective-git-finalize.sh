#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/objective-git-finalize.sh <objective-id> <objective-branch>
USAGE
}

[[ "$#" == "2" ]] || {
  usage >&2
  exit 1
}

OBJECTIVE_ID="$1"
OBJECTIVE_BRANCH="$2"
COMMIT_MESSAGE="chore(objective): finalize ${OBJECTIVE_ID}"

[[ -n "${OBJECTIVE_ID//[[:space:]]/}" ]] || {
  echo "ERROR: objective-id no puede estar vacío" >&2
  exit 1
}

git check-ref-format --branch "${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
  echo "ERROR: Branch de objetivo inválida: ${OBJECTIVE_BRANCH}" >&2
  exit 1
}
[[ "${OBJECTIVE_BRANCH}" != "main" ]] || {
  echo "ERROR: La branch del objetivo no puede ser main" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
PROJECT_CONTEXT_FILE="${CONTEXT_ROOT}/PROJECT_CONTEXT.md"
COMPLETED_OBJECTIVES_FILE="${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md"
OBJECTIVE_BRANCH_SCRIPT="${SCRIPT_DIR}/objective-branches.sh"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"

[[ -f "${PROJECT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe context/PROJECT_CONTEXT.md" >&2
  exit 1
}
[[ -f "${COMPLETED_OBJECTIVES_FILE}" ]] || {
  echo "ERROR: No existe context/COMPLETED_OBJECTIVES.md" >&2
  exit 1
}
[[ -x "${OBJECTIVE_BRANCH_SCRIPT}" ]] || {
  echo "ERROR: No existe scripts/objective-branches.sh ejecutable" >&2
  exit 1
}
[[ -x "${REPOSITORY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/suite-repositories.py ejecutable" >&2
  exit 1
}

# Hard lifecycle gate: finalization is legal only after the objective is already
# persisted as completed and removed from active/pending operational state.
python3 - "${OBJECTIVE_ID}" "${OBJECTIVE_BRANCH}" \
  "${PROJECT_CONTEXT_FILE}" "${COMPLETED_OBJECTIVES_FILE}" <<'PY'
from pathlib import Path
import re
import sys

objective_id, objective_branch, project_path, completed_path = sys.argv[1:]
project_text = Path(project_path).read_text(encoding="utf-8")
completed_text = Path(completed_path).read_text(encoding="utf-8")


def cells(line: str) -> list[str]:
    return [value.strip() for value in line[1:-1].split("|")]


def table_records(text: str):
    headers = None
    for raw in text.splitlines():
        line = raw.strip()
        if not (line.startswith("|") and line.endswith("|")):
            headers = None
            continue
        values = cells(line)
        if values and all(re.fullmatch(r":?-{3,}:?", value) for value in values):
            continue
        if "Objective ID" in values or "ID" in values:
            headers = values
            continue
        if headers is None or len(values) != len(headers):
            continue
        yield dict(zip(headers, values))


completed_matches = [
    row
    for row in table_records(completed_text)
    if row.get("Objective ID") == objective_id
]
if len(completed_matches) != 1:
    raise SystemExit(
        f"ERROR: {objective_id} no está completed exactamente una vez en COMPLETED_OBJECTIVES.md"
    )

record = completed_matches[0]
status = record.get("Final status", "")
branch = record.get("Branch", "").strip("`")
if status != "completed":
    raise SystemExit(
        f"ERROR: {objective_id} tiene Final status '{status or 'N/A'}'; se requiere completed"
    )
if branch != objective_branch:
    raise SystemExit(
        f"ERROR: Branch de cierre para {objective_id} es '{branch or 'N/A'}', no '{objective_branch}'"
    )

for row in table_records(project_text):
    row_id = row.get("ID") or row.get("Objective ID")
    status = row.get("Status", "")
    if row_id == objective_id and status in {"active", "pending"}:
        raise SystemExit(
            f"ERROR: {objective_id} todavía figura como {status} en PROJECT_CONTEXT.md"
        )

print(f"Lifecycle finalizado validado: {objective_id} / {objective_branch}")
PY

REPOSITORY_LIST="$(mktemp)"
CHANGED_LIST="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}" "${CHANGED_LIST}"' EXIT

python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORY_LIST}"

# La verificación transversal sucede antes de cualquier add/commit/push/merge.
"${OBJECTIVE_BRANCH_SCRIPT}" verify "${OBJECTIVE_BRANCH}"

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    printf '%s\n' "${relative_path}" >> "${CHANGED_LIST}"
  fi
done < "${REPOSITORY_LIST}"

if [[ ! -s "${CHANGED_LIST}" ]]; then
  echo "Sin repositorios con cambios; se normalizarán todos los repositorios a main."
fi

preflight_repository() {
  local relative_path="$1"
  local repository="${SUITE_ROOT}/${relative_path}"
  local current_branch
  local lock_name

  current_branch="$(git -C "${repository}" branch --show-current)"
  [[ "${current_branch}" == "${OBJECTIVE_BRANCH}" ]] || {
    echo "ERROR: ${relative_path}: branch actual '${current_branch:-detached HEAD}', esperada '${OBJECTIVE_BRANCH}'" >&2
    return 1
  }
  [[ -z "$(git -C "${repository}" diff --name-only --diff-filter=U)" ]] || {
    echo "ERROR: ${relative_path}: existen conflictos sin resolver" >&2
    return 1
  }
  git -C "${repository}" diff --check >/dev/null || {
    echo "ERROR: ${relative_path}: git diff --check falló" >&2
    return 1
  }
  git -C "${repository}" show-ref --verify --quiet refs/heads/main || {
    echo "ERROR: ${relative_path}: branch local main inexistente" >&2
    return 1
  }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: remote origin inexistente" >&2
    return 1
  }
  git -C "${repository}" fetch origin "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: no se pudo actualizar origin/main" >&2
    return 1
  }
  git -C "${repository}" merge-base --is-ancestor main origin/main || {
    echo "ERROR: ${relative_path}: main local no puede actualizarse por fast-forward a origin/main" >&2
    return 1
  }
  git -C "${repository}" push --dry-run origin \
    "HEAD:refs/heads/${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: la branch del objetivo no puede publicarse por fast-forward" >&2
    return 1
  }
  for lock_name in index.lock HEAD.lock packed-refs.lock; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${lock_name}")" ]] || {
      echo "ERROR: ${relative_path}: bloqueo Git activo (${lock_name})" >&2
      return 1
    }
  done
  for lock_name in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${lock_name}")" ]] || {
      echo "ERROR: ${relative_path}: operación Git en curso (${lock_name})" >&2
      return 1
    }
  done
}

preflight_failed=0
while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  preflight_repository "${relative_path}" || preflight_failed=1
done < "${REPOSITORY_LIST}"

[[ "${preflight_failed}" == "0" ]] || {
  echo "ERROR: Preflight Git transversal fallido; no se ejecutó add/commit/push/merge." >&2
  exit 1
}

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"

  echo "Finalizando ${relative_path}..."
  git -C "${repository}" add .
  if git -C "${repository}" diff --cached --quiet; then
    echo "Sin cambios staged en ${relative_path}; se omite commit."
    continue
  fi
  git -C "${repository}" commit -m "${COMMIT_MESSAGE}"
  git -C "${repository}" push -u origin "${OBJECTIVE_BRANCH}"

  git -C "${repository}" checkout main
  git -C "${repository}" pull --ff-only origin main
  git -C "${repository}" merge --no-ff "${OBJECTIVE_BRANCH}" \
    -m "merge: ${OBJECTIVE_BRANCH}"
  git -C "${repository}" push origin main

done < "${CHANGED_LIST}"

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  if [[ "$(git -C "${repository}" branch --show-current)" != "main" ]]; then
    echo "Normalizando ${relative_path} a main..."
    git -C "${repository}" checkout main
  fi
  git -C "${repository}" pull --ff-only origin main
done < "${REPOSITORY_LIST}"

echo "Finalización Git transversal completada para ${OBJECTIVE_ID} (${OBJECTIVE_BRANCH}). Todos los repositorios quedaron en main."
