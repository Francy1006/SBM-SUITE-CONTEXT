FROM debian:12-slim

ARG SONAR_SCANNER_VERSION=8.1.0.6389
ARG NODE_VERSION=22.14.0
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl unzip xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
      amd64) NODE_ARCH="linux-x64" ;; \
      arm64) NODE_ARCH="linux-arm64" ;; \
      *) echo "Unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL -o /tmp/node.tar.xz \
      "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-${NODE_ARCH}.tar.xz" \
    && tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 \
    && rm -f /tmp/node.tar.xz \
    && node --version \
    && npm --version

RUN case "${TARGETARCH}" in \
      amd64) SCANNER_ARCH="linux-x64" ;; \
      arm64) SCANNER_ARCH="linux-aarch64" ;; \
      *) echo "Unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac \
    && curl -fsSL -A 'Mozilla/5.0' -o /tmp/sonar-scanner.zip \
      "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-${SCANNER_ARCH}.zip" \
    && unzip -q /tmp/sonar-scanner.zip -d /opt \
    && rm -f /tmp/sonar-scanner.zip \
    && mv "/opt/sonar-scanner-${SONAR_SCANNER_VERSION}-${SCANNER_ARCH}" /opt/sonar-scanner \
    && ln -sf /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

ENV SONAR_USER_HOME=/opt/sonar-scanner/.sonar
ENV PATH="/opt/sonar-scanner/bin:/usr/local/bin:${PATH}"

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/sonar-scanner"]
