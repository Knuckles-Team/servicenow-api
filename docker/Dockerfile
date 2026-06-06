# syntax=docker/dockerfile:1
# Slim multi-stage build: install in a builder, ship only /usr/local. Cuts the
# pushed image ~43% (no default-jre/dev-tools/source) so layer pushes finish well
# inside the registry's blob-upload window even under concurrency.
FROM python:3.11-slim AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_HTTP_TIMEOUT=3600
RUN --mount=type=cache,target=/root/.cache/uv \
    pip install --no-cache-dir uv \
    && uv pip install --system --upgrade --break-system-packages --prerelease=allow servicenow-api[all]>=1.33.0

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
