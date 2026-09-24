#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/sonar-scanner-common.sh"
ARCH="${1:-$(sbm_sonar_detect_arch)}"

case "${ARCH}" in
  x86_64|amd64)
    TARGETARCH="amd64"
    ;;
  arm64|aarch64)
    TARGETARCH="arm64"
    ;;
  *)
    echo "Unsupported architecture: ${ARCH}" >&2
    exit 1
    ;;
esac

IMAGE_TAG="sbm-sonar-scanner:${TARGETARCH}"
DOCKERFILE="${ROOT_DIR}/docker/sonar-scanner/Dockerfile"

DOCKERFILE_HASH="$(sbm_sonar_dockerfile_hash)"

if [[ -n "${MSYSTEM:-}" ]]; then
  DOCKERFILE_FOR_DOCKER="$(cygpath -am -- "${DOCKERFILE}")"
  ROOT_DIR_FOR_DOCKER="$(cygpath -am -- "${ROOT_DIR}")"
  MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
    docker build --platform "linux/${TARGETARCH}" -t "${IMAGE_TAG}" \
      --label "com.sbm.sonar-scanner.dockerfile-sha256=${DOCKERFILE_HASH}" \
      -f "${DOCKERFILE_FOR_DOCKER}" "${ROOT_DIR_FOR_DOCKER}"
else
  docker build --platform "linux/${TARGETARCH}" -t "${IMAGE_TAG}" \
    --label "com.sbm.sonar-scanner.dockerfile-sha256=${DOCKERFILE_HASH}" \
    -f "${DOCKERFILE}" "${ROOT_DIR}"
fi

echo "Built ${IMAGE_TAG} for linux/${TARGETARCH}"
