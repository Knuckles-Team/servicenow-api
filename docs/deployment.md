# Deployment

This page covers running `servicenow-api` as a long-lived server: the transports, a
Docker Compose stack, the companion A2A agent server, putting it behind a Caddy
reverse proxy, and giving it a DNS name with Technitium.

> `servicenow-api` ships an **MCP server** (console script `servicenow-mcp`) and a
> companion **A2A agent server** (console script `servicenow-agent`). The MCP server
> is a typed, deterministic tool surface a policy router / agent calls; the agent
> server is a Pydantic-AI graph agent that consumes those tools.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    servicenow-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    servicenow-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    servicenow-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`servicenow-api` is configured entirely from the environment. The **required** set to
connect to ServiceNow:

| Var | Default | Meaning |
|---|---|---|
| `SERVICENOW_INSTANCE` | `https://dev350360.service-now.com` | ServiceNow instance URL |
| `SERVICENOW_USERNAME` | `admin` | User id (basic auth) |
| `SERVICENOW_PASSWORD` | _(unset)_ | Password (basic auth) |
| `SERVICENOW_CLIENT_ID` | _(unset)_ | OAuth client id (optional) |
| `SERVICENOW_CLIENT_SECRET` | _(unset)_ | OAuth client secret (optional) |
| `SERVICENOW_SSL_VERIFY` | `True` | Verify TLS |
| `HOST` / `PORT` / `TRANSPORT` | `0.0.0.0` / `8000` / `stdio` | HTTP transport binding |

Each ServiceNow tool domain (incidents, change management, CMDB, DevOps, …) is gated
by its own `*TOOL` toggle (for example `INCIDENTSTOOL`, `CMDBTOOL`,
`CHANGE_MANAGEMENTTOOL`), all defaulting to `True`. The full set, including telemetry
(`ENABLE_OTEL`) and access-governance (`EUNOMIA_*`) variables, is documented in
[`.env.example`](https://github.com/Knuckles-Team/servicenow-api/blob/main/.env.example).
Copy it to `.env` and populate only what you use.

## Backing Service (ServiceNow)

ServiceNow is a **managed SaaS platform** — there is no local backing system to
provision. Point `SERVICENOW_INSTANCE` at your tenant (for example a personal
developer instance from the ServiceNow Developer Program) and supply credentials via
the variables above. Because the backing system is hosted, only connection
configuration is required; no `platform.md` recipe applies.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/servicenow-api/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
services:
  servicenow-api-mcp:
    image: knucklessg1/servicenow-api:latest
    container_name: servicenow-api-mcp
    hostname: servicenow-api-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit SERVICENOW_* values
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## A2A agent server

`servicenow-api` also ships a Pydantic-AI **agent server** (console script
`servicenow-agent`). It consumes the MCP tool surface over `MCP_URL`, exposes an
A2A / web interface on port `9004`, and is published in the same image.
[`docker/agent.compose.yml`](https://github.com/Knuckles-Team/servicenow-api/blob/main/docker/agent.compose.yml)
runs the MCP server and the agent together:

```yaml
services:
  servicenow-api-mcp:
    image: knucklessg1/servicenow-api:latest
    container_name: servicenow-api-mcp
    hostname: servicenow-api-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"

  servicenow-api-agent:
    image: knucklessg1/servicenow-api:latest
    container_name: servicenow-api-agent
    hostname: servicenow-api-agent
    restart: always
    depends_on:
      - servicenow-api-mcp
    env_file:
      - ../.env
    command: [ "servicenow-agent" ]
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=9004
      - MCP_URL=http://servicenow-api-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
    ports:
      - "9004:9004"
```

```bash
docker compose -f docker/agent.compose.yml up -d
curl -s http://localhost:9004/health        # {"status":"OK"}
```

The agent reaches the MCP server by container name through `MCP_URL`; set `PROVIDER`
and `MODEL_ID` to select the backing LLM.

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
servicenow-api.arpa {
    tls internal
    reverse_proxy servicenow-api-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
servicenow-api.example.com {
    reverse_proxy servicenow-api-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=servicenow-api.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `servicenow-api.arpa → <caddy-host-ip>` in the Technitium web
console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "command": "uv",
      "args": ["run", "--with", "servicenow-api", "servicenow-mcp"],
      "env": {
        "SERVICENOW_INSTANCE": "https://your-instance.service-now.com",
        "SERVICENOW_USERNAME": "admin",
        "SERVICENOW_PASSWORD": "your_password"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://servicenow-api.arpa/mcp` instead.
