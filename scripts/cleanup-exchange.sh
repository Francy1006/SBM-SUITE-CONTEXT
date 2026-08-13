#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Uso:
  ./scripts/cleanup-exchange.sh context [context-root]
  ./scripts/cleanup-exchange.sh documentation [context-root]
USAGE
}

[[ "$#" -ge 1 && "$#" -le 2 ]] || {
  usage >&2
  exit 1
}

MODE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="${2:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

case "${MODE}" in
  context)
    INPUT_DIR="${CONTEXT_ROOT}/input"
    OUTPUT_DIR="${CONTEXT_ROOT}/output"
    RESPONSE_NAME="context-upgrade-response.json"
    ;;
  documentation)
    INPUT_DIR="${CONTEXT_ROOT}/documentation/input"
    OUTPUT_DIR="${CONTEXT_ROOT}/documentation/output"
    RESPONSE_NAME="documentation-upgrade-response.json"
    ;;
  *)
    echo "ERROR: Modo no soportado: ${MODE}" >&2
    usage >&2
    exit 1
    ;;
esac

RESPONSE_FILE="${OUTPUT_DIR}/${RESPONSE_NAME}"

[[ -d "${INPUT_DIR}" ]] || {
  echo "ERROR: No existe ${INPUT_DIR}" >&2
  exit 1
}
[[ -d "${OUTPUT_DIR}" ]] || {
  echo "ERROR: No existe ${OUTPUT_DIR}" >&2
  exit 1
}
[[ -f "${RESPONSE_FILE}" ]] || {
  echo "ERROR: No existe ${RESPONSE_FILE}; no se ejecuta cleanup" >&2
  exit 1
}

find "${INPUT_DIR}" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
find "${OUTPUT_DIR}" -mindepth 1 -maxdepth 1 \
  ! -name "${RESPONSE_NAME}" -exec rm -rf -- {} +

[[ -z "$(find "${INPUT_DIR}" -mindepth 1 -maxdepth 1 -print -quit)" ]] || {
  echo "ERROR: ${INPUT_DIR} no quedó vacío" >&2
  exit 1
}

OUTPUT_COUNT="$(find "${OUTPUT_DIR}" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')"
[[ "${OUTPUT_COUNT}" == "1" && -f "${RESPONSE_FILE}" ]] || {
  echo "ERROR: ${OUTPUT_DIR} debe contener únicamente ${RESPONSE_NAME}" >&2
  exit 1
}

printf 'Cleanup completado: %s\n' "${MODE}"
