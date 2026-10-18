# syntax=docker/dockerfile:1
# GENERATED from pipelines/templates/connector/Dockerfile.tmpl by
# pipelines/scripts/connector_dockerfile.py. Do not hand-edit: change the template or
# the connector's entry in the script's EXCEPTIONS table, then regenerate.
#
# Wheel-only connector image. The published servicenow-api wheel is installed from PyPI at
# the exact version in pyproject.toml (kept in sync by .bumpversion.cfg); no source is
# copied into any stage, and every distribution in the closure must be a wheel
# (--only-binary :all:). The release pipeline publishes the wheel before this build,
# so the install retries while the new version propagates through the index.
#
#   docker build --target <stage> -t servicenow-api:local -f docker/Dockerfile .
#   stages: mcp
FROM python:3.14-slim@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6 AS builder-base
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=3600

FROM builder-base AS builder-mcp
RUN --mount=type=cache,target=/root/.cache/uv \
    for attempt in 1 2 3 4 5 6 7 8 9 10; do \
        uv pip install --system --break-system-packages --only-binary :all: \
            --refresh-package servicenow-api "servicenow-api[mcp]==2.3.1" && exit 0; \
        echo "wheel not installable yet (attempt ${attempt}); retrying in 30s"; \
        sleep 30; \
    done; \
    exit 1

FROM python:3.14-slim@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6 AS runtime-base
ARG HOST=127.0.0.1
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"
ENV HOST=${HOST} \
    PORT=${PORT} \
    TRANSPORT=${TRANSPORT} \
    AUTH_TYPE=${AUTH_TYPE} \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:${PATH}" \
    HOME=/tmp \
    XDG_CONFIG_HOME=/tmp/.config \
    XDG_CACHE_HOME=/tmp/.cache \
    XDG_STATE_HOME=/tmp/.local/state
# Fixed non-root identity for least-privilege runtime and stable volume ownership.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --no-create-home \
        --home-dir /tmp --shell /usr/sbin/nologin app \
    && install -d -o 10001 -g 10001 -m 0700 \
        /tmp/.config /tmp/.cache /tmp/.local/state

# mcp: MCP server only.
FROM runtime-base AS mcp
COPY --from=builder-mcp /usr/local /usr/local
USER 10001:10001
CMD ["servicenow-mcp"]
