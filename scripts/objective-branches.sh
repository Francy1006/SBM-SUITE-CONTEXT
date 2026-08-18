#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Uso:
  ./scripts/objective-branches.sh prepare <objective-branch>
  ./scripts/objective-branches.sh verify <objective-branch>
EOF
}

[[ "$#" == "2" ]] || { usage >&2; exit 1; }
MODE="$1"
OBJECTIVE_BRANCH="$2"
case "${MODE}" in prepare|verify) ;; *) echo "ERROR: Modo no soportado: ${MODE}" >&2; usage >&2; exit 1 ;; esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"
POLICY_HELPER="${SCRIPT_DIR}/git-flow-policy.py"
[[ -f "${REPOSITORY_HELPER}" ]] || { echo "ERROR: No existe scripts/suite-repositories.py" >&2; exit 1; }
[[ -f "${POLICY_HELPER}" ]] || { echo "ERROR: No existe scripts/git-flow-policy.py" >&2; exit 1; }
IFS=$'\t' read -r _ BASE_BRANCH _ _ _ _ < <(python3 "${POLICY_HELPER}" describe "${OBJECTIVE_BRANCH}" --format tsv)
[[ "${BASE_BRANCH}" == "main" ]] || { echo "ERROR: La política temporal debe nacer desde main" >&2; exit 1; }

REPOSITORY_LIST="$(mktemp)"
BRANCH_PLAN="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}" "${BRANCH_PLAN}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORY_LIST}"

git_state_guard() {
  local repository="$1" relative_path="$2" name
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || { echo "ERROR: ${relative_path}: working tree contiene cambios locales" >&2; return 1; }
  for name in index.lock HEAD.lock packed-refs.lock MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${name}")" ]] || { echo "ERROR: ${relative_path}: bloqueo u operación Git activa (${name})" >&2; return 1; }
  done
}

preflight_repository() {
  local relative_path="$1" repository="${SUITE_ROOT}/$1" current_branch target_source remote_target occupied
  [[ -d "${repository}" ]] || { echo "ERROR: ${relative_path}: directorio inexistente" >&2; return 1; }
  [[ "$(git -C "${repository}" rev-parse --show-toplevel 2>/dev/null)" == "$(cd "${repository}" && pwd -P)" ]] || { echo "ERROR: ${relative_path}: el path registrado no es la raíz Git" >&2; return 1; }
  git_state_guard "${repository}" "${relative_path}" || return 1
  git -C "${repository}" show-ref --verify --quiet refs/heads/main || { echo "ERROR: ${relative_path}: branch local main inexistente" >&2; return 1; }
  git -C "${repository}" remote get-url origin >/dev/null 2>&1 || { echo "ERROR: ${relative_path}: remote origin inexistente" >&2; return 1; }
  git -C "${repository}" fetch origin "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || { echo "ERROR: ${relative_path}: no se pudo actualizar origin/main" >&2; return 1; }
  if ! git -C "${repository}" merge-base --is-ancestor main origin/main && ! git -C "${repository}" merge-base --is-ancestor origin/main main; then
    echo "ERROR: ${relative_path}: main diverge de origin/main" >&2; return 1
  fi
  current_branch="$(git -C "${repository}" branch --show-current)"
  occupied="$(git -C "${repository}" worktree list --porcelain | awk '/^branch refs\/heads\// {sub(/^branch refs\/heads\//, ""); print}')"
  if [[ "${current_branch}" != "main" ]] && grep -Fxq "main" <<< "${occupied}"; then
    echo "ERROR: ${relative_path}: main está ocupada por otro worktree" >&2; return 1
  fi
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    target_source="local"
    if [[ "${current_branch}" != "${OBJECTIVE_BRANCH}" ]] && grep -Fxq "${OBJECTIVE_BRANCH}" <<< "${occupied}"; then
      echo "ERROR: ${relative_path}: ${OBJECTIVE_BRANCH} está ocupada por otro worktree" >&2; return 1
    fi
  else
    remote_target="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
    [[ -z "${remote_target}" ]] && target_source="new" || target_source="remote"
  fi
  printf '%s\t%s\n' "${relative_path}" "${target_source}" >> "${BRANCH_PLAN}"
}

verify_repository() {
  local relative_path="$1" repository="${SUITE_ROOT}/$1" current
  current="$(git -C "${repository}" branch --show-current 2>/dev/null || true)"
  [[ "${current}" == "${OBJECTIVE_BRANCH}" ]] || { echo "ERROR: ${relative_path}: branch actual '${current:-detached HEAD}', esperada '${OBJECTIVE_BRANCH}'" >&2; return 1; }
}

if [[ "${MODE}" == "verify" ]]; then
  failed=0
  while IFS= read -r path; do [[ -z "${path}" ]] || verify_repository "${path}" || failed=1; done < "${REPOSITORY_LIST}"
  [[ "${failed}" == "0" ]] || exit 1
  echo "Branches verificadas en todos los repositorios SBM: ${OBJECTIVE_BRANCH}"
  exit 0
fi

failed=0
while IFS= read -r path; do [[ -z "${path}" ]] || preflight_repository "${path}" || failed=1; done < "${REPOSITORY_LIST}"
[[ "${failed}" == "0" ]] || { echo "ERROR: Preflight global fallido; no se modificó ninguna branch." >&2; exit 1; }

while IFS=$'\t' read -r path target_source; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  git -C "${repository}" checkout main
  git -C "${repository}" pull --ff-only origin main
  case "${target_source}" in
    local) git -C "${repository}" checkout "${OBJECTIVE_BRANCH}" ;;
    remote) git -C "${repository}" fetch origin "refs/heads/${OBJECTIVE_BRANCH}:refs/remotes/origin/${OBJECTIVE_BRANCH}"; git -C "${repository}" checkout --track "origin/${OBJECTIVE_BRANCH}" ;;
    new) git -C "${repository}" checkout -b "${OBJECTIVE_BRANCH}" main ;;
    *) echo "ERROR: ${path}: plan de branch inválido" >&2; exit 1 ;;
  esac
done < "${BRANCH_PLAN}"

failed=0
while IFS= read -r path; do [[ -z "${path}" ]] || verify_repository "${path}" || failed=1; done < "${REPOSITORY_LIST}"
[[ "${failed}" == "0" ]] || { echo "ERROR: Preparación transversal inconsistente." >&2; exit 1; }
echo "Branches preparadas desde main: ${OBJECTIVE_BRANCH}"
