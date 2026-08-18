#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/repos-branches.sh
USAGE
}

[[ "$#" == "0" ]] || {
  usage >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"
POLICY_HELPER="${SCRIPT_DIR}/git-flow-policy.py"

[[ -x "${REPOSITORY_HELPER}" || -f "${REPOSITORY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/suite-repositories.py" >&2
  exit 1
}

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

printf '%-40s %-42s %s\n' "REPOSITORY" "BRANCH" "GIT FLOW ROLE"
printf '%-40s %-42s %s\n' "----------------------------------------" "------------------------------------------" "--------------------"

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  branch="$(git -C "${repository}" branch --show-current)"
  [[ -n "${branch}" ]] || branch="DETACHED_HEAD"
  case "${branch}" in
    main) role="stable/release" ;;
    FEATURE-*|BUGFIX-*|HOTFIX-*|RELEASE-*)
      if policy="$(python3 "${POLICY_HELPER}" describe "${branch}" --format tsv 2>/dev/null)"; then
        IFS=$'\t' read -r branch_type base integration _ _ _ <<< "${policy}"
        role="${branch_type}: ${base}->${integration}"
      else
        role="invalid objective branch"
      fi
      ;;
    *) role="non-canonical" ;;
  esac
  printf '%-40s %-42s %s\n' "${relative_path}" "${branch}" "${role}"
done < "${REPOSITORIES}"
