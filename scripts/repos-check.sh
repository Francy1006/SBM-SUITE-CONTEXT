#!/usr/bin/env bash
set -uo pipefail

[[ "$#" == "0" ]] || {
  echo "Uso: ./scripts/repos-check.sh" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for script in repos-branches.sh repos-changes.sh; do
  [[ -x "${SCRIPT_DIR}/${script}" || -f "${SCRIPT_DIR}/${script}" ]] || {
    echo "ERROR: No existe scripts/${script}" >&2
    exit 1
  }
done

result=0

echo "### 1/2 BRANCHES"
"${SCRIPT_DIR}/repos-branches.sh" || result=1

echo
echo "### 2/2 CAMBIOS"
"${SCRIPT_DIR}/repos-changes.sh" || result=1

exit "${result}"
