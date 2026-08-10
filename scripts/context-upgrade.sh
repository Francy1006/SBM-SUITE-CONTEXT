#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SBM_SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
cd "${CONTEXT_ROOT}"

PROJECT_NAME="sbm-suite-context"
EXPECTED_CANONICAL_PROJECT_PATH="SBM-SUITE/context"

INPUT_DIR="${CONTEXT_ROOT}/input"
OUTPUT_DIR="${CONTEXT_ROOT}/output"
UPGRADE_ZIP="${INPUT_DIR}/context-upgrade.zip"
RESPONSE_FILE="${OUTPUT_DIR}/context-upgrade-response.json"

get_env() {
  local file="$1"
  local key="$2"
  awk -v key="${key}" '
    index($0, key "=") == 1 { value = substr($0, length(key) + 2) }
    END {
      sub(/\r$/, "", value)
      sub(/^"/, "", value)
      sub(/"$/, "", value)
      printf "%s", value
    }
  ' "${file}"
}

if [[ -z "${AI_ASSISTANT_URL:-}" ]]; then
  for candidate in \
    "${CONTEXT_ROOT}/.env.dev" \
    "${SBM_SUITE_ROOT}/SBM/sbm-ai-assistant/.env.dev" \
    "${SBM_SUITE_ROOT}/sbm/sbm-ai-assistant/.env.dev"
  do
    if [[ -f "${candidate}" ]]; then
      AI_ASSISTANT_URL="$(get_env "${candidate}" AI_ASSISTANT_URL)"
      break
    fi
  done
fi

[[ -n "${AI_ASSISTANT_URL:-}" ]] || {
  echo "ERROR: Falta AI_ASSISTANT_URL; expórtala o configúrala en sbm-ai-assistant/.env.dev" >&2
  exit 1
}
[[ -d "${INPUT_DIR}" ]] || {
  echo "ERROR: No existe ${INPUT_DIR}" >&2
  exit 1
}
[[ -f "${UPGRADE_ZIP}" ]] || {
  echo "ERROR: No existe ${UPGRADE_ZIP}" >&2
  exit 1
}

ZIP_COUNT="$(find "${INPUT_DIR}" -maxdepth 1 -type f -name '*.zip' | wc -l | tr -d ' ')"
[[ "${ZIP_COUNT}" == "1" ]] || {
  echo "ERROR: Debe existir exactamente un ZIP en ${INPUT_DIR}" >&2
  exit 1
}

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
  echo "ERROR: /contexts/contract HTTP ${HTTP_STATUS}" >&2
  exit 1
}

python3 - \
  "${UPGRADE_ZIP}" \
  "${CONTRACT_FILE}" \
  "${PROJECT_NAME}" \
  "${EXPECTED_CANONICAL_PROJECT_PATH}" <<'PY'
import json
import re
import sys
from datetime import date
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

zip_path, contract_path, project_name, expected_canonical = sys.argv[1:]

try:
    contract = json.loads(open(contract_path, encoding="utf-8").read())
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: Contrato inválido: {exc}") from exc

try:
    with ZipFile(zip_path) as archive:
        names = archive.namelist()
        if "manifest.json" not in names:
            raise SystemExit("ERROR: context-upgrade.zip no contiene manifest.json")
        if len(names) != len(set(names)):
            raise SystemExit("ERROR: context-upgrade.zip contiene rutas duplicadas")
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name:
                raise SystemExit(f"ERROR: Ruta ZIP no relativa/segura: {name}")
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
except (BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: context-upgrade.zip inválido: {exc}") from exc

if manifest.get("project_name") != project_name:
    raise SystemExit("ERROR: manifest.project_name no coincide")
if manifest.get("workflow") != "context-upgrade":
    raise SystemExit("ERROR: manifest.workflow debe ser context-upgrade")
if manifest.get("contract_version") != contract.get("contract_version"):
    raise SystemExit("ERROR: contract_version no coincide con el backend")

execution_mode = manifest.get("execution_mode")
if execution_mode not in {"evidence", "user-guided"}:
    raise SystemExit("ERROR: manifest.execution_mode inválido")

user_prompt_file = manifest.get("user_prompt_file")
if execution_mode == "evidence" and user_prompt_file is not None:
    raise SystemExit("ERROR: evidence requiere user_prompt_file=null")
if execution_mode == "user-guided" and user_prompt_file != "USER_PROMPT.md":
    raise SystemExit("ERROR: user-guided requiere USER_PROMPT.md")

phase = manifest.get("lifecycle_phase")
phases = contract.get("lifecycle_phases")
if not isinstance(phases, list) or phase not in phases:
    raise SystemExit("ERROR: lifecycle_phase no soportada")

projects = contract.get("canonical_projects")
if not isinstance(projects, dict) or projects.get(project_name) != expected_canonical:
    raise SystemExit("ERROR: mapping canónico del proyecto no coincide")
if manifest.get("canonical_project_path") != expected_canonical:
    raise SystemExit("ERROR: manifest.canonical_project_path no coincide")

objectives = manifest.get("objectives")
if not isinstance(objectives, list) or not objectives:
    raise SystemExit("ERROR: manifest.objectives debe ser un array no vacío")

id_pattern = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
branch_pattern = re.compile(
    r"^(FEATURE|BUGFIX|HOTFIX)-[a-z0-9]+(?:-[a-z0-9]+){0,3}$"
)
required_planning = {
    "objective_id",
    "objective",
    "status",
    "priority",
    "target_date",
    "branch",
}

ids = []
for index, objective in enumerate(objectives, start=1):
    if not isinstance(objective, dict):
        raise SystemExit(f"ERROR: manifest.objectives[{index}] debe ser objeto")

    objective_id = objective.get("objective_id")
    if not isinstance(objective_id, str) or not id_pattern.fullmatch(objective_id):
        raise SystemExit(f"ERROR: manifest.objectives[{index}].objective_id inválido")
    ids.append(objective_id)

    if phase == "planning-activation":
        missing = sorted(required_planning - set(objective))
        if missing:
            raise SystemExit(
                f"ERROR: manifest.objectives[{index}] incompleto: "
                + ", ".join(missing)
            )
        if not isinstance(objective.get("objective"), str) or not objective["objective"].strip():
            raise SystemExit(f"ERROR: manifest.objectives[{index}].objective inválido")
        if objective.get("status") not in {"active", "pending"}:
            raise SystemExit(f"ERROR: manifest.objectives[{index}].status inválido")

        priority = objective.get("priority")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 5:
            raise SystemExit(f"ERROR: manifest.objectives[{index}].priority inválido")

        target_date = objective.get("target_date")
        if target_date != "N/A":
            if not isinstance(target_date, str):
                raise SystemExit(f"ERROR: manifest.objectives[{index}].target_date inválido")
            try:
                date.fromisoformat(target_date)
            except ValueError as exc:
                raise SystemExit(
                    f"ERROR: manifest.objectives[{index}].target_date inválido"
                ) from exc

        branch = objective.get("branch")
        if not isinstance(branch, str) or not branch_pattern.fullmatch(branch):
            raise SystemExit(f"ERROR: manifest.objectives[{index}].branch inválido")

if len(ids) != len(set(ids)):
    raise SystemExit("ERROR: manifest.objectives contiene IDs duplicados")
if phase != "planning-activation" and len(objectives) != 1:
    raise SystemExit(f"ERROR: {phase} actualmente requiere exactamente un objetivo")

if manifest.get("output_filename") != "context-upgrade.zip":
    raise SystemExit("ERROR: manifest.output_filename debe ser context-upgrade.zip")

generated_patches = {
    name for name in names if name.startswith("patches/") and name.endswith(".json")
}
required_patches = {"patches/global-project-context.json"}
if phase == "implementation-closure":
    required_patches |= {
        "patches/completed-objectives.json",
        "patches/global-qa-context.json",
    }

missing_patches = sorted(required_patches - generated_patches)
if missing_patches:
    raise SystemExit(
        "ERROR: faltan patches requeridos para SBM-SUITE/context: "
        + ", ".join(missing_patches)
    )

for forbidden in {
    "patches/project-context.json",
    "patches/project-qa-context.json",
    "patches/project-deploy-context.json",
    "patches/project-readme.json",
}:
    if forbidden in generated_patches:
        raise SystemExit(
            f"ERROR: {forbidden} no aplica a SBM-SUITE/context"
        )

print(f"Preflight validado: {phase}")
print(f"Modo: {execution_mode}")
print("Objetivos: " + ", ".join(ids))
PY

mkdir -p "${OUTPUT_DIR}"

HTTP_STATUS="$(
  curl --silent --show-error \
    --output "${RESPONSE_FILE}" \
    --write-out "%{http_code}" \
    --request POST \
    "${AI_ASSISTANT_URL%/}/contexts/upgrade"
)"

[[ "${HTTP_STATUS}" == "200" ]] || {
  echo "ERROR: context-upgrade HTTP ${HTTP_STATUS}" >&2
  [[ -f "${RESPONSE_FILE}" ]] && cat "${RESPONSE_FILE}" >&2
  exit 1
}

python3 - "${RESPONSE_FILE}" "${PROJECT_NAME}" <<'PY'
import json
import sys
from pathlib import Path, PurePosixPath

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
project_name = sys.argv[2]

if payload.get("project_name") != project_name:
    raise SystemExit("ERROR: response.project_name no coincide")
if payload.get("workflow") != "context-upgrade":
    raise SystemExit("ERROR: response.workflow no coincide")
if payload.get("errors") not in ([], None):
    raise SystemExit(f"ERROR: backend informó errores: {payload.get('errors')}")
if payload.get("input_cleaned") is not True:
    raise SystemExit("ERROR: input no fue limpiado")

for field in ("backup_directory", "commit_message_file", "executive_readme_file"):
    value = payload.get(field)
    if not value:
        continue
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"ERROR: response.{field} debe ser relativo")

print("Contextos actualizados correctamente.")
print("Archivos actualizados:")
for path in payload.get("updated_files", []):
    print(f"- {path}")
print(f"Backup: {payload.get('backup_directory')}")
PY

[[ ! -e "${UPGRADE_ZIP}" ]] || {
  echo "ERROR: context-upgrade.zip no fue eliminado" >&2
  exit 1
}
