# servicenow-api

A Python **API + MCP Server + A2A Agent** for ServiceNow — a typed, deterministic
tool surface over the ServiceNow REST API for the agent-utilities ecosystem.

!!! info "Official documentation"
    This site is the canonical reference for `servicenow-api`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/servicenow-api)](https://pypi.org/project/servicenow-api/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/servicenow-api)](https://github.com/Knuckles-Team/servicenow-api/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/servicenow-api)

## Overview

`servicenow-api` wraps the ServiceNow REST surface — Table API, Incident, Change
Management, CMDB, DevOps, Knowledge, CI/CD, and more — with a typed Python client and
exposes it three ways: as a Python API you import, as consolidated MCP tools an agent
calls, and as a Pydantic-AI A2A agent server. It provides:

- **`Api`** — a session-based ServiceNow REST client validated by Pydantic models,
  organized by ServiceNow domain (incident, change, CMDB, DevOps, knowledge, system).
- **Consolidated, action-routed MCP tools** — each ServiceNow domain is a single
  togglable tool module, minimizing token overhead and tool bloat in LLM contexts.
- **A graph-orchestrated A2A agent** — a Pydantic-AI agent server (console script
  `servicenow-agent`) with confidence-gated routing and an optional web interface.

Authentication supports both basic credentials (username / password with optional
OAuth client) and OIDC token delegation; the client remains inactive when credentials
are absent.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and the command line.
- :material-sitemap: **[Architecture](overview.md)** — the standardized agent-package pattern and MCP configuration.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:SNOW-*` registry.

</div>

## Quick start

```bash
pip install "servicenow-api[mcp]"
servicenow-mcp                   # stdio MCP server (default transport)
```

Connect it to a ServiceNow instance:

```bash
export SERVICENOW_INSTANCE=https://your-instance.service-now.com
export SERVICENOW_USERNAME=admin
export SERVICENOW_PASSWORD=your_password
servicenow-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, agent server, reverse proxy,
DNS).
