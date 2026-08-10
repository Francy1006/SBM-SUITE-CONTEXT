#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Uso: ./scripts/documentation-deploy.sh <project_name>"
}

[[ "$#" == "1" ]] || {
  usage >&2
  exit 1
}

PROJECT_NAME="$1"
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
FORMAT_CONTEXT_FILE="${DOCUMENTATION_ROOT}/FORMAT_CONTEXT.md"
SYSTEM_PROMPT_FILE="${DOCUMENTATION_ROOT}/SYS_PROMPT.md"
QA_RESULTS_FILE="${CONTEXT_ROOT}/QA_CONTEXT.md"
RESPONSE_FILE="${OUTPUT_DIR}/documentation-export-response.json"
PROJECT_TREE_SCRIPT="${CONTEXT_ROOT}/project-tree.sh"
PROJECT_TREE_FILE="${CONTEXT_ROOT}/project-tree.txt"

CONTRACT_FILE="$(mktemp)"
GLOBAL_CONTEXT_FILE="$(mktemp)"
trap 'rm -f "${CONTRACT_FILE}" "${GLOBAL_CONTEXT_FILE}"' EXIT

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

CANONICAL_PROJECT_PATH="$(
  python3 - "${CONTRACT_FILE}" "${PROJECT_NAME}" <<'PY'
import json
import sys
from pathlib import Path

contract = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
project_name = sys.argv[2]
projects = contract.get("canonical_projects")
if not isinstance(projects, dict) or project_name not in projects:
    raise SystemExit(f"ERROR: {project_name} no está publicado por Project Registry")
canonical = projects[project_name]
if not isinstance(canonical, str) or not canonical:
    raise SystemExit(f"ERROR: mapping canónico inválido para {project_name}")
print(canonical)
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
  PROJECT_QA_RESULTS_FILE="${PROJECT_ROOT}/qa-results.md"
  PROJECT_QA_CONTEXT_FILE="${PROJECT_ROOT}/QA_CONTEXT.md"
else
  PROJECT_QA_RESULTS_FILE="${PROJECT_ROOT}/context/qa-results.md"
  PROJECT_QA_CONTEXT_FILE="${PROJECT_ROOT}/context/QA_CONTEXT.md"
fi

[[ -f "${FORMAT_CONTEXT_FILE}" ]] || {
  echo "ERROR: No existe ${FORMAT_CONTEXT_FILE}"
  exit 1
}

[[ -f "${SYSTEM_PROMPT_FILE}" ]] || {
  echo "ERROR: No existe ${SYSTEM_PROMPT_FILE}"
  exit 1
}
[[ -x "${PROJECT_TREE_SCRIPT}" ]] || {
  echo "ERROR: ${PROJECT_TREE_SCRIPT} no está disponible/ejecutable"
  exit 1
}

mkdir -p "${INPUT_DIR}" "${OUTPUT_DIR}"

find "${INPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete
find "${OUTPUT_DIR}" -mindepth 1 ! -name ".gitkeep" -delete

cd "${CONTEXT_ROOT}"
"${PROJECT_TREE_SCRIPT}"
[[ -f "${PROJECT_TREE_FILE}" ]] || {
  echo "ERROR: No se generó ${PROJECT_TREE_FILE}"
  exit 1
}

python3 - \
  "${CONTEXT_ROOT}/PROJECT_CONTEXT.md" \
  "${CONTEXT_ROOT}/COMPLETED_OBJECTIVES.md" \
  "${PROJECT_TREE_FILE}" \
  "${DOCUMENTATION_ROOT}/pages" \
  "${GLOBAL_CONTEXT_FILE}" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

project_context_path, completed_path, tree_path, pages_path, output_path = map(
    Path, sys.argv[1:]
)

def read_required(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"ERROR: Context evidence inválida: {path}")
    return path.read_text(encoding="utf-8")

def section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\s*$.*?(?=^##\s+|\Z)",
        markdown,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise SystemExit(f"ERROR: Falta sección global obligatoria: {heading}")
    return match.group(0).strip()

project_context = read_required(project_context_path)
completed_context = read_required(completed_path)
project_tree = read_required(tree_path).strip()

evidence = [
    (
        "SBM-SUITE/context/PROJECT_CONTEXT.md",
        "## 3. Active objectives",
        section(project_context, "## 3. Active objectives"),
    ),
    (
        "SBM-SUITE/context/PROJECT_CONTEXT.md",
        "## 4. Pending objectives",
        section(project_context, "## 4. Pending objectives"),
    ),
    (
        "SBM-SUITE/context/COMPLETED_OBJECTIVES.md",
        "## 1. Completed objectives by project",
        section(completed_context, "## 1. Completed objectives by project"),
    ),
]
if project_tree:
    evidence.append(
        (
            "SBM-SUITE/context/project-tree.txt",
            "Global project tree",
            project_tree,
        )
    )

chunks = []
for index, (archive_path, heading, content) in enumerate(evidence, start=1):
    point_id = hashlib.sha256(
        f"{archive_path}\0{heading}\0{content}".encode("utf-8")
    ).hexdigest()
    chunks.append({
        "point_id": point_id,
        "source_path": archive_path,
        "archive_path": archive_path,
        "section": heading,
        "score": 1.0 - (index - 1) * 0.001,
        "content": content,
    })

targets = []
for path in sorted(pages_path.rglob("*.md")):
    markdown = read_required(path)
    if re.search(r"^## (?:11\. Pending work|12\. Roadmap)\s*$", markdown, re.MULTILINE):
        relative = path.relative_to(pages_path.parent).as_posix()
        targets.append(f"documentation/{relative}")

if not targets:
    raise SystemExit("ERROR: No hay páginas autorizadas de roadmap/pending work")

objective_rows = []
for _, _, content in evidence[:3]:
    for line in content.splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("|")
            and not re.match(r"^\|\s*(?:ID|Objective ID|---)", stripped)
        ):
            objective_rows.append(stripped)

summary = (
    "Reconcile Documentation against the complete current global Context objective "
    "state across every registered project. Context is authoritative; Documentation "
    "may lag. Preserve unrelated documentation. Current objective rows:\n"
    + ("\n".join(objective_rows) if objective_rows else "No objective data rows.")
)

Path(output_path).write_text(
    json.dumps(
        {"chunks": chunks, "documentation_targets": targets, "summary": summary},
        ensure_ascii=False,
    ),
    encoding="utf-8",
)
PY

GIT_DIFF="$(
  {
    git -C "${PROJECT_ROOT}" diff --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" diff --cached --no-ext-diff -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
  } 2>/dev/null
)"

CHANGED_FILES="$(
  {
    git -C "${PROJECT_ROOT}" diff --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" diff --cached --name-only -- . \
      ':(exclude).env' ':(exclude).env.*' ':(exclude)**/.env' ':(exclude)**/.env.*'
    git -C "${PROJECT_ROOT}" ls-files --others --exclude-standard
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

GLOBAL_RECONCILIATION_SUMMARY="$(
  python3 - "${GLOBAL_CONTEXT_FILE}" <<'PY'
import json
import sys
from pathlib import Path

print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["summary"])
PY
)"
CHANGE_SUMMARY="${CHANGE_SUMMARY} ${GLOBAL_RECONCILIATION_SUMMARY}"

if [[ -f "${PROJECT_QA_RESULTS_FILE}" ]]; then
  QA_RESULTS="$(cat "${PROJECT_QA_RESULTS_FILE}")"
elif [[ -f "${PROJECT_QA_CONTEXT_FILE}" ]]; then
  QA_RESULTS="$(cat "${PROJECT_QA_CONTEXT_FILE}")"
elif [[ -f "${QA_RESULTS_FILE}" ]]; then
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
  GLOBAL_CONTEXT_FILE="${GLOBAL_CONTEXT_FILE}" \
  python3 <<'PY'
import json
import os
from pathlib import Path

changed_files = [
    line.strip()
    for line in os.environ["CHANGED_FILES"].splitlines()
    if line.strip()
]

global_context = json.loads(
    Path(os.environ["GLOBAL_CONTEXT_FILE"]).read_text(encoding="utf-8")
)

print(json.dumps({
    "project_name": os.environ["PROJECT_NAME"],
    "workflow": "documentation-deploy",
    "change_summary": os.environ["CHANGE_SUMMARY"],
    "changed_files": changed_files,
    "git_diff": os.environ["GIT_DIFF"],
    "qa_results": os.environ["QA_RESULTS"],
    "retrieved_context_chunks": global_context["chunks"],
    "documentation_targets": global_context["documentation_targets"],
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

python3 - "${RESPONSE_FILE}" "${PROJECT_NAME}" <<'PY'
import json
import sys
from pathlib import Path

response_path = Path(sys.argv[1])
payload = json.loads(response_path.read_text(encoding="utf-8"))
project_name = sys.argv[2]

if payload.get("status") != "completed":
    raise SystemExit("ERROR: La exportación no terminó con status=completed")
if payload.get("workflow") != "documentation-deploy":
    raise SystemExit("ERROR: La respuesta no corresponde a documentation-deploy")
if payload.get("project_name") != project_name:
    raise SystemExit("ERROR: La respuesta no corresponde al proyecto solicitado")
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
