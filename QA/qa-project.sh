#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./QA/qa-project.sh <project-or-repository> [--without-sonar]
  ./QA/qa-project.sh <project-or-repository> --with-sonar --sonarqube-ready
USAGE
}

[[ "$#" -ge 1 && "$#" -le 3 ]] || { usage >&2; exit 2; }
SELECTOR="$1"
shift
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
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
REPOSITORY_HELPER="${CONTEXT_ROOT}/scripts/suite-repositories.py"
OUTPUT_DIR="${QA_DIR}/output"

[[ -x "${REPOSITORY_HELPER}" ]] || { echo "ERROR: No existe scripts/suite-repositories.py ejecutable" >&2; exit 2; }
relative_path="$(python3 "${REPOSITORY_HELPER}" resolve "${SELECTOR}")"
if [[ "${relative_path}" == "context" ]]; then
  echo "ERROR: Para SBM-SUITE/context use ./QA/qa-context.sh" >&2
  exit 3
fi
repository="${SUITE_ROOT}/${relative_path}"
qa_check="${repository}/scripts/qa-check.sh"

references_sonar() {
  local file="$1"
  grep -Eiq 'sonar(qube|scanner|[-_ ]?scan)?' "${file}"
}

select_without_sonar_entrypoint() {
  local candidate
  for candidate in \
    scripts/qa-test.sh \
    scripts/test.sh \
    scripts/tests.sh \
    scripts/coverage.sh
  do
    if [[ -x "${repository}/${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  if [[ -x "${qa_check}" ]] && ! references_sonar "${qa_check}"; then
    printf '%s\n' "scripts/qa-check.sh"
    return 0
  fi
  return 3
}

if [[ "${MODE}" == "with-sonar" ]]; then
  [[ -x "${qa_check}" ]] || {
    echo "ERROR: ${relative_path}: no existe scripts/qa-check.sh ejecutable" >&2
    exit 3
  }
  if ! references_sonar "${qa_check}"; then
    echo "ERROR: ${relative_path}: scripts/qa-check.sh no tiene Sonar configurado" >&2
    exit 3
  fi
  entrypoint="scripts/qa-check.sh"
else
  set +e
  entrypoint="$(select_without_sonar_entrypoint)"
  select_status=$?
  set -e
  if [[ "${select_status}" != "0" ]]; then
    if [[ "${select_status}" == "3" ]]; then
      if [[ -x "${qa_check}" ]]; then
        echo "ERROR: ${relative_path}: QA existe pero no expone un entrypoint sin Sonar (qa-test.sh, test.sh, tests.sh o coverage.sh)" >&2
      else
        echo "ERROR: ${relative_path}: no existe QA ejecutable" >&2
      fi
    fi
    exit "${select_status}"
  fi
fi

mkdir -p "${OUTPUT_DIR}"
slug="$(printf '%s' "${relative_path}" | tr '/[:space:]' '--' | tr -cd '[:alnum:]_.-')"
mode_slug="$(printf '%s' "${MODE}" | tr -cd '[:alnum:]-')"
log_file="${OUTPUT_DIR}/${slug}-${mode_slug}.log"
result_file="${OUTPUT_DIR}/${slug}-${mode_slug}-qa-results.md"
rm -f "${log_file}" "${result_file}"
started_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

printf 'Ejecutando QA (%s): %s -> %s\n' "${MODE}" "${relative_path}" "${entrypoint}"
set +e
(
  cd "${repository}"
  "./${entrypoint}"
) 2>&1 | tee "${log_file}"
status=${PIPESTATUS[0]}
set -e
finished_at="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

{
  echo "# QA execution"
  echo
  echo "- Repository: \`${relative_path}\`"
  echo "- Mode: \`${MODE}\`"
  echo "- Entrypoint: \`${entrypoint}\`"
  echo "- Started: \`${started_at}\`"
  echo "- Finished: \`${finished_at}\`"
  echo "- Exit code: \`${status}\`"
  if [[ "${status}" == "0" ]]; then
    echo "- Overall status: passed"
  else
    echo "- Overall status: failed"
  fi
  echo "- Log: \`QA/output/${slug}-${mode_slug}.log\`"
} > "${result_file}"

project_evidence="${repository}/context/qa-results.md"
if [[ "${MODE}" == "with-sonar" ]]; then
  if [[ ! -s "${project_evidence}" ]]; then
    echo "ERROR: ${relative_path}: qa-check.sh no generó context/qa-results.md" >&2
    exit 4
  fi
  {
    echo
    echo "## Project evidence"
    echo
    cat "${project_evidence}"
  } >> "${result_file}"
fi

if [[ "${status}" != "0" ]]; then
  echo "ERROR: QA falló para ${relative_path} (exit ${status})" >&2
  exit "${status}"
fi

echo "Evidencia centralizada: QA/output/${slug}-${mode_slug}-qa-results.md"
echo "QA completado: ${relative_path} (${MODE})"
