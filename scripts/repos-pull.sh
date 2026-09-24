#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/repos-pull.sh
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
PATH_PORTABILITY_HELPER="${SCRIPT_DIR}/path-portability.py"

[[ -x "${REPOSITORY_HELPER}" || -f "${REPOSITORY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/suite-repositories.py" >&2
  exit 1
}
[[ -x "${PATH_PORTABILITY_HELPER}" || -f "${PATH_PORTABILITY_HELPER}" ]] || {
  echo "ERROR: No existe scripts/path-portability.py" >&2
  exit 1
}

if python3 -c 'import sys; raise SystemExit(sys.version_info[0] != 3)' >/dev/null 2>&1; then
  PYTHON_COMMAND="python3"
elif python -c 'import sys; raise SystemExit(sys.version_info[0] != 3)' >/dev/null 2>&1; then
  PYTHON_COMMAND="python"
else
  echo "ERROR: Python 3 no está disponible" >&2
  exit 1
fi

REPOSITORIES="$(mktemp)"
PREFLIGHT="$(mktemp)"
UPDATE_PLAN="$(mktemp)"
trap 'rm -f "${REPOSITORIES}" "${PREFLIGHT}" "${UPDATE_PLAN}"' EXIT
"${PYTHON_COMMAND}" "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}"

report_error() {
  local relative_path="$1" branch="$2" reason="$3"
  printf 'repositorio: %s\nbranch actual: %s\nestado: error (%s)\n\n' \
    "${relative_path}" "${branch}" "${reason}" >&2
}

preflight_repository() {
  local relative_path="$1" repository="${SUITE_ROOT}/$1" branch git_root

  if [[ ! -d "${repository}" ]]; then
    report_error "${relative_path}" "desconocida" "directorio inexistente"
    return 1
  fi
  if ! git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    report_error "${relative_path}" "desconocida" "no es un repositorio Git válido"
    return 1
  fi
  git_root="$(git -C "${repository}" rev-parse --show-toplevel)"
  if ! "${PYTHON_COMMAND}" "${PATH_PORTABILITY_HELPER}" equivalent \
    "${git_root}" "$(cd "${repository}" && pwd -P)"; then
    report_error "${relative_path}" "desconocida" "el path resuelto no es la raíz del repositorio"
    return 1
  fi
  if ! branch="$(git -C "${repository}" symbolic-ref --quiet --short HEAD)"; then
    report_error "${relative_path}" "detached HEAD" "HEAD no referencia una branch"
    return 1
  fi
  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    report_error "${relative_path}" "${branch}" "working tree contiene cambios tracked o untracked"
    return 1
  fi
  if ! git -C "${repository}" remote get-url origin >/dev/null 2>&1; then
    report_error "${relative_path}" "${branch}" "remote origin inexistente"
    return 1
  fi

  printf '%s\t%s\n' "${relative_path}" "${branch}" >> "${PREFLIGHT}"
}

echo "### FASE 1/3: PREFLIGHT LOCAL"
preflight_failed=0
while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  preflight_repository "${relative_path}" || preflight_failed=1
done < "${REPOSITORIES}"

[[ "${preflight_failed}" == "0" ]] || {
  echo "ERROR: Preflight transversal fallido; no se ejecutó fetch ni se modificó ningún repositorio." >&2
  exit 1
}
echo "Preflight local completado para todos los repositorios."
echo

echo "### FASE 2/3: FETCH Y VALIDACIÓN"
fetch_failed=0
while IFS=$'\t' read -r relative_path branch; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  if ! git -C "${repository}" fetch origin; then
    report_error "${relative_path}" "${branch}" "git fetch origin falló"
    fetch_failed=1
  fi
done < "${PREFLIGHT}"

[[ "${fetch_failed}" == "0" ]] || {
  echo "ERROR: Fetch transversal fallido; no se modificó ningún working tree." >&2
  exit 1
}

validation_failed=0
while IFS=$'\t' read -r relative_path branch; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  remote_ref="refs/remotes/origin/${branch}"

  if [[ "$(git -C "${repository}" symbolic-ref --quiet --short HEAD 2>/dev/null || true)" != "${branch}" ]]; then
    report_error "${relative_path}" "${branch}" "la branch cambió después del preflight"
    validation_failed=1
    continue
  fi
  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    report_error "${relative_path}" "${branch}" "el working tree cambió después del preflight"
    validation_failed=1
    continue
  fi

  if ! git -C "${repository}" show-ref --verify --quiet "${remote_ref}"; then
    report_error "${relative_path}" "${branch}" "origin/${branch} inexistente"
    validation_failed=1
    continue
  fi

  local_commit="$(git -C "${repository}" rev-parse HEAD)"
  remote_commit="$(git -C "${repository}" rev-parse "${remote_ref}")"
  if [[ "${local_commit}" == "${remote_commit}" ]]; then
    state="up-to-date"
  elif git -C "${repository}" merge-base --is-ancestor HEAD "${remote_ref}"; then
    state="fast-forward"
  elif git -C "${repository}" merge-base --is-ancestor "${remote_ref}" HEAD; then
    state="local-ahead"
  else
    report_error "${relative_path}" "${branch}" "branch local divergida de origin/${branch}"
    validation_failed=1
    continue
  fi
  printf '%s\t%s\t%s\n' "${relative_path}" "${branch}" "${state}" >> "${UPDATE_PLAN}"
done < "${PREFLIGHT}"

[[ "${validation_failed}" == "0" ]] || {
  echo "ERROR: Validación transversal fallida; no se modificó ningún working tree." >&2
  exit 1
}
echo "Referencias remotas y relaciones de ancestro validadas para todos los repositorios."
echo

echo "### FASE 3/3: ACTUALIZACIÓN FAST-FORWARD"
printf '%-40s %-42s %s\n' "REPOSITORY" "BRANCH ACTUAL" "ESTADO"
printf '%-40s %-42s %s\n' "----------------------------------------" "------------------------------------------" "------------"

fast_forward_count=0
up_to_date_count=0
local_ahead_count=0
while IFS=$'\t' read -r relative_path branch state; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"
  if [[ "${state}" == "fast-forward" ]]; then
    if ! git -C "${repository}" merge --ff-only "origin/${branch}" >/dev/null; then
      report_error "${relative_path}" "${branch}" "no se pudo aplicar fast-forward"
      exit 1
    fi
    fast_forward_count=$((fast_forward_count + 1))
  elif [[ "${state}" == "up-to-date" ]]; then
    up_to_date_count=$((up_to_date_count + 1))
  elif [[ "${state}" == "local-ahead" ]]; then
    local_ahead_count=$((local_ahead_count + 1))
  else
    report_error "${relative_path}" "${branch}" "estado interno inválido: ${state}"
    exit 1
  fi
  printf '%-40s %-42s %s\n' "${relative_path}" "${branch}" "${state}"
done < "${UPDATE_PLAN}"

total_count=$((fast_forward_count + up_to_date_count + local_ahead_count))
echo
echo "Sincronización transversal completada."
echo "Repositorios procesados: ${total_count}"
echo "Sincronizados mediante fast-forward: ${fast_forward_count}"
echo "Ya actualizados: ${up_to_date_count}"
echo "Local-ahead: ${local_ahead_count}"
