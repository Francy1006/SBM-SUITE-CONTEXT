#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/objective-git-finalize.sh <objective-branch> <commit-message>
USAGE
}

[[ "$#" == "2" ]] || {
  usage >&2
  exit 1
}

OBJECTIVE_BRANCH="$1"
COMMIT_MESSAGE="$2"

[[ -n "${COMMIT_MESSAGE//[[:space:]]/}" ]] || {
  echo "ERROR: commit-message no puede estar vacío" >&2
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
OBJECTIVE_BRANCH_SCRIPT="${SCRIPT_DIR}/objective-branches.sh"

[[ -f "${PROJECT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe context/PROJECT_CONTEXT.md" >&2
  exit 1
}
[[ -x "${OBJECTIVE_BRANCH_SCRIPT}" ]] || {
  echo "ERROR: No existe scripts/objective-branches.sh ejecutable" >&2
  exit 1
}

REPOSITORY_LIST="$(mktemp)"
CHANGED_LIST="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}" "${CHANGED_LIST}"' EXIT

python3 - "${PROJECT_CONTEXT_FILE}" "${SUITE_ROOT}" > "${REPOSITORY_LIST}" <<'PY'
from pathlib import Path, PurePosixPath
import os
import re
import sys

source = Path(sys.argv[1]).read_text(encoding="utf-8")
suite_root = Path(sys.argv[2]).resolve(strict=True)
match = re.search(
    r"^## 6\. Project objective summaries\s*$"
    r"(.*?)(?=^##\s+|\Z)",
    source,
    flags=re.MULTILINE | re.DOTALL,
)
if match is None:
    raise SystemExit("ERROR: PROJECT_CONTEXT.md no contiene Project objective summaries")

table_lines = [
    line.strip()
    for line in match.group(1).splitlines()
    if line.strip().startswith("|") and line.strip().endswith("|")
]
if len(table_lines) < 2:
    raise SystemExit("ERROR: Project objective summaries no contiene una tabla")

def cells(line: str) -> list[str]:
    return [value.strip() for value in line[1:-1].split("|")]

headers = cells(table_lines[0])
try:
    main_context_index = headers.index("Main context")
except ValueError as exc:
    raise SystemExit("ERROR: Project objective summaries no contiene Main context") from exc

repositories: list[str] = []
for line in table_lines[2:]:
    values = cells(line)
    if len(values) != len(headers):
        raise SystemExit("ERROR: Project objective summaries contiene una fila inválida")
    main_context = values[main_context_index].strip("`")
    suffix = "/context/PROJECT_CONTEXT.md"
    if main_context == "context/PROJECT_CONTEXT.md":
        repository = "context"
    elif main_context.endswith(suffix):
        repository = main_context[: -len(suffix)]
    else:
        raise SystemExit(
            "ERROR: Main context no resuelve un repositorio canónico: " + main_context
        )
    path = PurePosixPath(repository)
    if path.is_absolute() or ".." in path.parts or str(path) != repository or not path.parts:
        raise SystemExit(
            "ERROR: Repositorio no canónico en Project objective summaries: " + repository
        )
    if repository not in repositories:
        repositories.append(repository)

for current_root, directory_names, file_names in os.walk(suite_root):
    if ".git" not in directory_names and ".git" not in file_names:
        continue
    repository = Path(current_root).relative_to(suite_root).as_posix()
    if repository == ".":
        raise SystemExit("ERROR: SBM-SUITE no debe ser un repositorio Git raíz")
    if repository not in repositories:
        repositories.append(repository)
    directory_names[:] = []

if not repositories:
    raise SystemExit("ERROR: No se resolvieron repositorios SBM registrados")

print("\n".join(repositories))
PY

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
  echo "Sin repositorios con cambios; no hay nada que finalizar."
  exit 0
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
done < "${CHANGED_LIST}"

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
    echo "Sin cambios staged en ${relative_path}; se omite."
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

echo "Finalización Git transversal completada para ${OBJECTIVE_BRANCH}."
