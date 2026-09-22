#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == "1" ]] || {
  echo "Uso: ./scripts/objective-git-publish.sh <objective-id>" >&2
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
BRANCH_HELPER="${SCRIPT_DIR}/objective-branches.sh"
POLICY_HELPER="${SCRIPT_DIR}/git-flow-policy.py"
PATH_PORTABILITY_HELPER="${SCRIPT_DIR}/path-portability.py"

for required_file in \
  "${PROJECT_CONTEXT_FILE}" \
  "${CLI_HELPER}" \
  "${REPOSITORY_HELPER}" \
  "${BRANCH_HELPER}" \
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

COMMIT_MESSAGE="chore: checkpoint ${OBJECTIVE_ID}"
LIFECYCLE_BEFORE="$(
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
)"

# Verificación transversal no mutante antes de cualquier add/commit/push.
"${BRANCH_HELPER}" verify "${OBJECTIVE_BRANCH}" || {
  echo "ERROR: Preflight transversal fallido; no se ejecutó add/commit/push." >&2
  exit 1
}

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

preflight_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"
  local name
  local remote_sha
  local local_sha

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
  [[ "$(git -C "${repository}" branch --show-current)" == "${OBJECTIVE_BRANCH}" ]] || {
    echo "ERROR: ${path}: branch temporal no activa" >&2
    return 1
  }
  [[ -z "$(git -C "${repository}" diff --name-only --diff-filter=U)" ]] || {
    echo "ERROR: ${path}: conflictos sin resolver" >&2
    return 1
  }
  git -C "${repository}" diff --check >/dev/null || {
    echo "ERROR: ${path}: git diff --check falló" >&2
    return 1
  }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || {
    echo "ERROR: ${path}: origin inexistente" >&2
    return 1
  }

  for name in \
    index.lock HEAD.lock packed-refs.lock \
    MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${name}")" ]] || {
      echo "ERROR: ${path}: operación Git activa (${name})" >&2
      return 1
    }
  done

  remote_sha="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
  local_sha="$(git -C "${repository}" rev-parse HEAD)"
  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    if [[ -n "${remote_sha}" ]] && git -C "${repository}" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
      git -C "${repository}" push --dry-run origin \
        "HEAD:refs/heads/${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
        echo "ERROR: ${path}: branch temporal no publicable" >&2
        return 1
      }
    else
      git -C "${repository}" push --dry-run --set-upstream origin \
        "${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
        echo "ERROR: ${path}: primera publicación no disponible" >&2
        return 1
      }
    fi
  elif [[ -z "${remote_sha}" ]]; then
    git -C "${repository}" push --dry-run --set-upstream origin \
      "${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
      echo "ERROR: ${path}: primera publicación no disponible" >&2
      return 1
    }
  elif [[ "${remote_sha}" != "${local_sha}" ]]; then
    if git -C "${repository}" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
      git -C "${repository}" push --dry-run origin \
        "HEAD:refs/heads/${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
        echo "ERROR: ${path}: branch temporal no publicable" >&2
        return 1
      }
    else
      git -C "${repository}" push --dry-run --set-upstream origin \
        "${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
        echo "ERROR: ${path}: primera publicación no disponible" >&2
        return 1
      }
    fi
  fi
}

failed=0
while IFS= read -r path; do
  [[ -z "${path}" ]] || preflight_repository "${path}" || failed=1
done < "${REPOSITORIES}"

[[ "${failed}" == "0" ]] || {
  echo "ERROR: Preflight transversal fallido; no se ejecutó add/commit/push." >&2
  exit 1
}

publish_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"
  local remote_sha
  local local_sha
  local has_upstream=0

  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    git -C "${repository}" add .
    if ! git -C "${repository}" diff --cached --quiet; then
      git -C "${repository}" commit -m "${COMMIT_MESSAGE}"
    fi
  fi

  if git -C "${repository}" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
    has_upstream=1
  fi
  remote_sha="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
  local_sha="$(git -C "${repository}" rev-parse HEAD)"

  if [[ -z "${remote_sha}" ]]; then
    git -C "${repository}" push --set-upstream origin "${OBJECTIVE_BRANCH}"
  elif [[ "${remote_sha}" != "${local_sha}" ]]; then
    if [[ "${has_upstream}" == "1" ]]; then
      git -C "${repository}" push origin "${OBJECTIVE_BRANCH}"
    else
      git -C "${repository}" push --set-upstream origin "${OBJECTIVE_BRANCH}"
    fi
  elif [[ "${has_upstream}" != "1" ]]; then
    git -C "${repository}" config "branch.${OBJECTIVE_BRANCH}.remote" origin
    git -C "${repository}" config "branch.${OBJECTIVE_BRANCH}.merge" "refs/heads/${OBJECTIVE_BRANCH}"
  fi
}

while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  publish_repository "${path}"
done < "${REPOSITORIES}"

postflight_failed=0
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  [[ "$(git -C "${repository}" branch --show-current)" == "${OBJECTIVE_BRANCH}" ]] || {
    echo "ERROR: ${path}: no permaneció en ${OBJECTIVE_BRANCH}" >&2
    postflight_failed=1
    continue
  }
  git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}" || {
    echo "ERROR: ${path}: branch temporal local inexistente" >&2
    postflight_failed=1
  }
  git -C "${repository}" show-ref --verify --quiet "refs/heads/main" || {
    echo "ERROR: ${path}: main local inexistente" >&2
    postflight_failed=1
  }
  remote_sha="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
  [[ -n "${remote_sha}" ]] || {
    echo "ERROR: ${path}: branch temporal remota inexistente" >&2
    postflight_failed=1
    continue
  }
  [[ "${remote_sha}" == "$(git -C "${repository}" rev-parse HEAD)" ]] || {
    echo "ERROR: ${path}: HEAD no coincide con origin/${OBJECTIVE_BRANCH}" >&2
    postflight_failed=1
  }
done < "${REPOSITORIES}"

[[ "${postflight_failed}" == "0" ]] || {
  echo "ERROR: Postflight transversal fallido." >&2
  exit 1
}

LIFECYCLE_AFTER="$(
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
)"
[[ "${LIFECYCLE_BEFORE}" == "${LIFECYCLE_AFTER}" ]] || {
  echo "ERROR: el estado lifecycle del objetivo cambió durante git publish" >&2
  exit 1
}

echo "Checkpoint publicado para ${OBJECTIVE_ID} en ${OBJECTIVE_BRANCH}; repositorios permanecen en la branch temporal."
