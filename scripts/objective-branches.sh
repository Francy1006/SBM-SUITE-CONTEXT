#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Uso:
  ./scripts/objective-branches.sh prepare <objective-branch>
  ./scripts/objective-branches.sh verify <objective-branch>
EOF
}

[[ "$#" == "2" ]] || {
  usage >&2
  exit 1
}

MODE="$1"
OBJECTIVE_BRANCH="$2"

case "${MODE}" in
  prepare|verify) ;;
  *)
    echo "ERROR: Modo no soportado: ${MODE}" >&2
    usage >&2
    exit 1
    ;;
esac

git check-ref-format --branch "${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || {
  echo "ERROR: Branch de objetivo inválida: ${OBJECTIVE_BRANCH}" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"

[[ -x "${REPOSITORY_HELPER}" || -f "${REPOSITORY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/suite-repositories.py" >&2
  exit 1
}

REPOSITORY_LIST="$(mktemp)"
BRANCH_PLAN="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}" "${BRANCH_PLAN}"' EXIT

python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORY_LIST}"

preflight_repository() {
  local relative_path="$1"
  local repository="${SUITE_ROOT}/${relative_path}"
  local git_root
  local lock_name
  local target_ref
  local target_source
  local current_branch
  local occupied_branches

  [[ -d "${repository}" ]] || {
    echo "ERROR: ${relative_path}: directorio inexistente" >&2
    return 1
  }
  git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: no es un repositorio Git válido" >&2
    return 1
  }
  git_root="$(git -C "${repository}" rev-parse --show-toplevel)" || {
    echo "ERROR: ${relative_path}: no se pudo resolver la raíz Git" >&2
    return 1
  }
  [[ "${git_root}" == "$(cd "${repository}" && pwd -P)" ]] || {
    echo "ERROR: ${relative_path}: el path registrado no es la raíz del repositorio" >&2
    return 1
  }
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || {
    echo "ERROR: ${relative_path}: working tree contiene cambios locales" >&2
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
  git -C "${repository}" ls-remote --exit-code origin refs/heads/main \
    >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: origin/main inexistente o inaccesible" >&2
    return 1
  }
  git -C "${repository}" fetch origin \
    "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: no se pudo actualizar evidencia de origin/main" >&2
    return 1
  }
  if ! git -C "${repository}" merge-base --is-ancestor main origin/main \
    && ! git -C "${repository}" merge-base --is-ancestor origin/main main; then
    echo "ERROR: ${relative_path}: main diverge de origin/main e impide pull --ff-only" >&2
    return 1
  fi
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
  current_branch="$(git -C "${repository}" branch --show-current)"
  occupied_branches="$(
    git -C "${repository}" worktree list --porcelain \
      | awk '/^branch refs\/heads\// {sub(/^branch refs\/heads\//, ""); print}'
  )"
  if [[ "${current_branch}" != "main" ]] \
    && grep -Fxq "main" <<< "${occupied_branches}"; then
    echo "ERROR: ${relative_path}: main está ocupada por otro worktree" >&2
    return 1
  fi
  if git -C "${repository}" show-ref --verify --quiet \
    "refs/heads/${OBJECTIVE_BRANCH}"; then
    if [[ "${current_branch}" != "${OBJECTIVE_BRANCH}" ]] \
      && grep -Fxq "${OBJECTIVE_BRANCH}" <<< "${occupied_branches}"; then
      echo "ERROR: ${relative_path}: ${OBJECTIVE_BRANCH} está ocupada por otro worktree" >&2
      return 1
    fi
    target_source="local"
  else
    if ! target_ref="$(
      git -C "${repository}" ls-remote origin \
        "refs/heads/${OBJECTIVE_BRANCH}"
    )"; then
      echo "ERROR: ${relative_path}: no se pudo consultar origin" >&2
      return 1
    fi
    if [[ -n "${target_ref}" ]]; then
      target_source="remote"
    else
      target_source="new"
    fi
  fi
  printf '%s\t%s\n' "${relative_path}" "${target_source}" >> "${BRANCH_PLAN}"
}

verify_repository() {
  local relative_path="$1"
  local repository="${SUITE_ROOT}/${relative_path}"
  local current_branch
  local git_root

  [[ -d "${repository}" ]] || {
    echo "ERROR: ${relative_path}: directorio inexistente" >&2
    return 1
  }
  git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "ERROR: ${relative_path}: no es un repositorio Git válido" >&2
    return 1
  }
  git_root="$(git -C "${repository}" rev-parse --show-toplevel)" || {
    echo "ERROR: ${relative_path}: no se pudo resolver la raíz Git" >&2
    return 1
  }
  [[ "${git_root}" == "$(cd "${repository}" && pwd -P)" ]] || {
    echo "ERROR: ${relative_path}: el path registrado no es la raíz del repositorio" >&2
    return 1
  }
  current_branch="$(git -C "${repository}" branch --show-current)"
  [[ "${current_branch}" == "${OBJECTIVE_BRANCH}" ]] || {
    echo "ERROR: ${relative_path}: branch actual '${current_branch:-detached HEAD}', esperada '${OBJECTIVE_BRANCH}'" >&2
    return 1
  }
}

if [[ "${MODE}" == "verify" ]]; then
  verification_failed=0
  while IFS= read -r relative_path; do
    [[ -n "${relative_path}" ]] || continue
    verify_repository "${relative_path}" || verification_failed=1
  done < "${REPOSITORY_LIST}"
  [[ "${verification_failed}" == "0" ]] || exit 1
  echo "Branches verificadas en todos los repositorios SBM: ${OBJECTIVE_BRANCH}"
  exit 0
fi

preflight_failed=0
while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  preflight_repository "${relative_path}" || preflight_failed=1
done < "${REPOSITORY_LIST}"

[[ "${preflight_failed}" == "0" ]] || {
  echo "ERROR: Preflight global fallido; no se modificó ninguna branch." >&2
  exit 1
}

while IFS=$'\t' read -r relative_path target_source; do
  [[ -n "${relative_path}" && -n "${target_source}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  git -C "${repository}" checkout main
  git -C "${repository}" pull --ff-only origin main
  case "${target_source}" in
    local)
      git -C "${repository}" checkout "${OBJECTIVE_BRANCH}"
      ;;
    remote)
      git -C "${repository}" fetch origin \
        "refs/heads/${OBJECTIVE_BRANCH}:refs/remotes/origin/${OBJECTIVE_BRANCH}"
      git -C "${repository}" checkout --track \
        "origin/${OBJECTIVE_BRANCH}"
      ;;
    new)
      git -C "${repository}" checkout -b "${OBJECTIVE_BRANCH}" main
      ;;
    *)
      echo "ERROR: ${relative_path}: plan de branch inválido" >&2
      exit 1
      ;;
  esac
done < "${BRANCH_PLAN}"

verification_failed=0
while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  verify_repository "${relative_path}" || verification_failed=1
done < "${REPOSITORY_LIST}"
[[ "${verification_failed}" == "0" ]] || {
  echo "ERROR: La preparación transversal terminó con branches inconsistentes." >&2
  exit 1
}

echo "Branches preparadas en todos los repositorios SBM: ${OBJECTIVE_BRANCH}"
