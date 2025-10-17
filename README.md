# ServiceNow API

![PyPI - Version](https://img.shields.io/pypi/v/servicenow-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/servicenow-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/servicenow-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/servicenow-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/servicenow-api)
![PyPI - License](https://img.shields.io/pypi/l/servicenow-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/servicenow-api)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/servicenow-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/servicenow-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/servicenow-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/servicenow-api)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/servicenow-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/servicenow-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/servicenow-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/servicenow-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/servicenow-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/servicenow-api)

*Version: 1.2.0*

ServiceNow API Python Wrapper

This repository is actively maintained and will continue adding more API calls. It includes a Model Context Protocol (MCP) server for Agentic AI, enhanced with various authentication mechanisms, middleware for observability and control, and optional Eunomia authorization for policy-based access control.

Contributions are welcome!

All API Response objects are customized for the response call. You can access return values in a `parent.value.nested_value` format, or use `parent.model_dump()` to get the response as a dictionary.

#### API Calls:
- Application Service
- Change Management
- CI/CD
- CMDB
- Import Sets
- Incident
- Knowledge Base
- Table
- Custom Endpoint

If your API call isn't supported, you can use the `api_request` tool to perform GET/POST/PUT/DELETE requests to any ServiceNow endpoint.

#### Features:
- **Authentication**: Supports multiple authentication types including none (disabled), static (internal tokens), JWT, OAuth Proxy, OIDC Proxy, and Remote OAuth for external identity providers.
- **Middleware**: Includes logging, timing, rate limiting, and error handling for robust server operation.
- **Eunomia Authorization**: Optional policy-based authorization with embedded or remote Eunomia server integration.
- **Resources**: Provides `instance_config` and `incident_categories` for ServiceNow configuration and data.
- **Prompts**: Includes `create_incident_prompt` and `query_table_prompt` for AI-driven interactions.

<details>
  <summary><b>Usage:</b></summary>

### Basic API Usage

**OAuth Authentication**

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
client_id = "<SERVICENOW CLIENT_ID>"
client_secret = "<SERVICENOW_CLIENT_SECRET>"
servicenow_url = "<SERVICENOW_URL>"

client = servicenow_api.Api(
    url=servicenow_url,
    username=username,
    password=password,
    client_id=client_id,
    client_secret=client_secret
)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```

**Basic Authentication**

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
servicenow_url = "<SERVICENOW_URL>"

client = servicenow_api.Api(
    url=servicenow_url,
    username=username,
    password=password
)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```

**Proxy and SSL Verify**

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
servicenow_url = "<SERVICENOW_URL>"

proxy = "https://proxy.net"

client = servicenow_api.Api(
    url=servicenow_url,
    username=username,
    password=password,
    proxy=proxy,
    verify=False
)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```

### Deploy MCP Server as a Service

The ServiceNow MCP server can be deployed using Docker, with configurable authentication, middleware, and Eunomia authorization.

#### Using Docker Run

```bash
docker pull knucklessg1/servicenow:latest

docker run -d \
  --name servicenow-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=none \
  -e EUNOMIA_TYPE=none \
  -e SERVICENOW_INSTANCE=https://yourinstance.servicenow.com \
  -e SERVICENOW_USERNAME=user \
  -e SERVICENOW_PASSWORD=pass \
  -e SERVICENOW_CLIENT_ID=client_id \
  -e SERVICENOW_CLIENT_SECRET=client_secret \
  -e SERVICENOW_VERIFY=False \
  knucklessg1/servicenow:latest
```

For advanced authentication (e.g., JWT, OAuth Proxy, OIDC Proxy, Remote OAuth) or Eunomia, add the relevant environment variables:

```bash
docker run -d \
  --name servicenow-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=oidc-proxy \
  -e OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration \
  -e OIDC_CLIENT_ID=your-client-id \
  -e OIDC_CLIENT_SECRET=your-client-secret \
  -e OIDC_BASE_URL=https://your-server.com \
  -e ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/* \
  -e EUNOMIA_TYPE=embedded \
  -e EUNOMIA_POLICY_FILE=/app/mcp_policies.json \
  -e SERVICENOW_INSTANCE=https://yourinstance.servicenow.com \
  -e SERVICENOW_USERNAME=user \
  -e SERVICENOW_PASSWORD=pass \
  -e SERVICENOW_CLIENT_ID=client_id \
  -e SERVICENOW_CLIENT_SECRET=client_secret \
  -e SERVICENOW_VERIFY=False \
  knucklessg1/servicenow:latest
```

#### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
services:
  servicenow-mcp:
    image: knucklessg1/servicenow:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=none
      - EUNOMIA_TYPE=none
      - SERVICENOW_INSTANCE=https://yourinstance.servicenow.com
      - SERVICENOW_USERNAME=user
      - SERVICENOW_PASSWORD=pass
      - SERVICENOW_CLIENT_ID=client_id
      - SERVICENOW_CLIENT_SECRET=client_secret
      - SERVICENOW_VERIFY=False
    ports:
      - 8004:8004
```

For advanced setups with authentication and Eunomia:

```yaml
services:
  servicenow-mcp:
    image: knucklessg1/servicenow:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=oidc-proxy
      - OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration
      - OIDC_CLIENT_ID=your-client-id
      - OIDC_CLIENT_SECRET=your-client-secret
      - OIDC_BASE_URL=https://your-server.com
      - ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/*
      - EUNOMIA_TYPE=embedded
      - EUNOMIA_POLICY_FILE=/app/mcp_policies.json
      - SERVICENOW_INSTANCE=https://yourinstance.servicenow.com
      - SERVICENOW_USERNAME=user
      - SERVICENOW_PASSWORD=pass
      - SERVICENOW_CLIENT_ID=client_id
      - SERVICENOW_CLIENT_SECRET=client_secret
      - SERVICENOW_VERIFY=False
    ports:
      - 8004:8004
    volumes:
      - ./mcp_policies.json:/app/mcp_policies.json
```

Run the service:

```bash
docker-compose up -d
```

#### Configure `mcp.json` for AI Integration

Recommended: Store secrets in environment variables with lookup in the JSON file.

For Testing Only: Plain text storage will also work, although **not** recommended.

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "servicenow-api",
        "servicenow-mcp",
        "--transport",
        "${TRANSPORT}",
        "--host",
        "${HOST}",
        "--port",
        "${PORT}",
        "--auth-type",
        "${AUTH_TYPE}",
        "--eunomia-type",
        "${EUNOMIA_TYPE}"
      ],
      "env": {
        "SERVICENOW_INSTANCE": "https://yourinstance.servicenow.com",
        "SERVICENOW_USERNAME": "user",
        "SERVICENOW_PASSWORD": "pass",
        "SERVICENOW_CLIENT_ID": "client_id",
        "SERVICENOW_CLIENT_SECRET": "client_secret",
        "SERVICENOW_VERIFY": "False",
        "TOKEN_JWKS_URI": "${TOKEN_JWKS_URI}",
        "TOKEN_ISSUER": "${TOKEN_ISSUER}",
        "TOKEN_AUDIENCE": "${TOKEN_AUDIENCE}",
        "OAUTH_UPSTREAM_AUTH_ENDPOINT": "${OAUTH_UPSTREAM_AUTH_ENDPOINT}",
        "OAUTH_UPSTREAM_TOKEN_ENDPOINT": "${OAUTH_UPSTREAM_TOKEN_ENDPOINT}",
        "OAUTH_UPSTREAM_CLIENT_ID": "${OAUTH_UPSTREAM_CLIENT_ID}",
        "OAUTH_UPSTREAM_CLIENT_SECRET": "${OAUTH_UPSTREAM_CLIENT_SECRET}",
        "OAUTH_BASE_URL": "${OAUTH_BASE_URL}",
        "OIDC_CONFIG_URL": "${OIDC_CONFIG_URL}",
        "OIDC_CLIENT_ID": "${OIDC_CLIENT_ID}",
        "OIDC_CLIENT_SECRET": "${OIDC_CLIENT_SECRET}",
        "OIDC_BASE_URL": "${OIDC_BASE_URL}",
        "REMOTE_AUTH_SERVERS": "${REMOTE_AUTH_SERVERS}",
        "REMOTE_BASE_URL": "${REMOTE_BASE_URL}",
        "ALLOWED_CLIENT_REDIRECT_URIS": "${ALLOWED_CLIENT_REDIRECT_URIS}",
        "EUNOMIA_TYPE": "${EUNOMIA_TYPE}",
        "EUNOMIA_POLICY_FILE": "${EUNOMIA_POLICY_FILE}",
        "EUNOMIA_REMOTE_URL": "${EUNOMIA_REMOTE_URL}"
      },
      "timeout": 200000
    }
  }
}
```

#### CLI Parameters

The `servicenow-mcp` command supports the following CLI options for configuration:

- `--transport`: Transport method (`stdio`, `http`, `sse`) [default: `http`]
- `--host`: Host address for HTTP transport [default: `0.0.0.0`]
- `--port`: Port number for HTTP transport [default: `8000`]
- `--auth-type`: Authentication type (`none`, `static`, `jwt`, `oauth-proxy`, `oidc-proxy`, `remote-oauth`) [default: `none`]
- `--token-jwks-uri`: JWKS URI for JWT verification
- `--token-issuer`: Issuer for JWT verification
- `--token-audience`: Audience for JWT verification
- `--oauth-upstream-auth-endpoint`: Upstream authorization endpoint for OAuth Proxy
- `--oauth-upstream-token-endpoint`: Upstream token endpoint for OAuth Proxy
- `--oauth-upstream-client-id`: Upstream client ID for OAuth Proxy
- `--oauth-upstream-client-secret`: Upstream client secret for OAuth Proxy
- `--oauth-base-url`: Base URL for OAuth Proxy
- `--oidc-config-url`: OIDC configuration URL
- `--oidc-client-id`: OIDC client ID
- `--oidc-client-secret`: OIDC client secret
- `--oidc-base-url`: Base URL for OIDC Proxy
- `--remote-auth-servers`: Comma-separated list of authorization servers for Remote OAuth
- `--remote-base-url`: Base URL for Remote OAuth
- `--allowed-client-redirect-uris`: Comma-separated list of allowed client redirect URIs
- `--eunomia-type`: Eunomia authorization type (`none`, `embedded`, `remote`) [default: `none`]
- `--eunomia-policy-file`: Policy file for embedded Eunomia [default: `mcp_policies.json`]
- `--eunomia-remote-url`: URL for remote Eunomia server

#### Middleware

The MCP server includes the following built-in middleware for enhanced functionality:

- **ErrorHandlingMiddleware**: Provides comprehensive error logging and transformation.
- **RateLimitingMiddleware**: Limits request frequency with a token bucket algorithm (10 requests/second, burst capacity of 20).
- **TimingMiddleware**: Tracks execution time of requests.
- **LoggingMiddleware**: Logs all requests and responses for observability.

#### Eunomia Authorization

The server supports optional Eunomia authorization for policy-based access control:

- **Disabled (`none`)**: No authorization checks.
- **Embedded (`embedded`)**: Runs an embedded Eunomia server with a local policy file (`mcp_policies.json` by default).
- **Remote (`remote`)**: Connects to an external Eunomia server for centralized policy decisions.

To configure Eunomia policies:

```bash
# Initialize a default policy file
eunomia-mcp init

# Validate the policy file
eunomia-mcp validate mcp_policies.json
```

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install servicenow-api eunomia-mcp
```

</details>

<details>
  <summary><b>Tests:</b></summary>

```bash
python ./test/test_servicenow_models.py
```
</details>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)

![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/knuckles-team-servicenow-api-badge.png)](https://mseep.ai/app/knuckles-team-servicenow-api)
