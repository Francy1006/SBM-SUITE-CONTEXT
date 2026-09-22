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

context_python() {
  local candidate
  for candidate in \
    "${CONTEXT_ROOT}/.venv/Scripts/python.exe" \
    "${CONTEXT_ROOT}/.venv/Scripts/python3.exe" \
    "${CONTEXT_ROOT}/.venv/bin/python3" \
    "${CONTEXT_ROOT}/.venv/bin/python"
  do
    if [[ -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  echo "ERROR: Context requiere su propio Python en .venv/Scripts o .venv/bin" >&2
  return 1
}

path_without_inherited_venv() {
  local inherited_venv="${VIRTUAL_ENV:-}" entry cleaned="" path_value="${PATH:-}"
  local entries=()
  if [[ -n "${MSYSTEM:-}" && "${path_value}" =~ (^|\;)[A-Za-z]:[/\\] ]]; then
    path_value="$(cygpath --path --unix "${path_value}")"
  fi
  IFS=':' read -r -a entries <<< "${path_value}"
  for entry in "${entries[@]}"; do
    case "${entry%/}" in
      "${CONTEXT_ROOT}/.venv/Scripts"|"${CONTEXT_ROOT}/.venv/bin")
        continue
        ;;
      "${inherited_venv}/Scripts"|"${inherited_venv}/bin")
        [[ -n "${inherited_venv}" ]] && continue
        ;;
    esac
    if [[ -n "${cleaned}" ]]; then
      cleaned="${cleaned}:${entry}"
    else
      cleaned="${entry}"
    fi
  done
  printf '%s\n' "${cleaned}"
}

QA_RUNTIME_DIR=""
cleanup_qa_runtime() {
  if [[ -n "${QA_RUNTIME_DIR}" && -d "${QA_RUNTIME_DIR}" ]]; then
    rm -rf -- "${QA_RUNTIME_DIR}"
  fi
}
trap cleanup_qa_runtime EXIT

ensure_qa_runtime() {
  if [[ -z "${QA_RUNTIME_DIR}" ]]; then
    QA_RUNTIME_DIR="$(mktemp -d)"
  fi
}

install_windows_python3_shim() {
  local python_executable="$1"
  ensure_qa_runtime
  printf '#!/usr/bin/env bash\nexec %q "$@"\n' "${python_executable}" \
    > "${QA_RUNTIME_DIR}/python3"
  chmod +x "${QA_RUNTIME_DIR}/python3"
}

install_msys_docker_shim() {
  local docker_executable="$1"
  ensure_qa_runtime
  cat > "${QA_RUNTIME_DIR}/docker" <<'DOCKER_SHIM'
#!/usr/bin/env bash
set -euo pipefail

host_path() {
  if command -v cygpath >/dev/null 2>&1; then
    cygpath -am -- "$1"
  else
    printf '%s\n' "$1"
  fi
}

volume_spec() {
  local spec="$1" source remainder tail
  if [[ "${spec}" =~ ^[A-Za-z]:[/\\] ]]; then
    tail="${spec:2}"
    source="${spec:0:2}${tail%%:*}"
    remainder="${tail#*:}"
  elif [[ "${spec}" == /*:* || "${spec}" == ./*:* || "${spec}" == ../*:* ]]; then
    source="${spec%%:*}"
    remainder="${spec#*:}"
  else
    printf '%s\n' "${spec}"
    return 0
  fi
  printf '%s:%s\n' "$(host_path "${source}")" "${remainder}"
}

compose_command=0
[[ "${1:-}" == "compose" ]] && compose_command=1
requires_path_handling=0
for argument in "$@"; do
  case "${argument}" in
    cp|-v|--volume|--volume=*|--env-file|--env-file=*|/*|*=/*|[A-Za-z]:[/\\]*)
      requires_path_handling=1
      break
      ;;
  esac
  if [[ "${compose_command}" == "1" ]]; then
    case "${argument}" in
      -f|--file|--file=*|--project-directory|--project-directory=*)
        requires_path_handling=1
        break
        ;;
    esac
  fi
done
if [[ "${requires_path_handling}" == "0" ]]; then
  exec "${QA_REAL_DOCKER}" "$@"
fi

converted=()
while [[ "$#" -gt 0 ]]; do
  if [[ "${compose_command}" == "1" ]]; then
    case "$1" in
      -f|--file|--project-directory)
        converted+=("$1")
        shift
        converted+=("$(host_path "$1")")
        shift
        continue
        ;;
      --file=*|--project-directory=*)
        converted+=("${1%%=*}=$(host_path "${1#*=}")")
        shift
        continue
        ;;
    esac
  fi
  case "$1" in
    -v|--volume)
      converted+=("$1")
      shift
      converted+=("$(volume_spec "$1")")
      ;;
    --volume=*)
      converted+=("--volume=$(volume_spec "${1#*=}")")
      ;;
    --env-file)
      converted+=("$1")
      shift
      converted+=("$(host_path "$1")")
      ;;
    --env-file=*)
      converted+=("${1%%=*}=$(host_path "${1#*=}")")
      ;;
    *)
      converted+=("$1")
      ;;
  esac
  shift
done

if [[ "${converted[0]:-}" == "cp" ]]; then
  for index in 1 2; do
    value="${converted[${index}]:-}"
    if [[ -n "${value}" && ( "${value}" != *:* || "${value}" =~ ^[A-Za-z]:[/\\] ) ]]; then
      converted[${index}]="$(host_path "${value}")"
    fi
  done
fi

MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
  "${QA_REAL_DOCKER}" "${converted[@]}"
DOCKER_SHIM
  chmod +x "${QA_RUNTIME_DIR}/docker"
  export QA_REAL_DOCKER="${docker_executable}"
}

CONTEXT_PYTHON="$(context_python)"
relative_path="$(
  "${CONTEXT_PYTHON}" "${REPOSITORY_HELPER}" resolve "${SELECTOR}" | tr -d '\r'
)"
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

child_path="$(path_without_inherited_venv)"
repository_venv=""
repository_venv_bin=""
if [[ -d "${repository}/.venv/Scripts" ]]; then
  repository_venv="${repository}/.venv"
  repository_venv_bin="${repository_venv}/Scripts"
elif [[ -d "${repository}/.venv/bin" ]]; then
  repository_venv="${repository}/.venv"
  repository_venv_bin="${repository_venv}/bin"
fi
if [[ -n "${repository_venv_bin}" ]]; then
  child_path="${repository_venv_bin}${child_path:+:${child_path}}"
fi

if [[ -n "${MSYSTEM:-}" ]]; then
  if [[ -n "${repository_venv_bin}" && "${repository_venv_bin}" == */Scripts ]]; then
    if [[ ! -x "${repository_venv_bin}/python3" && ! -x "${repository_venv_bin}/python3.exe" && -x "${repository_venv_bin}/python.exe" ]]; then
      install_windows_python3_shim "${repository_venv_bin}/python.exe"
    fi
  elif [[ -z "${repository_venv}" ]]; then
    install_windows_python3_shim "${CONTEXT_PYTHON}"
  fi
  real_docker="$(PATH="${child_path}" command -v docker || true)"
  if [[ -n "${real_docker}" ]]; then
    install_msys_docker_shim "${real_docker}"
  fi
fi
if [[ -n "${QA_RUNTIME_DIR}" ]]; then
  child_path="${QA_RUNTIME_DIR}${child_path:+:${child_path}}"
fi

printf 'Ejecutando QA (%s): %s -> %s\n' "${MODE}" "${relative_path}" "${entrypoint}"
set +e
(
  unset VIRTUAL_ENV VIRTUAL_ENV_PROMPT
  if [[ -n "${repository_venv}" ]]; then
    export VIRTUAL_ENV="${repository_venv}"
  fi
  export PATH="${child_path}"
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
