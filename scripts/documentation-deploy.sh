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
FORMAT_CONTEXT_FILE="${DOCUMENTATION_ROOT}/FORMAT_CONTEXT.md"
SYSTEM_PROMPT_FILE="${DOCUMENTATION_ROOT}/SYS_PROMPT.md"
QA_RESULTS_FILE="${CONTEXT_ROOT}/QA_CONTEXT.md"
RESPONSE_FILE="${OUTPUT_DIR}/documentation-export-response.json"

[[ -f "${FORMAT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe ${FORMAT_CONTEXT_FILE}"
  exit 1
}

[[ -f "${SYSTEM_PROMPT_FILE}" ]] || {
  echo "ERROR: No existe ${SYSTEM_PROMPT_FILE}"
  exit 1
}

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

find "${INPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete
find "${OUTPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete

cd "${CONTEXT_ROOT}"

GIT_DIFF="$(
  {
    git diff --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git diff --cached --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
  } 2>/dev/null
)"

CHANGED_FILES="$(
  {
    git diff --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git diff --cached --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git ls-files --others --exclude-standard
  } 2>/dev/null \
    | awk '!/(^|\/)\.env($|\.)/' \
    | sort -u
)"

if [[ -n "${CHANGED_FILES}" ]]; then
  CHANGED_FILES_INLINE="$(
    printf '%s\n' "${CHANGED_FILES}" \
      | awk 'NF' \
      | paste -sd ',' - \
      | sed 's/,/, /g'
  )"
  CHANGE_SUMMARY="Current ${PROJECT_NAME} changes affect: ${CHANGED_FILES_INLINE}."
else
  CHANGE_SUMMARY="No uncommitted changes detected in ${PROJECT_NAME}."
fi

if [[ -f "${QA_RESULTS_FILE}" ]]; then
  QA_RESULTS="$(cat "${QA_RESULTS_FILE}")"
else
  QA_RESULTS="No QA results file was supplied for this documentation deployment."
fi

PAYLOAD="$(
  PROJECT_NAME="${PROJECT_NAME}" \
  CHANGE_SUMMARY="${CHANGE_SUMMARY}" \
  CHANGED_FILES="${CHANGED_FILES}" \
  GIT_DIFF="${GIT_DIFF}" \
  QA_RESULTS="${QA_RESULTS}" \
  python3 <<'PY'
import json
import os

changed_files = [
    line.strip()
    for line in os.environ["CHANGED_FILES"].splitlines()
    if line.strip()
]

print(json.dumps({
    "project_name": os.environ["PROJECT_NAME"],
    "workflow": "documentation-deploy",
    "change_summary": os.environ["CHANGE_SUMMARY"],
    "changed_files": changed_files,
    "git_diff": os.environ["GIT_DIFF"],
    "qa_results": os.environ["QA_RESULTS"],
    "retrieved_context_chunks": []
}))
PY
)"

curl --fail-with-body --silent --show-error \
  --request POST \
  "${AI_ASSISTANT_URL%/}/documentation/export" \
  --header "Content-Type: application/json" \
  --data-binary "${PAYLOAD}" \
  --output "${RESPONSE_FILE}"

python3 - "${RESPONSE_FILE}" <<'PY'
import json
import sys
from pathlib import Path

response_path = Path(sys.argv[1])
payload = json.loads(response_path.read_text(encoding="utf-8"))

if payload.get("status") != "completed":
    raise SystemExit("ERROR: La exportación no terminó con status=completed")
if payload.get("workflow") != "documentation-deploy":
    raise SystemExit("ERROR: La respuesta no corresponde a documentation-deploy")
if payload.get("project_name") != "sbm-suite-context":
    raise SystemExit("ERROR: La respuesta no corresponde al proyecto sbm-suite-context")
if payload.get("collection_name") != "sbm_documentation":
    raise SystemExit("ERROR: La colección esperada es sbm_documentation")
errors = payload.get("errors")
if not isinstance(errors, list) or errors:
    raise SystemExit(f"ERROR: La exportación informó errores: {errors}")
zip_path = payload.get("documentation_zip_path")
if not isinstance(zip_path, str) or not zip_path:
    raise SystemExit("ERROR: La respuesta no contiene documentation_zip_path")

print("Exportación de documentación completada.")
print(f"Paquete: {zip_path}")
PY

echo
echo "Generado en: documentation/output"
echo "Respuesta: documentation/output/documentation-export-response.json"
