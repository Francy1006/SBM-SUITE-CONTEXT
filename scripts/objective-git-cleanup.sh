#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/objective-git-cleanup.sh <objective-id> <objective-branch>
USAGE
}

[[ "$#" == "2" ]] || {
  usage >&2
  exit 1
}

OBJECTIVE_ID="$1"
OBJECTIVE_BRANCH="$2"

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
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"

[[ -f "${PROJECT_CONTEXT_FILE}" ]] || { echo "ERROR: No existe context/PROJECT_CONTEXT.md" >&2; exit 1; }
[[ -f "${COMPLETED_OBJECTIVES_FILE}" ]] || { echo "ERROR: No existe context/COMPLETED_OBJECTIVES.md" >&2; exit 1; }
[[ -x "${REPOSITORY_HELPER}" ]] || { echo "ERROR: No existe scripts/suite-repositories.py ejecutable" >&2; exit 1; }

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

matches = [row for row in table_records(completed_text) if row.get("Objective ID") == objective_id]
if len(matches) != 1:
    raise SystemExit(f"ERROR: {objective_id} no está completed exactamente una vez en COMPLETED_OBJECTIVES.md")
record = matches[0]
if record.get("Final status", "") != "completed":
    raise SystemExit(f"ERROR: {objective_id} no tiene Final status=completed")
branch = record.get("Branch", "").strip("`")
if branch != objective_branch:
    raise SystemExit(f"ERROR: Branch de cierre para {objective_id} es '{branch or 'N/A'}', no '{objective_branch}'")
for row in table_records(project_text):
    row_id = row.get("ID") or row.get("Objective ID")
    if row_id == objective_id and row.get("Status", "") in {"active", "pending"}:
        raise SystemExit(f"ERROR: {objective_id} todavía figura como {row.get('Status')} en PROJECT_CONTEXT.md")
print(f"Lifecycle finalizado validado para cleanup: {objective_id} / {objective_branch}")
PY

REPOSITORY_LIST="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORY_LIST}"

preflight_repository() {
  local relative_path="$1"
  local repository="${SUITE_ROOT}/${relative_path}"
  local current_branch local_main remote_main lock_name remote_branch_ref

  [[ -d "${repository}" ]] || { echo "ERROR: ${relative_path}: directorio inexistente" >&2; return 1; }
  git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "ERROR: ${relative_path}: no es un repositorio Git válido" >&2; return 1; }
  [[ "$(git -C "${repository}" rev-parse --show-toplevel)" == "$(cd "${repository}" && pwd -P)" ]] || { echo "ERROR: ${relative_path}: el path no es la raíz Git" >&2; return 1; }
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || { echo "ERROR: ${relative_path}: working tree contiene cambios locales" >&2; return 1; }
  current_branch="$(git -C "${repository}" branch --show-current)"
  [[ "${current_branch}" == "main" ]] || { echo "ERROR: ${relative_path}: branch actual '${current_branch:-detached HEAD}', esperada 'main'" >&2; return 1; }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || { echo "ERROR: ${relative_path}: remote origin inexistente" >&2; return 1; }
  git -C "${repository}" fetch origin "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || { echo "ERROR: ${relative_path}: no se pudo actualizar origin/main" >&2; return 1; }
  local_main="$(git -C "${repository}" rev-parse main)"
  remote_main="$(git -C "${repository}" rev-parse origin/main)"
  [[ "${local_main}" == "${remote_main}" ]] || { echo "ERROR: ${relative_path}: main local no coincide con origin/main" >&2; return 1; }

  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    git -C "${repository}" merge-base --is-ancestor "${OBJECTIVE_BRANCH}" main || {
      echo "ERROR: ${relative_path}: ${OBJECTIVE_BRANCH} local no está integrada en main" >&2
      return 1
    }
  fi

  remote_branch_ref="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
  if [[ -n "${remote_branch_ref}" ]]; then
    git -C "${repository}" fetch origin "+refs/heads/${OBJECTIVE_BRANCH}:refs/remotes/origin/${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
      echo "ERROR: ${relative_path}: no se pudo actualizar origin/${OBJECTIVE_BRANCH}" >&2
      return 1
    }
    git -C "${repository}" merge-base --is-ancestor "origin/${OBJECTIVE_BRANCH}" main || {
      echo "ERROR: ${relative_path}: origin/${OBJECTIVE_BRANCH} no está integrada en main" >&2
      return 1
    }
  fi

  for lock_name in index.lock HEAD.lock packed-refs.lock; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${lock_name}")" ]] || {
      echo "ERROR: ${relative_path}: bloqueo Git activo (${lock_name})" >&2
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
  echo "ERROR: Preflight de cleanup fallido; no se eliminó ninguna branch." >&2
  exit 1
}

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  echo "Limpiando ${relative_path}..."
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    git -C "${repository}" branch -d "${OBJECTIVE_BRANCH}"
  else
    echo "Branch local inexistente; se omite."
  fi
  if git -C "${repository}" ls-remote --exit-code origin "refs/heads/${OBJECTIVE_BRANCH}" >/dev/null 2>&1; then
    git -C "${repository}" push origin --delete "${OBJECTIVE_BRANCH}"
  else
    echo "Branch remota inexistente; se omite."
  fi
done < "${REPOSITORY_LIST}"

echo "Cleanup Git transversal completado para ${OBJECTIVE_ID} (${OBJECTIVE_BRANCH})."
