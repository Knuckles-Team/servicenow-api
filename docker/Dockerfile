# syntax=docker/dockerfile:1
# Slim multi-stage build: install in a builder, ship only /usr/local. Cuts the
# pushed image ~43% (no default-jre/dev-tools/source) so layer pushes finish well
# inside the registry's blob-upload window even under concurrency.
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=3600
# Some [all] deps (e.g. hnswlib, an agent-utilities transitive) ship no manylinux
# wheel and build from sdist, needing a C++ toolchain. Install it in the builder
# only — the final stage copies just /usr/local, so no compiler ships.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --upgrade --break-system-packages --prerelease=allow servicenow-api[all]>=1.37.0

FROM python:3.11-slim

ARG HOST=0.0.0.0
ARG PORT=8000
ARG TRANSPORT="stdio"
ARG AUTH_TYPE="none"

ENV HOST=${HOST} \
    PORT=${PORT} \
    TRANSPORT=${TRANSPORT} \
    AUTH_TYPE=${AUTH_TYPE} \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:/usr/local/bin:${PATH}" \
    UV_HTTP_TIMEOUT=3600 \
    UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install base dependencies, uv, and starship shell prompt
COPY --from=builder /usr/local /usr/local

CMD ["servicenow-mcp"]
