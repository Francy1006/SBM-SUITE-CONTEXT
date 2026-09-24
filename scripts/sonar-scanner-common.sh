#!/usr/bin/env bash
SBM_SONAR_HELPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SBM_SONAR_TIMEOUT_SECONDS="${SBM_SONAR_TIMEOUT_SECONDS:-1800}"

sbm_sonar_detect_arch() {
  local docker_arch=""

  if command -v docker >/dev/null 2>&1; then
    docker_arch="$(docker version --format '{{.Server.Arch}}' 2>/dev/null || true)"
    if [[ -z "${docker_arch}" ]]; then
      docker_arch="$(docker info --format '{{.Architecture}}' 2>/dev/null || true)"
    fi

    case "${docker_arch}" in
      x86_64|amd64|x64)
        echo "amd64"
        return 0
        ;;
      arm64|aarch64|arm64v8|arm64e)
        echo "arm64"
        return 0
        ;;
    esac
  fi

  local uname_arch
  uname_arch="$(uname -m 2>/dev/null || true)"
  case "${uname_arch}" in
    x86_64|amd64|x64)
      echo "amd64"
      return 0
      ;;
    arm64|aarch64|arm64v8|arm64e)
      echo "arm64"
      return 0
      ;;
  esac

  echo "ERROR: Arquitectura de Docker no soportada: ${docker_arch:-${uname_arch:-unknown}}" >&2
  return 1
}

sbm_sonar_platform() {
  local arch
  arch="$(sbm_sonar_detect_arch)"
  echo "linux/${arch}"
}

sbm_sonar_cache_dir() {
  local project_root="${1:?Falta project_root}"
  local arch="${2:-$(sbm_sonar_detect_arch)}"
  echo "${project_root}/.sonar/cache/${arch}"
}

sbm_sonar_image() {
  local arch
  arch="$(sbm_sonar_detect_arch)" || return
  printf 'sbm-sonar-scanner:%s\n' "${arch}"
}


# Python is already required by the scanner timeout controller.
# Read stdin so Git Bash paths do not need conversion for Windows Python.
sbm_sonar_dockerfile_hash() {
  python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())' \
    < "${SBM_SONAR_HELPER_DIR}/../docker/sonar-scanner/Dockerfile"
}

sbm_sonar_image_hash() {
  docker image inspect --format '{{ index .Config.Labels "com.sbm.sonar-scanner.dockerfile-sha256" }}' "$1"
}

sbm_sonar_msys_host_path() {
  cygpath -am -- "$1"
}

sbm_sonar_msys_volume() {
  local spec="$1" source remainder tail
  if [[ "${spec}" =~ ^[A-Za-z]:[/\\] ]]; then
    tail="${spec:2}"
    source="${spec:0:2}${tail%%:*}"
    remainder="${tail#*:}"
  elif [[ "${spec}" == /*:* || "${spec}" == ./*:* || "${spec}" == ../*:* ]]; then
    source="${spec%%:*}"
    remainder="${spec#*:}"
  else
    printf '%s\n' "${spec}"
    return 0
  fi
  printf '%s:%s\n' "$(sbm_sonar_msys_host_path "${source}")" "${remainder}"
}

# Reuse only images built from the current Dockerfile.

sbm_sonar_ensure_image() {
  local arch image actual_platform expected_hash actual_hash=""
  arch="$(sbm_sonar_detect_arch)" || return
  image="sbm-sonar-scanner:${arch}"

  expected_hash="$(sbm_sonar_dockerfile_hash)" || return
  if docker image inspect "${image}" >/dev/null 2>&1; then
    actual_hash="$(sbm_sonar_image_hash "${image}")" || return
  fi
  if [[ "${actual_hash}" != "${expected_hash}" ]]; then
    echo "SonarScanner: construyendo ${image}..." >&2
    bash "${SBM_SONAR_HELPER_DIR}/build-sonar-scanner-image.sh" "${arch}" >&2 || return
  fi

  actual_platform="$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "${image}")" || {
    echo "ERROR: No se pudo inspeccionar ${image}" >&2
    return 1
  }
  if [[ "${actual_platform}" != "linux/${arch}" ]]; then
    echo "ERROR: Arquitectura incorrecta para ${image}: ${actual_platform}; esperada linux/${arch}" >&2
    return 1
  fi
  actual_hash="$(sbm_sonar_image_hash "${image}")" || return
  if [[ "${actual_hash}" != "${expected_hash}" ]]; then
    echo "ERROR: Huella del Dockerfile incorrecta para ${image}: ${actual_hash}; esperada ${expected_hash}" >&2
    return 1
  fi
}

sbm_sonar_timeout_controller() {
  python3 - "$@" <<'PY'
import subprocess
import sys

try:
    timeout_seconds = int(sys.argv[1])
except ValueError:
    print("ERROR: SONAR_SCANNER_TIMEOUT_SECONDS debe ser un entero", file=sys.stderr)
    raise SystemExit(2)

cmd = sys.argv[2:]
if not cmd:
    print("ERROR: no command specified for SonarScanner", file=sys.stderr)
    raise SystemExit(2)

container_name = ""
for index, argument in enumerate(cmd):
    if argument == "--name" and index + 1 < len(cmd):
        container_name = cmd[index + 1]
        break
    if argument.startswith("--name="):
        container_name = argument.split("=", 1)[1]
        break

process = subprocess.Popen(cmd)
try:
    returncode = process.wait(timeout=timeout_seconds)
except subprocess.TimeoutExpired:
    try:
        process.terminate()
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)

    if container_name:
        subprocess.run(["docker", "rm", "-f", container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(
        f"ERROR: SonarScanner timed out after {timeout_seconds}s. The temporary container was terminated.",
        file=sys.stderr,
    )
    raise SystemExit(124)

raise SystemExit(returncode)
PY
}

sbm_sonar_run() {
  local timeout_seconds="${SONAR_SCANNER_TIMEOUT_SECONDS:-${SBM_SONAR_TIMEOUT_SECONDS}}"

  if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 es obligatorio para controlar el timeout del scanner" >&2
    return 1
  fi

  if [[ -z "${MSYSTEM:-}" ]]; then
    sbm_sonar_timeout_controller "${timeout_seconds}" "$@"
    return
  fi

  local converted=()
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      -v|--volume)
        converted+=("$1")
        shift
        [[ "$#" -gt 0 ]] || {
          echo "ERROR: -v/--volume requiere un volumen" >&2
          return 2
        }
        converted+=("$(sbm_sonar_msys_volume "$1")")
        ;;
      --volume=*)
        converted+=("--volume=$(sbm_sonar_msys_volume "${1#*=}")")
        ;;
      --env-file)
        converted+=("$1")
        shift
        [[ "$#" -gt 0 ]] || {
          echo "ERROR: --env-file requiere un path" >&2
          return 2
        }
        converted+=("$(sbm_sonar_msys_host_path "$1")")
        ;;
      --env-file=*)
        converted+=("--env-file=$(sbm_sonar_msys_host_path "${1#*=}")")
        ;;
      *)
        converted+=("$1")
        ;;
    esac
    shift
  done

  MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
    sbm_sonar_timeout_controller "${timeout_seconds}" "${converted[@]}"
}
