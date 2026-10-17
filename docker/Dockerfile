# MCP-server image: installs servicenow-api[mcp] (agent-connector-sdk runtime) and runs the MCP server.
#
#   docker build -t servicenow-api:local .
FROM python:3.11-slim@sha256:e031123e3d85762b141ad1cbc56452ba69c6e722ebf2f042cc0dc86c47c0d8b3 AS builder-base
COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=3600
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Slim MCP-only dependency closure.
FROM builder-base AS builder-mcp
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --break-system-packages servicenow-api[mcp]==2.2.0

# ServiceNow SDK CLI (now-sdk) — a minimal, self-contained Node.js LTS layer holding
# only the global @servicenow/sdk install. Copied whole (COPY --from below) into both
# runtime images so `now-sdk` is on PATH next to the Python console scripts.
FROM node:22-slim@sha256:6c74791e557ce11fc957704f6d4fe134a7bc8d6f5ca4403205b2966bd488f6b3 AS builder-node
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3 \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @servicenow/sdk@4.9.0 \
    && npm cache clean --force \
    && rm -rf /usr/local/lib/node_modules/npm/docs /usr/local/lib/node_modules/npm/man

FROM python:3.11-slim@sha256:e031123e3d85762b141ad1cbc56452ba69c6e722ebf2f042cc0dc86c47c0d8b3 AS runtime-base
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
    UV_HTTP_TIMEOUT=3600 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Slim image: MCP server only.
# Fixed identity for least-privilege runtime and stable volume ownership.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --no-create-home \
        --home-dir /tmp --shell /usr/sbin/nologin app
ENV HOME=/tmp \
    XDG_CONFIG_HOME=/tmp/.config \
    XDG_CACHE_HOME=/tmp/.cache

FROM runtime-base AS mcp
USER 10001:10001
COPY --from=builder-mcp /usr/local /usr/local
COPY --from=builder-node /usr/local /usr/local
CMD ["servicenow-mcp"]
