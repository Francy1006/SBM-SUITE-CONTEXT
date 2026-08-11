#!/usr/bin/env bash
set -euo pipefail

CONTEXT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${CONTEXT_ROOT}/.env.dev"
SBM_SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"

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

AI_ASSISTANT_URL="${AI_ASSISTANT_URL:-}"
if [[ -z "${AI_ASSISTANT_URL}" && -f "${ENV_FILE}" ]]; then
  AI_ASSISTANT_URL="$(get_env AI_ASSISTANT_URL)"
fi
if [[ -z "${AI_ASSISTANT_URL}" ]]; then
  for candidate in \
    "${SBM_SUITE_ROOT}/SBM/sbm-ai-assistant/.env.dev" \
    "${SBM_SUITE_ROOT}/sbm/sbm-ai-assistant/.env.dev"
  do
    if [[ -f "${candidate}" ]]; then
      ENV_FILE="${candidate}"
      AI_ASSISTANT_URL="$(get_env AI_ASSISTANT_URL)"
      break
    fi
  done
fi

[[ -n "${AI_ASSISTANT_URL}" ]] || {
  echo "ERROR: Falta AI_ASSISTANT_URL"
  exit 1
}

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

DOCUMENTATION_UPGRADE_VALIDATOR="${CONTEXT_ROOT}/scripts/validate_documentation_upgrade.py"
[[ -f "${DOCUMENTATION_UPGRADE_VALIDATOR}" ]] || {
  echo "ERROR: No existe ${DOCUMENTATION_UPGRADE_VALIDATOR}"
  exit 1
}
python3 "${DOCUMENTATION_UPGRADE_VALIDATOR}" "${UPGRADE_ZIP}"

PROJECT_NAME="$(
  python3 - "${UPGRADE_ZIP}" <<'PY'
import json
import re
import sys
from zipfile import BadZipFile, ZipFile

try:
    with ZipFile(sys.argv[1]) as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
except (BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: No se pudo leer manifest.project_name: {exc}") from exc

project_name = manifest.get("project_name")
if not isinstance(project_name, str) or not re.fullmatch(
    r"[A-Za-z0-9][A-Za-z0-9._-]*", project_name
):
    raise SystemExit("ERROR: manifest.project_name inválido")
if manifest.get("workflow") != "documentation-upgrade":
    raise SystemExit("ERROR: manifest.workflow debe ser documentation-upgrade")
print(project_name)
PY
)"

CONTRACT_FILE="$(mktemp)"
trap 'rm -f "${CONTRACT_FILE}"' EXIT
HTTP_STATUS="$(
  curl --silent --show-error \
    --output "${CONTRACT_FILE}" \
    --write-out "%{http_code}" \
    --request GET \
    "${AI_ASSISTANT_URL%/}/contexts/contract"
)"
[[ "${HTTP_STATUS}" == "200" ]] || {
  echo "ERROR: /contexts/contract HTTP ${HTTP_STATUS}"
  exit 1
}
python3 - "${CONTRACT_FILE}" "${PROJECT_NAME}" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
projects = contract.get("canonical_projects")
if not isinstance(projects, dict) or sys.argv[2] not in projects:
    raise SystemExit("ERROR: manifest.project_name no está publicado por Project Registry")
PY

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

python3 - "${RESPONSE_FILE}" "${PROJECT_NAME}" <<'PY'
import json
import sys
from pathlib import Path

response_path = Path(sys.argv[1])
payload = json.loads(response_path.read_text(encoding="utf-8"))
project_name = sys.argv[2]

if payload.get("workflow") != "documentation-upgrade":
    raise SystemExit("ERROR: La respuesta no corresponde a documentation-upgrade")
if payload.get("project_name") != project_name:
    raise SystemExit("ERROR: La respuesta no corresponde al proyecto del manifest")
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
