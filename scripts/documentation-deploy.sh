#!/usr/bin/env bash
set -euo pipefail

CONTEXT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${CONTEXT_ROOT}/.env.dev"

[[ "$#" == "0" ]] || {
  echo "Uso: ./scripts/documentation-deploy.sh" >&2
  exit 1
}

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
PROJECT_TREE_SCRIPT="${CONTEXT_ROOT}/scripts/project-tree.sh"
PROJECT_TREE_FILE="${CONTEXT_ROOT}/project-tree.txt"
RESPONSE_FILE="${OUTPUT_DIR}/documentation-export-response.json"
PACKAGE_FILE="${OUTPUT_DIR}/documentation-package.zip"
RECONCILIATION_HELPER="${CONTEXT_ROOT}/scripts/documentation_reconciliation.py"
RECONCILIATION_FILE="$(mktemp)"
trap 'rm -f "${RECONCILIATION_FILE}"' EXIT

[[ -f "${FORMAT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe ${FORMAT_CONTEXT_FILE}"
  exit 1
}

[[ -f "${SYSTEM_PROMPT_FILE}" ]] || {
  echo "ERROR: No existe ${SYSTEM_PROMPT_FILE}"
  exit 1
}

[[ -f "${RECONCILIATION_HELPER}" ]] || {
  echo "ERROR: No existe ${RECONCILIATION_HELPER}"
  exit 1
}

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

find "${INPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete
find "${OUTPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete

[[ -f "${PROJECT_TREE_SCRIPT}" ]] || {
  echo "ERROR: No existe ${PROJECT_TREE_SCRIPT}"
  exit 1
}

[[ -x "${PROJECT_TREE_SCRIPT}" ]] || {
  echo "ERROR: ${PROJECT_TREE_SCRIPT} no es ejecutable"
  exit 1
}

"${PROJECT_TREE_SCRIPT}"

[[ -f "${PROJECT_TREE_FILE}" ]] || {
  echo "ERROR: No existe ${PROJECT_TREE_FILE}"
  exit 1
}

python3 "${RECONCILIATION_HELPER}" \
  --project-context "${CONTEXT_ROOT}/PROJECT_CONTEXT.md" \
  --completed-context "${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md" \
  --documentation-root "${DOCUMENTATION_ROOT}" \
  --project-tree "${PROJECT_TREE_FILE}" \
  --output "${RECONCILIATION_FILE}"

RECONCILIATION_PENDING="$(
  python3 - "${RECONCILIATION_FILE}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("false" if payload["synchronized"] else "true")
PY
)"

if [[ "${RECONCILIATION_PENDING}" != "true" ]]; then
  python3 - "${RECONCILIATION_FILE}" "${RESPONSE_FILE}" <<'PY'
import json
import sys
from pathlib import Path

reconciliation_path, response_path = sys.argv[1:]
reconciliation = json.loads(
    Path(reconciliation_path).read_text(encoding="utf-8")
)
response = {
    "status": "completed",
    "workflow": "documentation-deploy",
    "project_name": "sbm-suite-context",
    "synchronized": True,
    "summary": reconciliation["summary"],
    "differences": [],
    "documentation_targets": [],
    "package_generated": False,
    "package_file": None,
}
Path(response_path).write_text(
    json.dumps(response, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY
  echo "Documentation already synchronized"
  echo "No se generó documentation/output/documentation-package.zip."
  echo "Respuesta: documentation/output/documentation-export-response.json"
  exit 0
fi

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

RECONCILIATION_SUMMARY="$(
  python3 - "${RECONCILIATION_FILE}" <<'PY'
import json
import sys
from pathlib import Path

print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["summary"])
PY
)"
CHANGE_SUMMARY="${CHANGE_SUMMARY} ${RECONCILIATION_SUMMARY}"

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
  RECONCILIATION_FILE="${RECONCILIATION_FILE}" \
  python3 <<'PY'
import json
import os
from pathlib import Path

changed_files = [
    line.strip()
    for line in os.environ["CHANGED_FILES"].splitlines()
    if line.strip()
]
reconciliation = json.loads(
    Path(os.environ["RECONCILIATION_FILE"]).read_text(encoding="utf-8")
)

print(json.dumps({
    "project_name": os.environ["PROJECT_NAME"],
    "workflow": "documentation-deploy",
    "change_summary": os.environ["CHANGE_SUMMARY"],
    "changed_files": changed_files,
    "git_diff": os.environ["GIT_DIFF"],
    "qa_results": os.environ["QA_RESULTS"],
    "retrieved_context_chunks": reconciliation["retrieved_context_chunks"],
    "documentation_targets": reconciliation["documentation_targets"],
}))
PY
)"

printf '%s' "${PAYLOAD}" \
  | curl --fail-with-body --silent --show-error \
      --request POST \
      "${AI_ASSISTANT_URL%/}/documentation/export" \
      --header "Content-Type: application/json" \
      --data-binary @- \
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

python3 - "${PACKAGE_FILE}" <<'PY'
import json
import sys
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

try:
    with ZipFile(sys.argv[1]) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        listed = {
            line.strip()
            for line in archive.read("documentation-files.txt")
            .decode("utf-8")
            .splitlines()
            if line.strip()
        }
except (BadZipFile, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: documentation-package.zip inválido: {exc}") from exc

functional = {
    path
    for path in names
    if PurePosixPath(path).parts[:2] == ("documentation", "pages")
    and path.endswith(".md")
}
declarations = manifest.get("documentation_files")
if not isinstance(declarations, list):
    raise SystemExit("ERROR: manifest.documentation_files inválido")
declared = {
    item.get("archive_path")
    for item in declarations
    if isinstance(item, dict)
    and item.get("complete") is True
    and item.get("selected_by_rag") is True
}
if not functional:
    raise SystemExit(
        "ERROR: documentation-package.zip no contiene candidatos funcionales"
    )
if functional != listed or functional != declared:
    raise SystemExit(
        "ERROR: candidatos físicos, documentation-files.txt y "
        "manifest.documentation_files no coinciden"
    )
print("Candidatos funcionales validados:")
for path in sorted(functional):
    print(f"- {path}")
PY

echo
echo "Generado en: documentation/output"
echo "Respuesta: documentation/output/documentation-export-response.json"
