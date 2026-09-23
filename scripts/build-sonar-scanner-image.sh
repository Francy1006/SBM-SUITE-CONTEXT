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

docker build --platform "linux/${TARGETARCH}" -t "${IMAGE_TAG}" --label "com.sbm.sonar-scanner.dockerfile-sha256=${DOCKERFILE_HASH}" -f "${DOCKERFILE}" "${ROOT_DIR}"

echo "Built ${IMAGE_TAG} for linux/${TARGETARCH}"
