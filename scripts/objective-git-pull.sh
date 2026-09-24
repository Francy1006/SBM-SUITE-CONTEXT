#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == "1" ]] || {
  echo "Uso: ./scripts/objective-git-pull.sh <objective-id>" >&2
  exit 1
}

OBJECTIVE_ID="$1"
export GIT_TERMINAL_PROMPT=0
export GIT_PAGER=cat
export GIT_EDITOR=true
export PYTHONDONTWRITEBYTECODE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
PROJECT_CONTEXT_FILE="${CONTEXT_ROOT}/PROJECT_CONTEXT.md"
COMPLETED_OBJECTIVES_FILE="${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md"
CLI_HELPER="${SCRIPT_DIR}/sbm-cli.py"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"
POLICY_HELPER="${SCRIPT_DIR}/git-flow-policy.py"
PATH_PORTABILITY_HELPER="${SCRIPT_DIR}/path-portability.py"

for required_file in \
  "${PROJECT_CONTEXT_FILE}" \
  "${CLI_HELPER}" \
  "${REPOSITORY_HELPER}" \
  "${POLICY_HELPER}" \
  "${PATH_PORTABILITY_HELPER}"; do
  [[ -f "${required_file}" ]] || {
    echo "ERROR: archivo requerido inexistente: ${required_file}" >&2
    exit 1
  }
done

resolved_values="$(
  python3 "${CLI_HELPER}" \
    --project-context "${PROJECT_CONTEXT_FILE}" \
    --objective-id "${OBJECTIVE_ID}"
)"
IFS=$'\t' read -r RESOLVED_ID OBJECTIVE_BRANCH _ <<< "${resolved_values}"
[[ "${RESOLVED_ID}" == "${OBJECTIVE_ID}" ]] || {
  echo "ERROR: el lifecycle resolvió ${RESOLVED_ID}, no ${OBJECTIVE_ID}" >&2
  exit 1
}

IFS=$'\t' read -r _ BASE_BRANCH _ _ _ _ < <(
  python3 "${POLICY_HELPER}" describe "${OBJECTIVE_BRANCH}" --format tsv
)
[[ "${BASE_BRANCH}" == "main" ]] || {
  echo "ERROR: La política temporal debe nacer desde main" >&2
  exit 1
}

lifecycle_digest() {
  python3 - "${PROJECT_CONTEXT_FILE}" "${COMPLETED_OBJECTIVES_FILE}" <<'PY'
from hashlib import sha256
from pathlib import Path
import sys

digest = sha256()
for path in sys.argv[1:]:
    file = Path(path)
    digest.update(file.name.encode("utf-8"))
    digest.update(b"\0")
    if file.is_file():
        digest.update(file.read_bytes())
    digest.update(b"\0")
print(digest.hexdigest())
PY
}

LIFECYCLE_BEFORE="$(lifecycle_digest)"

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

preflight_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"
  local name
  local occupied

  [[ -d "${repository}" ]] || {
    echo "ERROR: ${path}: directorio inexistente" >&2
    return 1
  }
  git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "ERROR: ${path}: no es un repositorio Git válido" >&2
    return 1
  }
  python3 "${PATH_PORTABILITY_HELPER}" equivalent \
    "$(git -C "${repository}" rev-parse --show-toplevel)" \
    "$(cd "${repository}" && pwd -P)" || {
    echo "ERROR: ${path}: el path resuelto no es la raíz del repositorio" >&2
    return 1
  }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || {
    echo "ERROR: ${path}: origin inexistente" >&2
    return 1
  }
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || {
    echo "ERROR: ${path}: working tree contiene cambios locales" >&2
    return 1
  }
  git -C "${repository}" diff --check >/dev/null || {
    echo "ERROR: ${path}: git diff --check falló" >&2
    return 1
  }

  occupied="$(
    git -C "${repository}" worktree list --porcelain \
      | awk '/^branch refs\/heads\// {sub(/^branch refs\/heads\//, ""); print}'
  )"
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    if [[ "$(git -C "${repository}" branch --show-current)" != "${OBJECTIVE_BRANCH}" ]] \
      && grep -Fxq "${OBJECTIVE_BRANCH}" <<< "${occupied}"; then
      echo "ERROR: ${path}: ${OBJECTIVE_BRANCH} está ocupada por otro worktree" >&2
      return 1
    fi
  fi

  for name in \
    index.lock HEAD.lock packed-refs.lock \
    MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${name}")" ]] || {
      echo "ERROR: ${path}: operación Git activa (${name})" >&2
      return 1
    }
  done
}

failed=0
while IFS= read -r path; do
  [[ -z "${path}" ]] || preflight_repository "${path}" || failed=1
done < "${REPOSITORIES}"

[[ "${failed}" == "0" ]] || {
  echo "ERROR: Preflight transversal fallido; no se ejecutó fetch ni se modificó ningún repositorio." >&2
  exit 1
}

fetch_failed=0
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  git -C "${repository}" fetch origin >/dev/null 2>&1 || {
    echo "ERROR: ${path}: git fetch origin falló" >&2
    fetch_failed=1
  }
done < "${REPOSITORIES}"

[[ "${fetch_failed}" == "0" ]] || {
  echo "ERROR: Fetch transversal fallido; no se modificó ningún working tree." >&2
  exit 1
}

[[ "$(lifecycle_digest)" == "${LIFECYCLE_BEFORE}" ]] || {
  echo "ERROR: el estado lifecycle cambió concurrentemente durante fetch" >&2
  exit 1
}

EXPECTED_CONTEXT_HEAD=""

validate_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"
  local remote_ref="refs/remotes/origin/${OBJECTIVE_BRANCH}"
  local counts behind ahead

  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || {
    echo "ERROR: ${path}: el working tree cambió después del preflight" >&2
    return 1
  }
  git -C "${repository}" show-ref --verify --quiet "${remote_ref}" || {
    echo "ERROR: ${path}: origin/${OBJECTIVE_BRANCH} inexistente" >&2
    return 1
  }
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    counts="$(git -C "${repository}" rev-list --left-right --count "${remote_ref}...refs/heads/${OBJECTIVE_BRANCH}")" || {
      echo "ERROR: ${path}: no se pudo determinar la relación local/origin" >&2
      return 1
    }
    read -r behind ahead <<< "${counts}"
    if (( behind > 0 && ahead > 0 )); then
      echo "ERROR: ${path}: ${OBJECTIVE_BRANCH} local no admite fast-forward: divergencia con origin (behind=${behind}, ahead=${ahead})" >&2
      return 1
    fi
    if [[ "${path}" == "context" ]]; then
      if (( behind > 0 )); then
        EXPECTED_CONTEXT_HEAD="$(git -C "${repository}" rev-parse "${remote_ref}")"
      else
        EXPECTED_CONTEXT_HEAD="$(git -C "${repository}" rev-parse "refs/heads/${OBJECTIVE_BRANCH}")"
      fi
    fi
  elif [[ "${path}" == "context" ]]; then
    EXPECTED_CONTEXT_HEAD="$(git -C "${repository}" rev-parse "${remote_ref}")"
  fi
}

failed=0
while IFS= read -r path; do
  [[ -z "${path}" ]] || validate_repository "${path}" || failed=1
done < "${REPOSITORIES}"

[[ "${failed}" == "0" ]] || {
  echo "ERROR: Validación transversal fallida; no se modificó ningún working tree." >&2
  exit 1
}

[[ -n "${EXPECTED_CONTEXT_HEAD}" ]] || {
  echo "ERROR: no se pudo determinar el commit esperado de context" >&2
  exit 1
}

pull_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"

  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    git -C "${repository}" checkout "${OBJECTIVE_BRANCH}"
  else
    git -C "${repository}" checkout --track "origin/${OBJECTIVE_BRANCH}"
  fi
  git -C "${repository}" pull --ff-only origin "${OBJECTIVE_BRANCH}"
  if ! git -C "${repository}" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
    git -C "${repository}" config "branch.${OBJECTIVE_BRANCH}.remote" origin
    git -C "${repository}" config "branch.${OBJECTIVE_BRANCH}.merge" "refs/heads/${OBJECTIVE_BRANCH}"
  fi
}

while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  pull_repository "${path}"
done < "${REPOSITORIES}"

postflight_failed=0
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  [[ "$(git -C "${repository}" branch --show-current)" == "${OBJECTIVE_BRANCH}" ]] || {
    echo "ERROR: ${path}: no terminó en ${OBJECTIVE_BRANCH}" >&2
    postflight_failed=1
    continue
  }
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || {
    echo "ERROR: ${path}: working tree no quedó limpio" >&2
    postflight_failed=1
  }
  git -C "${repository}" merge-base --is-ancestor "refs/remotes/origin/${OBJECTIVE_BRANCH}" HEAD || {
    echo "ERROR: ${path}: HEAD no contiene todos los commits de origin/${OBJECTIVE_BRANCH}" >&2
    postflight_failed=1
  }
done < "${REPOSITORIES}"

[[ "${postflight_failed}" == "0" ]] || {
  echo "ERROR: Postflight transversal fallido." >&2
  exit 1
}

[[ "$(git -C "${CONTEXT_ROOT}" rev-parse HEAD)" == "${EXPECTED_CONTEXT_HEAD}" ]] || {
  echo "ERROR: context cambió concurrentemente durante git pull" >&2
  exit 1
}
[[ -z "$(git -C "${CONTEXT_ROOT}" status --porcelain -- \
  "$(basename "${PROJECT_CONTEXT_FILE}")" \
  "$(basename "${COMPLETED_OBJECTIVES_FILE}")")" ]] || {
  echo "ERROR: el estado lifecycle cambió concurrentemente durante git pull" >&2
  exit 1
}

set +e
updated_values="$({
  python3 "${CLI_HELPER}" \
    --project-context "${PROJECT_CONTEXT_FILE}" \
    --objective-id "${OBJECTIVE_ID}"
} 2>&1)"
updated_status=$?
set -e
if [[ "${updated_status}" != "0" ]]; then
  echo "ERROR: lifecycle incompatible después de actualizar context: ${updated_values}" >&2
  exit 1
fi
IFS=$'\t' read -r UPDATED_ID UPDATED_BRANCH _ <<< "${updated_values}"
[[ "${UPDATED_ID}" == "${OBJECTIVE_ID}" && "${UPDATED_BRANCH}" == "${OBJECTIVE_BRANCH}" ]] || {
  echo "ERROR: lifecycle incompatible después de actualizar context: esperado ${OBJECTIVE_ID}/${OBJECTIVE_BRANCH}, obtenido ${UPDATED_ID}/${UPDATED_BRANCH}" >&2
  exit 1
}

echo "Branch ${OBJECTIVE_BRANCH} actualizada desde origin para ${OBJECTIVE_ID}; commits locales conservados y repositorios listos en la branch del objetivo."
