FROM node:22.14.0-bookworm-slim

ARG TOOLING_VERSION=1.0.0
ARG NPM_VERSION=10.9.2
ARG YO_VERSION=7.0.1
ARG YEOMAN_ENVIRONMENT_VERSION=6.2.0
ARG YEOMAN_GENERATOR_VERSION=7.5.1
ARG YEOMAN_TEST_VERSION=9.1.0
ARG MOCHA_VERSION=10.8.2
ARG CHAI_VERSION=5.1.2
ARG YAML_VERSION=2.7.0
ARG AJV_VERSION=8.20.0

ENV TOOLING_IMAGE=sbm-agent-tooling
ENV TOOLING_VERSION=${TOOLING_VERSION}
ENV NODE_ENV=development
ENV NPM_CONFIG_UPDATE_NOTIFIER=false
ENV NPM_CONFIG_FUND=false
ENV NPM_CONFIG_AUDIT=false

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      curl \
      unzip \
      coreutils \
      expect \
 && rm -rf /var/lib/apt/lists/*

RUN npm install --global \
      npm@${NPM_VERSION} \
      yo@${YO_VERSION} \
      yeoman-environment@${YEOMAN_ENVIRONMENT_VERSION} \
      yeoman-generator@${YEOMAN_GENERATOR_VERSION} \
      yeoman-test@${YEOMAN_TEST_VERSION} \
      mocha@${MOCHA_VERSION} \
      chai@${CHAI_VERSION} \
      yaml@${YAML_VERSION} \
      ajv@${AJV_VERSION} \
 && npm cache clean --force

RUN useradd \
      --create-home \
      --uid 10001 \
      --shell /bin/bash \
      sbm

RUN mkdir -p \
      /workspace \
      /tmp/sbm-agent-tooling \
 && chown -R sbm:sbm \
      /workspace \
      /tmp/sbm-agent-tooling

WORKDIR /workspace

USER sbm

CMD ["bash"]
