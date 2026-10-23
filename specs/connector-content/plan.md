# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `servicenow-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `servicenow_api` from it.
