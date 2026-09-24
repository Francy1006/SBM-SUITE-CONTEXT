#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == "0" ]] || {
  echo "Uso: ./scripts/documentation-upgrade.sh" >&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${CONTEXT_ROOT}/.env.dev"
SBM_SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"

get_env() {
  local key="$1"
  local env_file="${2:-${ENV_FILE}}"

  awk -v key="${key}" '
    index($0, key "=") == 1 { value = substr($0, length(key) + 2) }
    END {
      sub(/\r$/, "", value)
      sub(/^"/, "", value)
      sub(/"$/, "", value)
      printf "%s", value
    }
  ' "${env_file}"
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
      AI_ASSISTANT_URL="$(get_env AI_ASSISTANT_URL "${candidate}")"
      break
    fi
  done
fi

[[ -n "${AI_ASSISTANT_URL}" ]] || {
  echo "ERROR: Falta AI_ASSISTANT_URL"
  exit 1
}

[[ "${AI_ASSISTANT_URL}" =~ ^https?:// ]] || {
  echo "ERROR: AI_ASSISTANT_URL debe usar http:// o https://" >&2
  exit 1
}

AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS="${AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS:-5}"
AI_ASSISTANT_MAX_TIME_SECONDS="${AI_ASSISTANT_MAX_TIME_SECONDS:-180}"
for timeout_value in "${AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS}" "${AI_ASSISTANT_MAX_TIME_SECONDS}"; do
  [[ "${timeout_value}" =~ ^[1-9][0-9]*$ ]] || {
    echo "ERROR: Los timeouts HTTP deben ser enteros positivos" >&2
    exit 1
  }
done

# SBM-UTIL always uses the process environment or context/.env.dev.
SBM_UTIL_BASE_URL="${SBM_UTIL_BASE_URL:-}"
SBM_SERVICE_TOKEN="${SBM_SERVICE_TOKEN:-}"
if [[ -f "${ENV_FILE}" ]]; then
  SBM_UTIL_BASE_URL="${SBM_UTIL_BASE_URL:-$(get_env SBM_UTIL_BASE_URL)}"
  SBM_SERVICE_TOKEN="${SBM_SERVICE_TOKEN:-$(get_env SBM_SERVICE_TOKEN)}"
fi
[[ -n "${SBM_UTIL_BASE_URL}" ]] || {
  echo "ERROR: Falta SBM_UTIL_BASE_URL" >&2
  exit 1
}
[[ "${SBM_UTIL_BASE_URL}" =~ ^https?:// ]] || {
  echo "ERROR: SBM_UTIL_BASE_URL debe usar http:// o https://" >&2
  exit 1
}
[[ -n "${SBM_SERVICE_TOKEN}" ]] || {
  echo "ERROR: Falta SBM_SERVICE_TOKEN" >&2
  exit 1
}
SBM_UTIL_CONNECT_TIMEOUT_SECONDS="${SBM_UTIL_CONNECT_TIMEOUT_SECONDS:-5}"
SBM_UTIL_MAX_TIME_SECONDS="${SBM_UTIL_MAX_TIME_SECONDS:-900}"
for timeout_value in "${SBM_UTIL_CONNECT_TIMEOUT_SECONDS}" "${SBM_UTIL_MAX_TIME_SECONDS}"; do
  [[ "${timeout_value}" =~ ^[1-9][0-9]*$ ]] || {
    echo "ERROR: Los timeouts HTTP de SBM-UTIL deben ser enteros positivos" >&2
    exit 1
  }
done

[[ "${CONTEXT_ROOT}" == "${SBM_SUITE_ROOT}/context" ]] || {
  echo "ERROR: CONTEXT_ROOT no corresponde a ${SBM_SUITE_ROOT}/context"
  exit 1
}

DOCUMENTATION_ROOT="${CONTEXT_ROOT}/documentation"
INPUT_DIR="${DOCUMENTATION_ROOT}/input"
OUTPUT_DIR="${DOCUMENTATION_ROOT}/output"
BACKUP_DIR="${CONTEXT_ROOT}/backup"
RESPONSE_FILE="${OUTPUT_DIR}/documentation-upgrade-response.json"

upgrade_documentation() {
mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}" "${BACKUP_DIR}"
rm -f "${RESPONSE_FILE}"

UPGRADE_INPUT="$(
  "${SCRIPT_DIR}/resolve-upgrade-input.py" \
    "${INPUT_DIR}" \
    "documentation-upgrade" \
    "documentation-upgrade.zip"
)"
IFS=$'\t' read -r ORIGINAL_UPGRADE_ZIP UPGRADE_ZIP <<< "${UPGRADE_INPUT}"
[[ -f "${UPGRADE_ZIP}" ]] || {
  echo "ERROR: No se pudo normalizar ${ORIGINAL_UPGRADE_ZIP} a ${UPGRADE_ZIP}"
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
sys.stdout.write(project_name)
PY
)"

CONTRACT_FILE="$(mktemp)"
HTTP_STATUS="$(
  curl --connect-timeout "${AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS}" \
    --max-time "${AI_ASSISTANT_MAX_TIME_SECONDS}" \
    --silent --show-error \
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
  curl --connect-timeout "${AI_ASSISTANT_CONNECT_TIMEOUT_SECONDS}" \
    --max-time "${AI_ASSISTANT_MAX_TIME_SECONDS}" \
    --silent --show-error \
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
import sys

sys.stdout.write(json.dumps({
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

"${SCRIPT_DIR}/cleanup-exchange.sh" documentation "${CONTEXT_ROOT}"

}

# Keep retry state outside the exchange directories cleaned by the lifecycle.
PENDING_SYNC_FILE="${DOCUMENTATION_ROOT}/.notion-sync-pending"
SYNC_RESPONSE_FILE="$(mktemp)"
CONTRACT_FILE=""
trap 'rm -f "${CONTRACT_FILE}" "${SYNC_RESPONSE_FILE}"' EXIT
if [[ -f "${PENDING_SYNC_FILE}" ]] && \
   [[ -z "$(find "${INPUT_DIR}" -maxdepth 1 -type f -name '*.zip' -print -quit)" ]]; then
  echo "Reintentando publicación Notion pendiente; Markdown local conservado."
else
  # Preserve any pending publication if the new local upgrade fails.
  upgrade_documentation
  touch "${PENDING_SYNC_FILE}"
fi

CURL_STATUS=0
HTTP_STATUS="$(
  curl --connect-timeout "${SBM_UTIL_CONNECT_TIMEOUT_SECONDS}" \
    --max-time "${SBM_UTIL_MAX_TIME_SECONDS}" \
    --silent --show-error \
    --output "${SYNC_RESPONSE_FILE}" \
    --write-out "%{http_code}" \
    --request POST \
    "${SBM_UTIL_BASE_URL%/}/api/notion/documentation/sync" \
    --header "Content-Type: application/json" \
    --header "X-SBM-Service-Token: ${SBM_SERVICE_TOKEN}" \
    --data-binary '{"project":"SBM-SUITE","documentationPath":"sbm-suite"}'
)" || CURL_STATUS=$?
if [[ "${CURL_STATUS}" -ne 0 ]]; then
  echo "ERROR: Sync Notion vía SBM-UTIL falló (curl ${CURL_STATUS}; conexión o timeout). Markdown conservado; vuelva a ejecutar el script para reintentar." >&2
  exit 1
fi
[[ "${HTTP_STATUS}" =~ ^2[0-9][0-9]$ ]] || {
  echo "ERROR: Sync Notion vía SBM-UTIL respondió HTTP ${HTTP_STATUS}. Markdown conservado; vuelva a ejecutar el script para reintentar." >&2
  exit 1
}
python3 - "${SYNC_RESPONSE_FILE}" <<'PY_SYNC'
import json
import sys
from pathlib import Path

try:
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("project") != "SBM-SUITE":
        raise ValueError("project debe ser SBM-SUITE")
    counters = ("discovered", "created", "updated", "unchanged")
    for key in counters:
        if type(payload.get(key)) is not int or payload[key] < 0:
            raise ValueError(f"{key} debe existir y ser un entero no negativo")
    if payload["discovered"] != sum(payload[key] for key in counters[1:]):
        raise ValueError("discovered no coincide con created + updated + unchanged")
except (OSError, UnicodeError, ValueError) as exc:
    # Do not echo the response: it may contain credentials or sensitive details.
    detail = str(exc) if type(exc) is ValueError else "JSON inválido o ilegible"
    raise SystemExit(
        f"ERROR: Respuesta SBM-UTIL inválida: {detail}. Markdown conservado; "
        "vuelva a ejecutar el script para reintentar."
    ) from None
print("Notion sincronizado: " + "/".join(f"{key}={payload[key]}" for key in counters))
PY_SYNC
rm -f "${PENDING_SYNC_FILE}"
echo "Documentación actualizada correctamente."
