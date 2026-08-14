#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == "0" ]] || { echo "Uso: ./QA/qa-context.sh" >&2; exit 2; }

QA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${QA_DIR}/.." && pwd)"
OUTPUT_DIR="${QA_DIR}/output"
LOG_FILE="${OUTPUT_DIR}/context-qa.log"
RESULT_FILE="${OUTPUT_DIR}/context-qa-results.md"
mkdir -p "${OUTPUT_DIR}"
rm -f "${LOG_FILE}" "${RESULT_FILE}"
started_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

set +e
(
  set -euo pipefail
  cd "${CONTEXT_ROOT}"
  echo "1/3 Python unit/regression tests"
  test_count=0
  while IFS= read -r test_file; do
    test_count=$((test_count + 1))
    echo "Running ${test_file}"
    python3 -m unittest "${test_file}"
  done < <(find scripts/tests -maxdepth 1 -type f -name 'test_*.py' | sort)
  [[ "${test_count}" -gt 0 ]] || { echo "ERROR: No se encontraron scripts/tests/test_*.py" >&2; exit 1; }

  echo "2/3 Python syntax"
  while IFS= read -r file; do
    python3 -m py_compile "${file}"
  done < <(find scripts -type f -name '*.py' -not -path '*/__pycache__/*' | sort)

  echo "3/3 Bash syntax"
  while IFS= read -r file; do
    bash -n "${file}"
  done < <(find scripts QA -type f -name '*.sh' | sort)
) 2>&1 | tee "${LOG_FILE}"
status=${PIPESTATUS[0]}
set -e
finished_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

{
  echo "# Context QA"
  echo
  echo "- Scope: \`SBM-SUITE/context\`"
  echo "- SonarQube: not used"
  echo "- Started: \`${started_at}\`"
  echo "- Finished: \`${finished_at}\`"
  echo "- Exit code: \`${status}\`"
  if [[ "${status}" == "0" ]]; then
    echo "- Overall status: passed"
  else
    echo "- Overall status: failed"
  fi
  echo "- Log: \`QA/output/context-qa.log\`"
} > "${RESULT_FILE}"

if [[ "${status}" != "0" ]]; then
  echo "ERROR: QA de Context falló (exit ${status})" >&2
  exit "${status}"
fi

echo "Evidencia: QA/output/context-qa-results.md"
echo "QA de Context completado correctamente."
