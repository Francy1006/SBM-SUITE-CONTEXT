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

[[ -x "${REPOSITORY_HELPER}" || -f "${REPOSITORY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/suite-repositories.py" >&2
  exit 1
}

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

printf '%-50s %s\n' "REPOSITORY" "BRANCH"
printf '%-50s %s\n' "--------------------------------------------------" "------------------------------"

while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  branch="$(git -C "${repository}" branch --show-current)"
  [[ -n "${branch}" ]] || branch="DETACHED_HEAD"
  printf '%-50s %s\n' "${relative_path}" "${branch}"
done < "${REPOSITORIES}"
