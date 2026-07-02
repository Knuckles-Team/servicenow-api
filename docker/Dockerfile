# syntax=docker/dockerfile:1
# Two right-sized images from ONE Dockerfile, selected by build --target. Both are
# slim multi-stage (build in a builder, ship only /usr/local — no dev-tools/source):
#
#   --target agent  (DEFAULT)  installs servicenow-api[agent] = the FULL runtime
#                              (agent-utilities[agent]: engine + pydantic-ai + dspy +
#                              skills). Because [agent] also includes [mcp], this image
#                              can run EITHER the agent OR the mcp server. Push as the
#                              default tags: latest / main / <version>.
#
#   --target mcp               installs servicenow-api[mcp]   = MCP-server tooling ONLY
#                              (agent-utilities[mcp]: fastmcp/fastapi — NO engine,
#                              pydantic-ai, dspy, llama-index, tree-sitter). The slim
#                              variant. Push as the :mcp / :mcp-<version> tag.
#
#   docker build --target agent -t servicenow-api:latest .
#   docker build --target mcp   -t servicenow-api:mcp    .
FROM python:3.11-slim AS builder-base
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/
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
    uv pip install --system --upgrade --break-system-packages --prerelease=allow servicenow-api[mcp]>=2.0.1

# Full agent runtime dependency closure.
FROM builder-base AS builder-agent
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --upgrade --break-system-packages --prerelease=allow servicenow-api[agent]>=2.0.1

FROM python:3.11-slim AS runtime-base
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

# Slim image: MCP server only.
FROM runtime-base AS mcp
COPY --from=builder-mcp /usr/local /usr/local
CMD ["servicenow-mcp"]

# Full image (DEFAULT target): agent runtime; can also run the mcp server.
FROM runtime-base AS agent
COPY --from=builder-agent /usr/local /usr/local
CMD ["servicenow-agent"]
