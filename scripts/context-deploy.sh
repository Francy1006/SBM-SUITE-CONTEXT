#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Uso:
  ./scripts/context-deploy.sh <project_name> planning-activation '<objectives-json-array>' [user_prompt]
  ./scripts/context-deploy.sh <project_name> implementation-progress '<objectives-json-array>' [user_prompt]
  ./scripts/context-deploy.sh <project_name> implementation-closure '<objectives-json-array>' [user_prompt]

planning-activation:
  - acepta uno o más objetivos;
  - cada objetivo requiere: objective_id, objective, status, priority, target_date, branch.

implementation-progress / implementation-closure:
  - actualmente requieren exactamente un objetivo.
EOF
}

[[ "$#" -ge 3 && "$#" -le 4 ]] || {
  usage >&2
  exit 1
}

PROJECT_NAME="$1"
LIFECYCLE_PHASE="$2"
OBJECTIVES_JSON="$3"
USER_PROMPT="${4:-}"

if [[ -n "${USER_PROMPT//[[:space:]]/}" ]]; then
  EXECUTION_MODE="user-guided"
else
  EXECUTION_MODE="evidence"
fi

case "${LIFECYCLE_PHASE}" in
  planning-activation|implementation-progress|implementation-closure) ;;
  *)
    echo "ERROR: Fase no válida: ${LIFECYCLE_PHASE}" >&2
    usage >&2
    exit 1
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SBM_SUITE_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
cd "${CONTEXT_ROOT}"

INPUT_DIR="${CONTEXT_ROOT}/input"
OUTPUT_DIR="${CONTEXT_ROOT}/output"
PROMPT_TEMPLATE="${CONTEXT_ROOT}/SYS_PROMPT.md"
FORMAT_CONTEXT_FILE="${CONTEXT_ROOT}/FORMAT_CONTEXT.md"
PROJECT_TREE_SCRIPT="${CONTEXT_ROOT}/project-tree.sh"
PROJECT_TREE_FILE="${CONTEXT_ROOT}/project-tree.txt"
SYSTEM_PROMPT_FILE="${OUTPUT_DIR}/SYS_PROMPT.md"
RESPONSE_FILE="${OUTPUT_DIR}/context-export-response.json"

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

[[ -f "${PROMPT_TEMPLATE}" ]] || {
  echo "ERROR: No existe ${PROMPT_TEMPLATE}" >&2
  exit 1
}
[[ -f "${FORMAT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe ${FORMAT_CONTEXT_FILE}" >&2
  exit 1
}
[[ -x "${PROJECT_TREE_SCRIPT}" ]] || {
  echo "ERROR: ${PROJECT_TREE_SCRIPT} no está disponible/ejecutable" >&2
  exit 1
}

NORMALIZED_OBJECTIVES="$(
  python3 - "${OBJECTIVES_JSON}" "${LIFECYCLE_PHASE}" <<'PY'
import json
import re
import sys
from datetime import date

raw, phase = sys.argv[1:]
try:
    objectives = json.loads(raw)
except json.JSONDecodeError as exc:
    raise SystemExit(f"ERROR: objectives debe ser JSON válido: {exc}") from exc

if not isinstance(objectives, list) or not objectives:
    raise SystemExit("ERROR: objectives debe ser un array no vacío")

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
normalized = []
for index, objective in enumerate(objectives, start=1):
    if not isinstance(objective, dict):
        raise SystemExit(f"ERROR: objectives[{index}] debe ser un objeto")

    objective_id = objective.get("objective_id")
    if not isinstance(objective_id, str) or not id_pattern.fullmatch(objective_id):
        raise SystemExit(f"ERROR: objectives[{index}].objective_id inválido")
    ids.append(objective_id)

    if phase == "planning-activation":
        missing = sorted(required_planning - set(objective))
        if missing:
            raise SystemExit(
                f"ERROR: objectives[{index}] no contiene: " + ", ".join(missing)
            )

        description = objective.get("objective")
        status = objective.get("status")
        priority = objective.get("priority")
        target_date = objective.get("target_date")
        branch = objective.get("branch")

        if not isinstance(description, str) or not description.strip():
            raise SystemExit(f"ERROR: objectives[{index}].objective es obligatorio")
        if status not in {"active", "pending"}:
            raise SystemExit(f"ERROR: objectives[{index}].status debe ser active o pending")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 5:
            raise SystemExit(f"ERROR: objectives[{index}].priority debe ser 0-5")
        if target_date != "N/A":
            if not isinstance(target_date, str):
                raise SystemExit(
                    f"ERROR: objectives[{index}].target_date debe ser YYYY-MM-DD o N/A"
                )
            try:
                date.fromisoformat(target_date)
            except ValueError as exc:
                raise SystemExit(
                    f"ERROR: objectives[{index}].target_date debe ser YYYY-MM-DD o N/A"
                ) from exc
        if not isinstance(branch, str) or not branch_pattern.fullmatch(branch):
            raise SystemExit(
                f"ERROR: objectives[{index}].branch debe usar "
                "FEATURE|BUGFIX|HOTFIX y máximo 4 palabras"
            )

    normalized.append(objective)

if len(ids) != len(set(ids)):
    raise SystemExit("ERROR: objectives contiene objective_id duplicados")

if phase != "planning-activation" and len(normalized) != 1:
    raise SystemExit(f"ERROR: {phase} actualmente requiere exactamente un objetivo")

print(json.dumps(normalized, ensure_ascii=False, separators=(",", ":")))
PY
)"

CONTRACT_FILE="$(mktemp)"
META_FILE="$(mktemp)"
trap 'rm -f "${CONTRACT_FILE}" "${META_FILE}"' EXIT

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
  "${CONTRACT_FILE}" \
  "${PROJECT_NAME}" \
  "${LIFECYCLE_PHASE}" \
  "${META_FILE}" <<'PY'
import json
import sys
from pathlib import Path

contract_path, project, phase, meta_path = sys.argv[1:]
contract = json.loads(Path(contract_path).read_text(encoding="utf-8"))

version = contract.get("contract_version")
phases = contract.get("lifecycle_phases")
projects = contract.get("canonical_projects")
patches = contract.get("supported_patch_paths")

if not isinstance(version, str) or not version:
    raise SystemExit("ERROR: contract_version inválido")
if not isinstance(phases, list) or phase not in phases:
    raise SystemExit(f"ERROR: lifecycle phase no publicada: {phase}")
if not isinstance(projects, dict) or project not in projects:
    raise SystemExit(f"ERROR: {project} no está publicado por Project Registry")
canonical_project_path = projects[project]
if not isinstance(canonical_project_path, str) or not canonical_project_path:
    raise SystemExit(f"ERROR: mapping canónico inválido para {project}")
if not isinstance(patches, list):
    raise SystemExit("ERROR: supported_patch_paths inválido")

required = {"patches/global-project-context.json"}
if project != "sbm-suite-context":
    required.add("patches/project-context.json")
if phase == "implementation-closure":
    required |= {
        "patches/completed-objectives.json",
        "patches/global-qa-context.json",
    }
    if project != "sbm-suite-context":
        required.add("patches/project-qa-context.json")

missing = sorted(required - set(patches))
if missing:
    raise SystemExit("ERROR: contrato incompleto: " + ", ".join(missing))

Path(meta_path).write_text(
    json.dumps({
        "contract_version": version,
        "canonical_project_path": canonical_project_path,
    }),
    encoding="utf-8",
)
print(f"Contrato validado: {version} ({canonical_project_path})")
PY

CANONICAL_PROJECT_PATH="$(
  python3 - "${META_FILE}" <<'PY'
import json
import sys
from pathlib import Path

print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["canonical_project_path"])
PY
)"

PROJECT_ROOT="$(
  python3 - "${SBM_SUITE_ROOT}" "${CANONICAL_PROJECT_PATH}" <<'PY'
import os
import sys
from pathlib import Path, PurePosixPath

suite_root = Path(sys.argv[1]).resolve(strict=True)
canonical = PurePosixPath(sys.argv[2])
if canonical.is_absolute() or ".." in canonical.parts:
    raise SystemExit("ERROR: canonical_project_path no es seguro")
if not canonical.parts or canonical.parts[0] != suite_root.name:
    raise SystemExit("ERROR: canonical_project_path no pertenece a SBM-SUITE")
candidate = (suite_root.parent / Path(*canonical.parts)).resolve(strict=True)
if os.path.commonpath((suite_root, candidate)) != str(suite_root):
    raise SystemExit("ERROR: PROJECT_ROOT escapa de SBM-SUITE")
if not candidate.is_dir():
    raise SystemExit("ERROR: PROJECT_ROOT no es un directorio")
print(candidate)
PY
)"

if [[ "${PROJECT_NAME}" == "sbm-suite-context" ]]; then
  QA_RESULTS_FILE="${PROJECT_ROOT}/qa-results.md"
else
  QA_RESULTS_FILE="${PROJECT_ROOT}/context/qa-results.md"
fi

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"
find "${INPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete
find "${OUTPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete

python3 - \
  "${PROMPT_TEMPLATE}" \
  "${SYSTEM_PROMPT_FILE}" \
  "${META_FILE}" \
  "${PROJECT_NAME}" \
  "${LIFECYCLE_PHASE}" \
  "${EXECUTION_MODE}" <<'PY'
import json
import re
import sys
from pathlib import Path

src, dst, meta, project, phase, execution_mode = sys.argv[1:]
version = json.loads(Path(meta).read_text(encoding="utf-8"))["contract_version"]
text = Path(src).read_text(encoding="utf-8")

for key, value in {
    "{{PROJECT_NAME}}": project,
    "{{CONTRACT_VERSION}}": version,
    "{{LIFECYCLE_PHASE}}": phase,
    "{{EXECUTION_MODE}}": execution_mode,
}.items():
    text = text.replace(key, value)

if re.search(r"\{\{[A-Z0-9_]+\}\}", text):
    raise SystemExit("ERROR: SYS_PROMPT.md conserva placeholders sin resolver")

Path(dst).write_text(text, encoding="utf-8")
PY

"${PROJECT_TREE_SCRIPT}"
[[ -f "${PROJECT_TREE_FILE}" ]] || {
  echo "ERROR: No se generó ${PROJECT_TREE_FILE}" >&2
  exit 1
}

GIT_DIFF="$(
  {
    git -C "${PROJECT_ROOT}" diff --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' \
      ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" diff --cached --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' \
      ':(exclude)**/.env' ':(exclude)**/.env.*'
  } 2>/dev/null
)"

CHANGED_FILES="$(
  {
    git -C "${PROJECT_ROOT}" diff --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' \
      ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" diff --cached --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' \
      ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" ls-files --others --exclude-standard
  } 2>/dev/null \
    | awk '!/(^|\/)\.env($|\.)/' \
    | sort -u
)"

if [[ -n "${CHANGED_FILES}" ]]; then
  CHANGE_SUMMARY="Current ${PROJECT_NAME} changes affect: $(printf '%s\n' "${CHANGED_FILES}" | awk 'NF' | paste -sd ',' - | sed 's/,/, /g')."
else
  CHANGE_SUMMARY="No uncommitted changes detected in ${PROJECT_NAME}."
fi

QA_RESULTS=""
[[ -f "${QA_RESULTS_FILE}" ]] && QA_RESULTS="$(cat "${QA_RESULTS_FILE}")"

if [[ "${LIFECYCLE_PHASE}" == "implementation-closure" && -z "${QA_RESULTS//[[:space:]]/}" ]]; then
  echo "ERROR: implementation-closure requiere ${QA_RESULTS_FILE}" >&2
  exit 1
fi

PAYLOAD="$(
  PROJECT_NAME="${PROJECT_NAME}" \
  LIFECYCLE_PHASE="${LIFECYCLE_PHASE}" \
  EXECUTION_MODE="${EXECUTION_MODE}" \
  OBJECTIVES_JSON="${NORMALIZED_OBJECTIVES}" \
  USER_PROMPT="${USER_PROMPT}" \
  CHANGE_SUMMARY="${CHANGE_SUMMARY}" \
  CHANGED_FILES="${CHANGED_FILES}" \
  GIT_DIFF="${GIT_DIFF}" \
  QA_RESULTS="${QA_RESULTS}" \
  python3 <<'PY'
import json
import os

print(json.dumps({
    "project_name": os.environ["PROJECT_NAME"],
    "workflow": "context-deploy",
    "lifecycle_phase": os.environ["LIFECYCLE_PHASE"],
    "execution_mode": os.environ["EXECUTION_MODE"],
    "objectives": json.loads(os.environ["OBJECTIVES_JSON"]),
    "user_prompt": os.environ["USER_PROMPT"] or None,
    "change_summary": os.environ["CHANGE_SUMMARY"],
    "changed_files": [
        value
        for value in os.environ["CHANGED_FILES"].splitlines()
        if value.strip()
    ],
    "git_diff": os.environ["GIT_DIFF"],
    "qa_results": os.environ["QA_RESULTS"],
}, ensure_ascii=False))
PY
)"

printf '%s' "${PAYLOAD}" \
  | curl --fail-with-body --silent --show-error \
      --request POST "${AI_ASSISTANT_URL%/}/contexts/export" \
      --header "Content-Type: application/json" \
      --data-binary @- \
      --output "${RESPONSE_FILE}"

python3 - \
  "${RESPONSE_FILE}" \
  "${PROJECT_NAME}" \
  "${LIFECYCLE_PHASE}" \
  "${EXECUTION_MODE}" \
  "${NORMALIZED_OBJECTIVES}" <<'PY'
import json
import sys
from pathlib import Path

response = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
project, phase, execution_mode = sys.argv[2:5]
requested = json.loads(sys.argv[5])

if response.get("status") != "completed" or response.get("workflow") != "context-deploy":
    raise SystemExit("ERROR: context-deploy no terminó correctamente")
if response.get("project_name") != project or response.get("lifecycle_phase") != phase:
    raise SystemExit("ERROR: respuesta no coincide con proyecto/fase")
if response.get("execution_mode") != execution_mode:
    raise SystemExit("ERROR: respuesta no coincide con execution_mode solicitado")
if response.get("objectives") != requested:
    raise SystemExit("ERROR: respuesta no coincide con objectives[] solicitado")
if response.get("errors") not in ([], None):
    raise SystemExit(f"ERROR: backend informó errores: {response.get('errors')}")

print("Exportación de contexto completada.")
print(f"Proyecto: {project}")
print(f"Fase: {phase}")
print(f"Modo: {execution_mode}")
print("Objetivos: " + ", ".join(
    objective["objective_id"] for objective in requested
))
print("Paquete: output/context-deploy-package.zip")
PY
