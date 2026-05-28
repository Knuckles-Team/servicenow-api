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
    UV_COMPILE_BYTECODE=1

# Install base dependencies, uv, and starship shell prompt
RUN apt-get update \
    && apt-get install -y default-jre ripgrep tree fd-find curl nano \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && curl -sS https://starship.rs/install.sh | sh -s -- --yes \
    && mkdir -p /root/.config \
    && echo "eval \"\$(starship init bash)\"" >> /root/.bashrc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Compile and install package in-place
RUN uv pip install --system --upgrade --verbose --no-cache --break-system-packages --prerelease=allow servicenow-api[all]>=1.22.1

COPY docker/starship.toml /root/.config/starship.toml

CMD ["servicenow-mcp"]
