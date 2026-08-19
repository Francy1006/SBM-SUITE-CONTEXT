#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ge "2" ]] || {
  echo "Uso: ./scripts/objective-git-finalize.sh <objective-id>... <objective-branch>" >&2
  exit 1
}

OBJECTIVE_COUNT=$(( $# - 1 ))
OBJECTIVE_IDS=("${@:1:${OBJECTIVE_COUNT}}")
OBJECTIVE_BRANCH="${!#}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
PROJECT_CONTEXT_FILE="${CONTEXT_ROOT}/PROJECT_CONTEXT.md"
COMPLETED_OBJECTIVES_FILE="${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"
BRANCH_HELPER="${SCRIPT_DIR}/objective-branches.sh"
POLICY_HELPER="${SCRIPT_DIR}/git-flow-policy.py"
OBJECTIVE_STATE_HELPER="${SCRIPT_DIR}/objective-git-state.py"
WORKFLOW_STATE_HELPER="${SCRIPT_DIR}/workflow-state.py"
CLEANUP_HELPER="${SCRIPT_DIR}/objective-git-cleanup.sh"
QA_GATE_FILE="${CONTEXT_ROOT}/QA/output/finalization-gate.json"
DOCUMENTATION_GATE_FILE="${CONTEXT_ROOT}/documentation/output/finalization-gate.json"

for required_file in \
  "${PROJECT_CONTEXT_FILE}" \
  "${COMPLETED_OBJECTIVES_FILE}" \
  "${REPOSITORY_HELPER}" \
  "${BRANCH_HELPER}" \
  "${POLICY_HELPER}" \
  "${OBJECTIVE_STATE_HELPER}" \
  "${WORKFLOW_STATE_HELPER}" \
  "${CLEANUP_HELPER}"; do
  [[ -f "${required_file}" ]] || {
    echo "ERROR: archivo requerido inexistente: ${required_file}" >&2
    exit 1
  }
done

IFS=$'\t' read -r BRANCH_TYPE BASE_BRANCH INTEGRATION_BRANCH FINAL_BRANCH REQUIRES_QA REQUIRES_DOCUMENTATION < <(
  python3 "${POLICY_HELPER}" describe "${OBJECTIVE_BRANCH}" --format tsv
)
[[ "${BASE_BRANCH}" == "main" && "${INTEGRATION_BRANCH}" == "main" && "${FINAL_BRANCH}" == "main" ]] || {
  echo "ERROR: La política de finalización debe usar main exclusivamente" >&2
  exit 1
}

python3 "${OBJECTIVE_STATE_HELPER}" \
  --branch "${OBJECTIVE_BRANCH}" \
  --project-context "${PROJECT_CONTEXT_FILE}" \
  --completed-objectives "${COMPLETED_OBJECTIVES_FILE}" \
  "${OBJECTIVE_IDS[@]}"

[[ -f "${QA_GATE_FILE}" ]] || {
  echo "ERROR: QA gate inexistente: ${QA_GATE_FILE}" >&2
  exit 1
}
[[ -f "${DOCUMENTATION_GATE_FILE}" ]] || {
  echo "ERROR: Documentation gate inexistente: ${DOCUMENTATION_GATE_FILE}" >&2
  exit 1
}

DOCUMENTATION_STATE_SHA256="$(python3 - \
  "${QA_GATE_FILE}" \
  "${DOCUMENTATION_GATE_FILE}" \
  "${OBJECTIVE_BRANCH}" \
  "${OBJECTIVE_IDS[@]}" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

qa_path = Path(sys.argv[1])
doc_path = Path(sys.argv[2])
branch = sys.argv[3]
objective_ids = sys.argv[4:]


def load(path: Path, label: str) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {label} inválido: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"ERROR: {label} inválido: objeto JSON esperado")
    return payload


def require_common(payload: dict, label: str, expected_status: str) -> None:
    if payload.get("branch") != branch:
        raise SystemExit(
            f"ERROR: {label}.branch={payload.get('branch')!r}; esperado {branch!r}"
        )
    if payload.get("status") != expected_status:
        raise SystemExit(
            f"ERROR: {label}.status={payload.get('status')!r}; esperado {expected_status!r}"
        )
    if payload.get("objectives") != objective_ids:
        raise SystemExit(
            f"ERROR: {label}.objectives no coincide con el batch ordenado solicitado"
        )
    digest = payload.get("state_sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise SystemExit(f"ERROR: {label}.state_sha256 inválido")


qa = load(qa_path, "QA gate")
require_common(qa, "QA gate", "passed")
if qa.get("mode") != "full-suite-with-sonar":
    raise SystemExit("ERROR: QA gate.mode debe ser full-suite-with-sonar")

doc = load(doc_path, "Documentation gate")
require_common(doc, "Documentation gate", "updated")
print(doc["state_sha256"])
PY
)"

python3 "${WORKFLOW_STATE_HELPER}" \
  --suite-root "${SUITE_ROOT}" \
  --repository-helper "${REPOSITORY_HELPER}" \
  --scope documentation \
  --expect "${DOCUMENTATION_STATE_SHA256}" >/dev/null

# Verificación transversal antes de cualquier add/commit/push/merge/checkout a main.
"${BRANCH_HELPER}" verify "${OBJECTIVE_BRANCH}"

REPOSITORIES="$(mktemp)"
CHANGED_REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}" "${CHANGED_REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

preflight_repository() {
  local path="$1"
  local repository="${SUITE_ROOT}/$1"
  local name
  local occupied
  local remote_main

  [[ -d "${repository}" ]] || {
    echo "ERROR: ${path}: directorio inexistente" >&2
    return 1
  }
  git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "ERROR: ${path}: no es un repositorio Git válido" >&2
    return 1
  }
  [[ "$(git -C "${repository}" rev-parse --show-toplevel)" == "$(cd "${repository}" && pwd -P)" ]] || {
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
  git -C "${repository}" show-ref --verify --quiet refs/heads/main || {
    echo "ERROR: ${path}: main inexistente" >&2
    return 1
  }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || {
    echo "ERROR: ${path}: origin inexistente" >&2
    return 1
  }
  remote_main="$(git -C "${repository}" ls-remote origin refs/heads/main | awk '{print $1}')"
  [[ -n "${remote_main}" ]] || {
    echo "ERROR: ${path}: origin/main inexistente" >&2
    return 1
  }
  git -C "${repository}" fetch origin \
    "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || {
    echo "ERROR: ${path}: no se pudo actualizar origin/main" >&2
    return 1
  }
  git -C "${repository}" merge-base --is-ancestor main origin/main || {
    echo "ERROR: ${path}: main local no admite fast-forward" >&2
    return 1
  }

  occupied="$(
    git -C "${repository}" worktree list --porcelain \
      | awk '/^branch refs\/heads\// {sub(/^branch refs\/heads\//, ""); print}'
  )"
  grep -Fxq "main" <<< "${occupied}" && {
    echo "ERROR: ${path}: main ocupada por otro worktree" >&2
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

  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    printf '%s\n' "${path}" >> "${CHANGED_REPOSITORIES}"
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
  echo "ERROR: Preflight transversal fallido; no se ejecutó add/commit/push/merge." >&2
  exit 1
}

COMMIT_MESSAGE="chore: finalize transversal objective batch"
MERGE_MESSAGE="merge: finalize transversal objective batch"

# Solo los repositorios con cambios reales reciben commit y publicación de la branch.
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"

  git -C "${repository}" add .
  if ! git -C "${repository}" diff --cached --quiet; then
    git -C "${repository}" commit -m "${COMMIT_MESSAGE}"
  fi

  if git -C "${repository}" rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
    git -C "${repository}" push origin "${OBJECTIVE_BRANCH}"
  else
    git -C "${repository}" push --set-upstream origin "${OBJECTIVE_BRANCH}"
  fi
done < "${CHANGED_REPOSITORIES}"

# Todos los repositorios terminan en main; solo los modificados hacen merge/push.
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"

  git -C "${repository}" checkout main
  git -C "${repository}" pull --ff-only origin main

  if grep -Fxq "${path}" "${CHANGED_REPOSITORIES}"; then
    git -C "${repository}" merge --no-ff "${OBJECTIVE_BRANCH}" -m "${MERGE_MESSAGE}"
    git -C "${repository}" push origin main
  fi

done < "${REPOSITORIES}"

# Verificación final antes del cleanup transversal integrado.
postflight_failed=0
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  [[ "$(git -C "${repository}" branch --show-current)" == "main" ]] || {
    echo "ERROR: ${path}: no terminó en main" >&2
    postflight_failed=1
    continue
  }
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || {
    echo "ERROR: ${path}: working tree no quedó limpio" >&2
    postflight_failed=1
  }
  git -C "${repository}" fetch origin \
    "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || {
    echo "ERROR: ${path}: no se pudo verificar origin/main" >&2
    postflight_failed=1
    continue
  }
  [[ "$(git -C "${repository}" rev-parse main)" == "$(git -C "${repository}" rev-parse origin/main)" ]] || {
    echo "ERROR: ${path}: main no quedó sincronizada con origin/main" >&2
    postflight_failed=1
  }
done < "${REPOSITORIES}"

[[ "${postflight_failed}" == "0" ]] || {
  echo "ERROR: Postflight transversal fallido." >&2
  exit 1
}

"${CLEANUP_HELPER}" "${OBJECTIVE_IDS[@]}" "${OBJECTIVE_BRANCH}"

echo "Finalización transversal completada para ${OBJECTIVE_COUNT} objetivo(s) (${BRANCH_TYPE}); repositorios en main y branch temporal eliminada."
