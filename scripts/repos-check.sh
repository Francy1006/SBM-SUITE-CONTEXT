#!/usr/bin/env bash
set -uo pipefail

[[ "$#" == "0" ]] || {
  echo "Uso: ./scripts/repos-check.sh" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
REPOSITORY_HELPER="${SCRIPT_DIR}/suite-repositories.py"
PATH_PORTABILITY_HELPER="${SCRIPT_DIR}/path-portability.py"

for helper in "${REPOSITORY_HELPER}" "${PATH_PORTABILITY_HELPER}"; do
  [[ -x "${helper}" || -f "${helper}" ]] || {
    echo "ERROR: No existe scripts/$(basename "${helper}")" >&2
    exit 1
  }
done

REPOSITORIES="$(mktemp)"
trap 'rm -f "${REPOSITORIES}"' EXIT
python3 "${REPOSITORY_HELPER}" list-paths > "${REPOSITORIES}" || exit 1

result=0
while IFS= read -r relative_path; do
  [[ -n "${relative_path}" ]] || continue
  repository="${SUITE_ROOT}/${relative_path}"

  if [[ ! -d "${repository}" ]]; then
    printf '%s | branch=- | estado=error | upstream=- | ahead=- behind=- | repositorio inexistente\n' \
      "${relative_path}"
    result=1
    continue
  fi

  git_root="$(git -C "${repository}" rev-parse --show-toplevel 2>/dev/null)" || {
    printf '%s | branch=- | estado=error | upstream=- | ahead=- behind=- | no es un repositorio Git\n' \
      "${relative_path}"
    result=1
    continue
  }
  if ! python3 "${PATH_PORTABILITY_HELPER}" equivalent \
    "${git_root}" "$(cd "${repository}" && pwd -P)"; then
    printf '%s | branch=- | estado=error | upstream=- | ahead=- behind=- | no es la raíz del repositorio Git\n' \
      "${relative_path}"
    result=1
    continue
  fi

  branch="$(git -C "${repository}" symbolic-ref --quiet --short HEAD 2>/dev/null)" \
    || branch="DETACHED_HEAD"
  if [[ -n "$(git -C "${repository}" status --porcelain)" ]]; then
    state="con cambios"
  else
    state="limpio"
  fi

  upstream="$(git -C "${repository}" rev-parse \
    --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)" || upstream=""
  if [[ -n "${upstream}" ]]; then
    counts="$(git -C "${repository}" rev-list --left-right --count \
      "HEAD...${upstream}" 2>/dev/null)" || counts=""
    if [[ -n "${counts}" ]]; then
      read -r ahead behind <<< "${counts}"
    else
      ahead="-"
      behind="-"
    fi
  else
    upstream="sin upstream"
    ahead="-"
    behind="-"
  fi

  printf '%s | branch=%s | estado=%s | upstream=%s | ahead=%s behind=%s\n' \
    "${relative_path}" "${branch}" "${state}" "${upstream}" "${ahead}" "${behind}"
done < "${REPOSITORIES}"

if [[ "${result}" == "0" ]]; then
  echo "Check transversal completado correctamente."
else
  echo "ERROR: Check transversal completado con errores." >&2
fi

exit "${result}"
