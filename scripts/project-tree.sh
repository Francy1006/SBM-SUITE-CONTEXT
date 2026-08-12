#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == "0" ]] || {
  echo "Uso: ./scripts/project-tree.sh" >&2
  exit 1
}

CONTEXT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "${CONTEXT_ROOT}/.." && pwd)"
OUTPUT_FILE="${CONTEXT_ROOT}/project-tree.txt"

EXCLUDED_NAMES=(
  ".git"
  ".venv"
  "venv"
  "node_modules"
  "__pycache__"
  "dist"
  "build"
  "coverage"
  "htmlcov"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  ".idea"
  ".vscode"
  "volumes"
)

EXCLUDED_FILE_PATTERNS=(
  ".env"
  ".env.*"
  "*.pyc"
  "*.pyo"
  "*.pyd"
  "*.so"
  "*.dylib"
  "*.dll"
  "*.exe"
  "*.bin"
  "*.class"
  "*.jar"
  "*.war"
  "*.zip"
  "*.tar"
  "*.tar.gz"
  "*.tgz"
  "*.7z"
  "*.rar"
  "*.png"
  "*.jpg"
  "*.jpeg"
  "*.gif"
  "*.webp"
  "*.ico"
  "*.pdf"
  "*.db"
  "*.sqlite"
  "*.sqlite3"
  "*.pem"
  "*.key"
  "*.crt"
  "*.cer"
  "*.p12"
  "*.pfx"
)

build_find_expression() {
  local expression=()
  local name

  for name in "${EXCLUDED_NAMES[@]}"; do
    expression+=(
      -name "${name}" -o
    )
  done

  unset 'expression[${#expression[@]}-1]'

  printf '%q ' "${expression[@]}"
}

build_file_exclusions() {
  local expression=()
  local pattern

  for pattern in "${EXCLUDED_FILE_PATTERNS[@]}"; do
    expression+=(
      -name "${pattern}" -o
    )
  done

  unset 'expression[${#expression[@]}-1]'

  printf '%q ' "${expression[@]}"
}

RELATIVE_ROOT="$(basename "${PROJECT_ROOT}")"
TEMP_FILE="$(mktemp)"
trap 'rm -f "${TEMP_FILE}"' EXIT

NAME_EXPRESSION="$(build_find_expression)"
FILE_EXCLUSIONS="$(build_file_exclusions)"

{
  printf '%s/\n' "${RELATIVE_ROOT}"

  eval find '"${PROJECT_ROOT}"' \
    -mindepth 1 \
    '\(' "${NAME_EXPRESSION}" '\)' -prune -o \
    -type f \
    '!' '\(' "${FILE_EXCLUSIONS}" '\)' \
    -print0 \
    | while IFS= read -r -d '' path; do
        relative_path="${path#"${PROJECT_ROOT}/"}"
        file_size="$(wc -c < "${path}" | tr -d ' ')"
        printf 'F\t%s\t%s\n' "${relative_path}" "${file_size}"
      done

  eval find '"${PROJECT_ROOT}"' \
    -mindepth 1 \
    '\(' "${NAME_EXPRESSION}" '\)' -prune -o \
    -type d \
    -print0 \
    | while IFS= read -r -d '' path; do
        relative_path="${path#"${PROJECT_ROOT}/"}"
        printf 'D\t%s\t-\n' "${relative_path}"
      done
} \
  | LC_ALL=C sort -t $'\t' -k2,2 \
  > "${TEMP_FILE}"

{
  printf '%s/\n' "${RELATIVE_ROOT}"

  while IFS=$'\t' read -r entry_type relative_path file_size; do
    [[ -n "${relative_path}" ]] || continue

    depth="$(
      awk -F'/' '{print NF}' <<< "${relative_path}"
    )"
    indent=""

    if [[ "${depth}" -gt 1 ]]; then
      indent="$(
        printf '%*s' "$(((depth - 1) * 2))" ''
      )"
    fi

    name="${relative_path##*/}"

    if [[ "${entry_type}" == "D" ]]; then
      printf '%s- %s/\n' "${indent}" "${name}"
    else
      printf '%s- %s [%s bytes]\n' \
        "${indent}" \
        "${name}" \
        "${file_size}"
    fi
  done < <(tail -n +2 "${TEMP_FILE}")
} > "${OUTPUT_FILE}"

echo "Project tree generado en: ${OUTPUT_FILE}"
