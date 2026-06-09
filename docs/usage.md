# Usage — API / CLI / MCP

`servicenow-api` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** (`Api`) you import, and as a **command-line** server. The
full ServiceNow domain coverage and concept registry are in [Overview](overview.md)
and [Concepts](concepts.md).

## As an MCP server

Once [deployed](deployment.md), the server registers consolidated, action-routed
tools — one per ServiceNow domain. Each domain is toggled by its own `*TOOL`
environment variable (all default to enabled).

| Group | Domains |
|---|---|
| Service Management | `incidents`, `change_management`, `cmdb`, `cilifecycle` |
| Knowledge & HR | `knowledge_management`, `hr` |
| Platform & Data | `table_api`, `import_sets`, `data_classification`, `attachment`, `aggregate` |
| DevOps & Delivery | `devops`, `cicd`, `source_control`, `update_sets`, `testing`, `flows` |
| Operations | `account`, `auth`, `batch`, `email`, `plugins`, `custom_api`, `misc` |

Example agent prompts that map onto these tools:

- *"Open incident INC0010001 and show its current state"* → the `incidents` tool
- *"List change requests scheduled for this week"* → the `change_management` tool
- *"Look up the CMDB CI for host `app-01`"* → the `cmdb` tool

## As a Python API

`Api` is a session-based ServiceNow REST client; every domain method validates its
inputs with Pydantic models and returns a structured `Response`.

```python
from servicenow_api import Api

api = Api(
    url="https://your-instance.service-now.com",
    username="admin",
    password="your_password",
    verify=True,
)

# Reads
incidents = api.get_incidents()                          # list of incident records
incident = api.get_incident(incident_id="<sys_id>")      # a single incident
changes = api.get_change_requests()                      # change requests
ci = api.get_cmdb(cmdb_id="<sys_id>")                    # CMDB configuration item
records = api.get_table(table="incident")                # raw Table API read
```

Build a client straight from the environment:

```python
from servicenow_api.auth import get_client

api = get_client()        # reads SERVICENOW_* from the environment / .env,
                          # auto-detecting OIDC delegation or basic auth
```

## As a CLI

Both servers are installed as console scripts and accept transport and binding flags.

```bash
# MCP server (stdio by default)
servicenow-mcp
servicenow-mcp --transport streamable-http --host 0.0.0.0 --port 8000

# A2A agent server (consumes the MCP tools over MCP_URL)
MCP_URL=http://localhost:8000/mcp PROVIDER=openai MODEL_ID=gpt-4o \
  servicenow-agent
```

Each domain tool reads only the configuration it needs and remains inactive when the
corresponding credentials or `*TOOL` toggle are absent. See [Deployment](deployment.md)
for the full environment table and the long-lived server topology.
