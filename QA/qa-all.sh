#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./QA/qa-all.sh [--without-sonar]
  ./QA/qa-all.sh --with-sonar --sonarqube-ready
USAGE
}

MODE="without-sonar"
SONAR_READY=0
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --without-sonar)
      MODE="without-sonar"
      ;;
    --with-sonar)
      MODE="with-sonar"
      ;;
    --sonarqube-ready)
      SONAR_READY=1
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "${MODE}" == "without-sonar" && "${SONAR_READY}" == "1" ]]; then
  echo "ERROR: --sonarqube-ready solo es válido con --with-sonar" >&2
  exit 2
fi
if [[ "${MODE}" == "with-sonar" && "${SONAR_READY}" != "1" ]]; then
  echo "ERROR: confirme SonarQube con --sonarqube-ready antes de ejecutar QA con Sonar" >&2
  exit 2
fi

QA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${QA_DIR}/.." && pwd)"
REPOSITORY_HELPER="${CONTEXT_ROOT}/scripts/suite-repositories.py"
OUTPUT_DIR="${QA_DIR}/output"
REPOSITORY_LIST="$(mktemp)"
trap 'rm -f "${REPOSITORY_LIST}"' EXIT

python3 "${REPOSITORY_HELPER}" list > "${REPOSITORY_LIST}"
mkdir -p "${OUTPUT_DIR}"
mode_slug="$(printf '%s' "${MODE}" | tr -cd '[:alnum:]-')"
SUMMARY="${OUTPUT_DIR}/qa-all-${mode_slug}-results.md"
QUEUE="${OUTPUT_DIR}/qa-all-${mode_slug}-queue.tsv"

{
  echo -e "project\trepository\tmode\tstatus\texit_code"
} > "${QUEUE}"
{
  echo "# QA transversal"
  echo
  echo "- Mode: \`${MODE}\`"
  if [[ "${MODE}" == "with-sonar" ]]; then
    echo "- Execution: sequential queue"
  fi
  echo
  echo "| Project | Repository | Status | Evidence |"
  echo "|---|---|---|---|"
} > "${SUMMARY}"

failed=0
executed=0
skipped=0
while IFS=$'\t' read -r project relative_path; do
  [[ -n "${relative_path}" ]] || continue
  if [[ "${relative_path}" == "context" ]]; then
    continue
  fi

  args=("${relative_path}")
  if [[ "${MODE}" == "with-sonar" ]]; then
    args+=(--with-sonar --sonarqube-ready)
  else
    args+=(--without-sonar)
  fi

  echo "Cola QA: ${relative_path} (${MODE})"
  set +e
  "${QA_DIR}/qa-project.sh" "${args[@]}" </dev/null
  status=$?
  set -e

  slug="$(printf '%s' "${relative_path}" | tr '/[:space:]' '--' | tr -cd '[:alnum:]_.-')"
  evidence="QA/output/${slug}-${mode_slug}-qa-results.md"
  if [[ "${status}" == "0" ]]; then
    result="passed"
    queue_status="passed"
    executed=$((executed + 1))
  elif [[ "${status}" == "3" ]]; then
    evidence="N/A"
    if [[ "${MODE}" == "without-sonar" ]]; then
      result="not-configured"
      queue_status="failed"
      failed=1
    else
      result="not-applicable"
      queue_status="skipped"
      skipped=$((skipped + 1))
    fi
  else
    result="failed (${status})"
    queue_status="failed"
    failed=1
    executed=$((executed + 1))
    [[ -f "${OUTPUT_DIR}/${slug}-${mode_slug}-qa-results.md" ]] || evidence="N/A"
  fi

  printf '%s\t%s\t%s\t%s\t%s\n' "${project}" "${relative_path}" "${MODE}" "${queue_status}" "${status}" >> "${QUEUE}"
  printf '| %s | `%s` | %s | `%s` |\n' "${project}" "${relative_path}" "${result}" "${evidence}" >> "${SUMMARY}"
done < "${REPOSITORY_LIST}"

{
  echo
  echo "Executed: ${executed}"
  echo "Skipped: ${skipped}"
  echo "Queue: \`QA/output/$(basename "${QUEUE}")\`"
} >> "${SUMMARY}"

if [[ "${executed}" == "0" ]]; then
  echo "ERROR: No se ejecutó ningún QA aplicable" >&2
  exit 1
fi

echo "Resumen transversal: QA/output/$(basename "${SUMMARY}")"
echo "Cola: QA/output/$(basename "${QUEUE}")"
[[ "${failed}" == "0" ]] || { echo "ERROR: Uno o más proyectos fallaron o no están configurados para el modo solicitado" >&2; exit 1; }
echo "QA transversal completado correctamente (${MODE})."
