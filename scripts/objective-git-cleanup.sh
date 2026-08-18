#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ge "2" ]] || { echo "Uso: ./scripts/objective-git-cleanup.sh <objective-id>... <objective-branch>" >&2; exit 1; }
OBJECTIVE_COUNT=$(( $# - 1 ))
OBJECTIVE_IDS=("${@:1:${OBJECTIVE_COUNT}}")
OBJECTIVE_BRANCH="${!#}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
python3 "${SCRIPT_DIR}/git-flow-policy.py" describe "${OBJECTIVE_BRANCH}" >/dev/null
python3 "${SCRIPT_DIR}/objective-git-state.py" --branch "${OBJECTIVE_BRANCH}" \
  --project-context "${CONTEXT_ROOT}/PROJECT_CONTEXT.md" \
  --completed-objectives "${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md" \
  "${OBJECTIVE_IDS[@]}"

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${SCRIPT_DIR}/suite-repositories.py" list-paths > "${REPOSITORIES}"

preflight_repository() {
  local path="$1" repository="${SUITE_ROOT}/$1" local_main remote_objective name occupied
  [[ -z "$(git -C "${repository}" status --porcelain)" ]] || { echo "ERROR: ${path}: working tree contiene cambios" >&2; return 1; }
  [[ "$(git -C "${repository}" branch --show-current)" == "main" ]] || { echo "ERROR: ${path}: branch actual no es main" >&2; return 1; }
  git -C "${repository}" fetch origin "+refs/heads/main:refs/remotes/origin/main" >/dev/null 2>&1 || return 1
  local_main="$(git -C "${repository}" rev-parse main)"
  [[ "${local_main}" == "$(git -C "${repository}" rev-parse origin/main)" ]] || { echo "ERROR: ${path}: main no está sincronizada con origin" >&2; return 1; }
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    git -C "${repository}" merge-base --is-ancestor "${OBJECTIVE_BRANCH}" main || { echo "ERROR: ${path}: ${OBJECTIVE_BRANCH} no está integrada en main" >&2; return 1; }
  fi
  remote_objective="$(git -C "${repository}" ls-remote origin "refs/heads/${OBJECTIVE_BRANCH}" | awk '{print $1}')"
  if [[ -n "${remote_objective}" ]]; then
    git -C "${repository}" fetch origin "+refs/heads/${OBJECTIVE_BRANCH}:refs/remotes/origin/${OBJECTIVE_BRANCH}" >/dev/null 2>&1 || return 1
    git -C "${repository}" merge-base --is-ancestor "origin/${OBJECTIVE_BRANCH}" main || { echo "ERROR: ${path}: origin/${OBJECTIVE_BRANCH} no está integrada en main" >&2; return 1; }
  fi
  occupied="$(git -C "${repository}" worktree list --porcelain | awk '/^branch refs\/heads\// {sub(/^branch refs\/heads\//, ""); print}')"
  grep -Fxq "${OBJECTIVE_BRANCH}" <<< "${occupied}" && { echo "ERROR: ${path}: branch temporal ocupada por worktree" >&2; return 1; }
  for name in index.lock HEAD.lock packed-refs.lock MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "${repository}" rev-parse --git-path "${name}")" ]] || { echo "ERROR: ${path}: operación Git activa (${name})" >&2; return 1; }
  done
}

failed=0
while IFS= read -r path; do [[ -z "${path}" ]] || preflight_repository "${path}" || failed=1; done < "${REPOSITORIES}"
[[ "${failed}" == "0" ]] || { echo "ERROR: Preflight de cleanup fallido; no se eliminó ninguna branch." >&2; exit 1; }
while IFS= read -r path; do
  [[ -n "${path}" ]] || continue
  repository="${SUITE_ROOT}/${path}"
  if git -C "${repository}" show-ref --verify --quiet "refs/heads/${OBJECTIVE_BRANCH}"; then
    git -C "${repository}" branch -d "${OBJECTIVE_BRANCH}"
  fi
  if git -C "${repository}" ls-remote --exit-code origin "refs/heads/${OBJECTIVE_BRANCH}" >/dev/null 2>&1; then
    git -C "${repository}" push origin --delete "${OBJECTIVE_BRANCH}"
  fi
done < "${REPOSITORIES}"
echo "Cleanup transversal completado para ${OBJECTIVE_COUNT} objetivo(s); repositorios en main."
