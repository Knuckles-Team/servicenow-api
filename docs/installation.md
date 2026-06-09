# Installation

`servicenow-api` is a standard Python package and a prebuilt container image. Pick the
path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **ServiceNow instance** and credentials — ServiceNow is a managed SaaS
  platform, so only connection configuration is required (see
  [Deployment](deployment.md#backing-service-servicenow)).

## From PyPI (recommended)

```bash
pip install servicenow-api
```

### Optional extras

The base install ships the typed REST client. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "servicenow-api[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "servicenow-api[agent]"` | Pydantic-AI agent server + Logfire tracing |
| `all` | `pip install "servicenow-api[all]"` | Everything above (MCP + agent + Logfire) |
| `test` | `pip install "servicenow-api[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run the MCP server and the A2A agent
pip install "servicenow-api[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/servicenow-api.git
cd servicenow-api
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run servicenow-mcp
```

## Prebuilt Docker image

A multi-stage, slim image is published on every release (entrypoint `servicenow-mcp`):

```bash
docker pull knucklessg1/servicenow-api:latest

docker run --rm -i \
  -e SERVICENOW_INSTANCE=https://your-instance.service-now.com \
  -e SERVICENOW_USERNAME=admin \
  -e SERVICENOW_PASSWORD=your_password \
  knucklessg1/servicenow-api:latest        # stdio transport (default)
```

For an HTTP server with a published port and the agent server, see
[Deployment](deployment.md).

## Verify the install

```bash
servicenow-mcp --help
python -c "import servicenow_api; print(servicenow_api.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP / agent server behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the API, and the command line.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
