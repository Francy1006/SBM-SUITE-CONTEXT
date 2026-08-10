#!/usr/bin/env bash
set -euo pipefail

CONTEXT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${CONTEXT_ROOT}/.env.dev"

[[ -f "${ENV_FILE}" ]] || {
  echo "ERROR: No existe ${ENV_FILE}"
  exit 1
}

get_env() {
  local key="$1"

  awk -v key="${key}" '
    index($0, key "=") == 1 { value = substr($0, length(key) + 2) }
    END {
      sub(/\r$/, "", value)
      sub(/^"/, "", value)
      sub(/"$/, "", value)
      printf "%s", value
    }
  ' "${ENV_FILE}"
}

PROJECT_NAME="$(get_env DOPPLER_PROJECT)"
AI_ASSISTANT_URL="$(get_env AI_ASSISTANT_URL)"
SBM_SUITE_ROOT_RAW="$(get_env SBM_SUITE_ROOT)"

[[ "${PROJECT_NAME}" == "sbm-suite-context" ]] || {
  echo "ERROR: DOPPLER_PROJECT debe ser sbm-suite-context"
  exit 1
}

[[ -n "${AI_ASSISTANT_URL}" ]] || {
  echo "ERROR: Falta AI_ASSISTANT_URL"
  exit 1
}

[[ -n "${SBM_SUITE_ROOT_RAW}" ]] || {
  echo "ERROR: Falta SBM_SUITE_ROOT"
  exit 1
}

resolve_suite_root() {
  local configured_path="$1"
  local candidate

  if [[ "${configured_path}" = /* ]]; then
    candidate="${configured_path}"
  else
    candidate="${CONTEXT_ROOT}/${configured_path}"
  fi

  [[ -d "${candidate}" ]] || {
    echo "ERROR: No existe SBM_SUITE_ROOT resuelto en ${candidate}" >&2
    return 1
  }

  (cd "${candidate}" && pwd)
}

SBM_SUITE_ROOT="$(resolve_suite_root "${SBM_SUITE_ROOT_RAW}")"

[[ "${CONTEXT_ROOT}" == "${SBM_SUITE_ROOT}/context" ]] || {
  echo "ERROR: CONTEXT_ROOT no corresponde a ${SBM_SUITE_ROOT}/context"
  exit 1
}

DOCUMENTATION_ROOT="${CONTEXT_ROOT}/documentation"
INPUT_DIR="${DOCUMENTATION_ROOT}/input"
OUTPUT_DIR="${DOCUMENTATION_ROOT}/output"
BACKUP_DIR="${CONTEXT_ROOT}/backup"
UPGRADE_ZIP="${INPUT_DIR}/documentation-upgrade.zip"
RESPONSE_FILE="${OUTPUT_DIR}/documentation-upgrade-response.json"

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}" "${BACKUP_DIR}"
rm -f "${RESPONSE_FILE}"

[[ -f "${UPGRADE_ZIP}" ]] || {
  echo "ERROR: No existe ${UPGRADE_ZIP}"
  exit 1
}

ZIP_COUNT="$(
  find "${INPUT_DIR}" \
    -maxdepth 1 \
    -type f \
    -name '*.zip' \
    | wc -l \
    | tr -d ' '
)"

[[ "${ZIP_COUNT}" == "1" ]] || {
  echo "ERROR: Debe existir exactamente un ZIP en ${INPUT_DIR}"
  exit 1
}

HTTP_STATUS="$(
  curl --silent --show-error \
    --output "${RESPONSE_FILE}" \
    --write-out "%{http_code}" \
    --request POST \
    "${AI_ASSISTANT_URL%/}/documentation/upgrade" \
    --header "Content-Type: application/json" \
    --data-binary "$(
      PROJECT_NAME="${PROJECT_NAME}" \
      python3 <<'PY'
import json
import os

print(json.dumps({
    "project_name": os.environ["PROJECT_NAME"],
    "workflow": "documentation-upgrade"
}))
PY
    )"
)"

if [[ "${HTTP_STATUS}" -lt 200 || "${HTTP_STATUS}" -ge 300 ]]; then
  echo "ERROR: Documentation upgrade respondió HTTP ${HTTP_STATUS}"
  if [[ -s "${RESPONSE_FILE}" ]]; then
    cat "${RESPONSE_FILE}"
    echo
  fi
  exit 1
fi

python3 - "${RESPONSE_FILE}" <<'PY'
import json
import sys
from pathlib import Path

response_path = Path(sys.argv[1])
payload = json.loads(response_path.read_text(encoding="utf-8"))

if payload.get("workflow") != "documentation-upgrade":
    raise SystemExit("ERROR: La respuesta no corresponde a documentation-upgrade")
if payload.get("project_name") != "sbm-suite-context":
    raise SystemExit("ERROR: La respuesta no corresponde al proyecto sbm-suite-context")
errors = payload.get("errors")
if errors is not None and (not isinstance(errors, list) or errors):
    raise SystemExit(f"ERROR: El upgrade informó errores: {errors}")
if payload.get("input_cleaned") is not True:
    raise SystemExit("ERROR: El ZIP de entrada no fue limpiado")
updated_files = payload.get("updated_files")
if not isinstance(updated_files, list) or not updated_files:
    raise SystemExit("ERROR: La respuesta no contiene archivos actualizados")
backup_directory = payload.get("backup_directory")
if not isinstance(backup_directory, str) or not backup_directory:
    raise SystemExit("ERROR: La respuesta no contiene backup_directory")
if not backup_directory.startswith("context/backup/"):
    raise SystemExit("ERROR: backup_directory debe ser relativo a context/backup/")

print("Archivos actualizados:")
for path in updated_files:
    print(f"- {path}")
print(f"Backup generado: {backup_directory}")
PY

[[ ! -e "${UPGRADE_ZIP}" ]] || {
  echo "ERROR: El ZIP de entrada no fue eliminado"
  exit 1
}

echo "Documentación actualizada correctamente."
