#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Uso: ./QA/qa-full.sh --branch <temporary-branch> --objectives-json '<array>' --sonarqube-ready" >&2
}

BRANCH=""
OBJECTIVES_JSON=""
SONAR_READY=0
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --branch) [[ "$#" -ge 2 ]] || { usage; exit 2; }; BRANCH="$2"; shift ;;
    --objectives-json) [[ "$#" -ge 2 ]] || { usage; exit 2; }; OBJECTIVES_JSON="$2"; shift ;;
    --sonarqube-ready) SONAR_READY=1 ;;
    *) usage; exit 2 ;;
  esac
  shift
done
[[ -n "${BRANCH}" && -n "${OBJECTIVES_JSON}" && "${SONAR_READY}" == "1" ]] || { usage; exit 2; }

QA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_ROOT="$(cd "${QA_DIR}/.." && pwd)"

context_python() {
  local candidate
  for candidate in \
    "${CONTEXT_ROOT}/.venv/Scripts/python.exe" \
    "${CONTEXT_ROOT}/.venv/Scripts/python3.exe" \
    "${CONTEXT_ROOT}/.venv/bin/python3" \
    "${CONTEXT_ROOT}/.venv/bin/python"
  do
    if [[ -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done
  echo "ERROR: Context requiere su propio Python en .venv/Scripts o .venv/bin" >&2
  return 1
}

CONTEXT_PYTHON="$(context_python)"
export PATH="$(dirname "${CONTEXT_PYTHON}"):${PATH}"
"${CONTEXT_PYTHON}" "${CONTEXT_ROOT}/scripts/git-flow-policy.py" describe "${BRANCH}" >/dev/null
"${CONTEXT_ROOT}/scripts/objective-branches.sh" verify "${BRANCH}"
NORMALIZED_IDS="$("${CONTEXT_PYTHON}" - "${OBJECTIVES_JSON}" <<'PY'
import json, sys
payload = json.loads(sys.argv[1])
if not isinstance(payload, list) or not payload:
    raise SystemExit("ERROR: objectives-json debe ser un array no vacío")
ids = [item.get("objective_id") if isinstance(item, dict) else None for item in payload]
if any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
    raise SystemExit("ERROR: objectives-json contiene IDs inválidos o duplicados")
sys.stdout.write(json.dumps(ids, ensure_ascii=False, separators=(",", ":")))
PY
)"

"${QA_DIR}/qa-context.sh"
"${QA_DIR}/qa-all.sh" --with-sonar --sonarqube-ready
STATE_SHA256="$("${CONTEXT_PYTHON}" "${CONTEXT_ROOT}/scripts/workflow-state.py" \
  --suite-root "$(cd "${CONTEXT_ROOT}/.." && pwd)" \
  --repository-helper "${CONTEXT_ROOT}/scripts/suite-repositories.py")"
mkdir -p "${QA_DIR}/output"
"${CONTEXT_PYTHON}" - "${QA_DIR}/output/finalization-gate.json" "${BRANCH}" "${NORMALIZED_IDS}" "${STATE_SHA256}" <<'PY'
import json, sys
from pathlib import Path
path, branch, ids, state_sha256 = sys.argv[1:]
Path(path).write_text(json.dumps({
    "branch": branch,
    "status": "passed",
    "mode": "full-suite-with-sonar",
    "objectives": json.loads(ids),
    "state_sha256": state_sha256,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
echo "QA completo registrado para ${BRANCH}."
