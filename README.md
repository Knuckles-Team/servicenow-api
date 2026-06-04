# Servicenow Api
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/servicenow-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
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

*Version: 1.31.0*

---

## Overview

**Servicenow Api** is a production-grade Agent and Model Context Protocol (MCP) server designed to interface directly with Python ServiceNow API Wrapper.

---

## Key Features

- **Consolidated Action-Routed MCP Tools:** Minimizes token overhead and eliminates tool bloat in LLM contexts by grouping methods into optimized, togglable tool modules.
- **Enterprise-Grade Security:** Comprehensive support for Eunomia policies, OIDC token delegation, and granular execution context tracking.
- **Integrated Graph Agent:** Built-in Pydantic AI agent supporting the Agent Control Protocol (ACP) and standard Web interfaces (AG-UI).
- **Native Telemetry & Tracing:** Out-of-the-box OpenTelemetry exports and native Langfuse tracing.

---

## CLI or API

This agent wraps the Python ServiceNow API Wrapper API. You can interact with it programmatically or via its integrated execution entrypoints.

Detailed instructions on how to use the underlying API wrappers, extended schema bindings, and developer SDK references are maintained in [docs/index.md](docs/index.md).

---

## MCP

This server utilizes dynamic Action-Routed tools to optimize token overhead and maximize IDE compatibility.

### Available MCP Tools
| Tool Module | Toggle Env Var | Enabled by Default | Description & Nested Methods |
|-------------|----------------|--------------------|------------------------------|
| **Misc** | `MISC_TOOL` | `True` | Manage ingest incidents to kg operations. |
| **Flows** | `FLOWS_TOOL` | `True` | Manage servicenow flows operations. Action-routed methods: `collect_graph_for_roots`, `get_flow_metadata`, `workflow_to_mermaid`. |
| **Application** | `APPLICATION_TOOL` | `True` | Manage servicenow application operations. Action-routed methods: `get_application`. |
| **Cmdb** | `CMDB_TOOL` | `True` | Manage servicenow cmdb operations. Action-routed methods: `create_cmdb_instance`, `create_cmdb_relation`, `delete_cmdb_relation`, `get_cmdb`, `get_cmdb_instance`, `get_cmdb_instances`, `ingest_cmdb_data`, `patch_cmdb_instance`, `update_cmdb_instance`. |
| **Cicd** | `CICD_TOOL` | `True` | Manage servicenow cicd operations. Action-routed methods: `app_repo_install`, `app_repo_publish`, `app_repo_rollback`, `batch_install`, `batch_install_result`, `batch_rollback`, `combo_suite_scan`, `full_scan`, `instance_scan_progress`, `point_scan`, `progress`, `suite_scan`. |
| **Plugins** | `PLUGINS_TOOL` | `True` | Manage servicenow plugins operations. Action-routed methods: `activate_plugin`, `rollback_plugin`. |
| **Source Control** | `SOURCE_CONTROL_TOOL` | `True` | Manage servicenow source control operations. Action-routed methods: `apply_remote_source_control_changes`, `import_repository`. |
| **Testing** | `TESTING_TOOL` | `True` | Manage servicenow testing operations. Action-routed methods: `run_test_suite`. |
| **Update Sets** | `UPDATE_SETS_TOOL` | `True` | Manage servicenow update sets operations. Action-routed methods: `update_set_back_out`, `update_set_commit`, `update_set_commit_multiple`, `update_set_create`, `update_set_preview`, `update_set_retrieve`. |
| **Batch** | `BATCH_TOOL` | `True` | Manage servicenow batch operations. Action-routed methods: `batch_request`. |
| **Change Management** | `CHANGE_MANAGEMENT_TOOL` | `True` | Manage servicenow change management operations. Action-routed methods: `approve_change_request`, `calculate_standard_change_request_risk`, `check_change_request_conflict`, `create_change_request`, `create_change_request_ci_association`, `create_change_request_task`, `delete_change_request`, `delete_change_request_conflict_scan`, `delete_change_request_task`, `get_change_request`, `get_change_request_ci`, `get_change_request_conflict`, `get_change_request_models`, `get_change_request_nextstate`, `get_change_request_schedule`, `get_change_request_tasks`, `get_change_request_worker`, `get_change_requests`, `get_standard_change_request_model`, `get_standard_change_request_template`, `get_standard_change_request_templates`, `refresh_change_request_impacted_services`, `update_change_request`, `update_change_request_first_available`, `update_change_request_task`. |
| **Cilifecycle** | `CILIFECYCLE_TOOL` | `True` | Manage servicenow cilifecycle operations. Action-routed methods: `add_ci_lifecycle_action`, `check_ci_lifecycle_compat_actions`, `check_ci_lifecycle_lease_expired`, `check_ci_lifecycle_not_allowed_action`, `check_ci_lifecycle_not_allowed_ops_transition`, `check_ci_lifecycle_requestor_valid`, `delete_ci_lifecycle_action`, `extend_ci_lifecycle_lease`, `get_ci_lifecycle_active_actions`, `get_ci_lifecycle_status`, `register_ci_lifecycle_operator`, `set_ci_lifecycle_status`, `unregister_ci_lifecycle_operator`. |
| **Devops** | `DEVOPS_TOOL` | `True` | Manage servicenow devops operations. Action-routed methods: `check_devops_change_control`, `check_devops_step_mapping`, `get_devops_change_info`, `get_devops_code_schema`, `get_devops_onboarding_status`, `get_devops_orchestration_schema`, `get_devops_plan_schema`, `register_devops_artifact`. |
| **Import Sets** | `IMPORT_SETS_TOOL` | `True` | Manage servicenow import sets operations. Action-routed methods: `get_import_set`, `insert_import_set`, `insert_multiple_import_sets`. |
| **Incidents** | `INCIDENTS_TOOL` | `True` | Manage servicenow incidents operations. Action-routed methods: `create_incident`, `get_incident`, `get_incidents`. |
| **Knowledge Management** | `KNOWLEDGE_MANAGEMENT_TOOL` | `True` | Manage servicenow knowledge management operations. Action-routed methods: `get_featured_knowledge_article`, `get_knowledge_article`, `get_knowledge_article_attachment`, `get_knowledge_articles`, `get_most_viewed_knowledge_articles`. |
| **Table Api** | `TABLE_API_TOOL` | `True` | Manage servicenow table api operations. Action-routed methods: `add_table_record`, `delete_table_record`, `get_table`, `get_table_record`, `patch_table_record`, `update_table_record`. |
| **Auth** | `AUTH_TOOL` | `True` | Manage servicenow auth operations. Action-routed methods: `refresh_auth_token`. |
| **Custom Api** | `CUSTOM_API_TOOL` | `True` | Manage servicenow custom api operations. Action-routed methods: `api_request`. |
| **Email** | `EMAIL_TOOL` | `True` | Manage servicenow email operations. Action-routed methods: `send_email`. |
| **Data Classification** | `DATA_CLASSIFICATION_TOOL` | `True` | Manage servicenow data classification operations. Action-routed methods: `get_data_classification`. |
| **Aggregate** | `AGGREGATE_TOOL` | `True` | Manage servicenow aggregate operations. Action-routed methods: `get_stats`. |
| **Activity Subscriptions** | `ACTIVITY_SUBSCRIPTIONS_TOOL` | `True` | Manage servicenow activity subscriptions operations. Action-routed methods: `get_activity_subscriptions`. |
| **Account** | `ACCOUNT_TOOL` | `True` | Manage servicenow account operations. Action-routed methods: `get_account`. |
| **Hr** | `HR_TOOL` | `True` | Manage servicenow hr operations. Action-routed methods: `get_hr_profile`. |
| **Metricbase** | `METRICBASE_TOOL` | `True` | Manage servicenow metricbase operations. Action-routed methods: `metricbase_insert`. |
| **Attachment** | `ATTACHMENT_TOOL` | `True` | Manage servicenow attachment operations. Action-routed methods: `delete_attachment`, `get_attachment`, `upload_attachment`. |
| **Service Qualification** | `SERVICE_QUALIFICATION_TOOL` | `True` | Manage servicenow service qualification operations. Action-routed methods: `check_service_qualification`, `get_service_qualification`, `process_service_qualification_result`. |
| **Ppm** | `PPM_TOOL` | `True` | Manage servicenow ppm operations. Action-routed methods: `insert_cost_plans`, `insert_project_tasks`. |
| **Product Inventory** | `PRODUCT_INVENTORY_TOOL` | `True` | Manage servicenow product inventory operations. Action-routed methods: `delete_product_inventory`, `get_product_inventory`. |

Detailed tool schemas, parameter shapes, and validation constraints are preserved in [docs/mcp.md](docs/mcp.md).

### Dynamic Tool Selection & Visibility

This MCP server supports dynamic toolset selection and visibility filtering at runtime. This allows you to restrict the set of exposed tools in order to prevent blowing up the LLM's context window.

You can configure tool filtering via multiple input channels:

- **CLI Arguments:** Pass `--tools` or `--toolsets` (or their disabled counterparts `--disabled-tools` and `--disabled-toolsets`) during startup.
- **Environment Variables:** Define standard environment variables:
  - `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS`
  - `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS`
- **HTTP SSE Request Headers:** Pass custom headers during transport initialization:
  - `x-mcp-enabled-tools` / `x-mcp-disabled-tools`
  - `x-mcp-enabled-tags` / `x-mcp-disabled-tags`
- **HTTP SSE Request Query Parameters:** Append query parameters directly to your transport connection URL:
  - `?tools=tool1,tool2`
  - `?tags=tag1`

When query strings or parameters are supplied, an LLM-free **Knowledge Graph resolution layer** (using `DynamicToolOrchestrator`) matches query intents against known tool tags, names, or descriptions, with safe fallback and automated 24-hour background cache refreshing.

---

### MCP Configuration Examples

#### stdio Transport (Recommended for local IDEs e.g., Cursor, Claude Desktop)
Configure your IDE's `mcp.json` to launch the MCP server via `uvx`:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "command": "uvx",
      "args": [
        "--from",
        "servicenow-api",
        "servicenow-mcp"
      ],
      "env": {
        "SERVICENOW_INSTANCE": "your_servicenow_instance_here",
        "SERVICENOW_USERNAME": "your_servicenow_username_here",
        "SERVICENOW_CLIENT_ID": "your_servicenow_client_id_here",
        "SERVICENOW_SSL_VERIFY": "your_servicenow_ssl_verify_here",
        "DEBUG": "your_debug_here",
        "PYTHONUNBUFFERED": "your_pythonunbuffered_here",
        "SERVICENOW_PASSWORD": "your_servicenow_password_here",
        "SERVICENOW_CLIENT_SECRET": "your_servicenow_client_secret_here"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (Recommended for production deployments)
Configure your client's `mcp.json` to launch the Streamable-HTTP server via `uvx` with explicit host and port definition:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "command": "uvx",
      "args": [
        "--from",
        "servicenow-api",
        "servicenow-mcp"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "SERVICENOW_INSTANCE": "your_servicenow_instance_here",
        "SERVICENOW_USERNAME": "your_servicenow_username_here",
        "SERVICENOW_CLIENT_ID": "your_servicenow_client_id_here",
        "SERVICENOW_SSL_VERIFY": "your_servicenow_ssl_verify_here",
        "DEBUG": "your_debug_here",
        "PYTHONUNBUFFERED": "your_pythonunbuffered_here",
        "SERVICENOW_PASSWORD": "your_servicenow_password_here",
        "SERVICENOW_CLIENT_SECRET": "your_servicenow_client_secret_here"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed remote or local Streamable-HTTP instance:

```json
{
  "mcpServers": {
    "servicenow-api": {
      "url": "http://localhost:8000/servicenow-api/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name servicenow-api-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e SERVICENOW_INSTANCE="your_value" \
  -e SERVICENOW_USERNAME="your_value" \
  -e SERVICENOW_CLIENT_ID="your_value" \
  -e SERVICENOW_SSL_VERIFY="your_value" \
  -e DEBUG="your_value" \
  -e PYTHONUNBUFFERED="your_value" \
  -e SERVICENOW_PASSWORD="your_value" \
  -e SERVICENOW_CLIENT_SECRET="your_value" \
  knucklessg1/servicenow-api:latest
```

---

## Agent

This repository features a fully integrated Pydantic AI Graph Agent. It communicates over the **Agent Control Protocol (ACP)** and interacts seamlessly with the **Agent Web UI (AG-UI)** and Terminal interface.

### Running the Agent CLI
To start the interactive command-line agent:

```bash
# Set credentials
export SERVICENOW_INSTANCE="your_value"
export SERVICENOW_USERNAME="your_value"
export SERVICENOW_CLIENT_ID="your_value"
export SERVICENOW_SSL_VERIFY="your_value"
export DEBUG="your_value"
export PYTHONUNBUFFERED="your_value"
export SERVICENOW_PASSWORD="your_value"
export SERVICENOW_CLIENT_SECRET="your_value"

# Run the agent server
servicenow-agent --provider openai --model-id gpt-4o
```

### Docker Compose Orchestration
The following `docker/agent.compose.yml` configures the Agent, Web UI, and Terminal Interface together:

```yaml
version: '3.8'

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
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

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
      - ENABLE_OTEL=True
    ports:
      - "9004:9004"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:9004/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

```

Detailed graph node architecture explanations, custom skill configurations, and agentic trace guides are available in [docs/agent.md](docs/agent.md).

---

## Security & Governance

Built directly upon the enterprise-ready [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) core, standard security parameters are fully supported:

### Access Control & Policy Enforcement
- **Eunomia Policies:** Fine-grained, policy-driven tool authorization. Supports `none`, local `embedded` (`mcp_policies.json`), or centralized `remote` modes.
- **OIDC Token Delegation:** Compliant with RFC 8693 token exchange for flowing authenticating user credentials from Web UI / ACP → Agent → MCP.
- **Scoped Credentials:** Execution context runs restricted to the specific caller identity.

### Runtime Security Grid
| Feature | Functionality | Enablement |
|---------|---------------|------------|
| **Tool Guard** | Sensitivity inspection with human-in-the-loop validation | Enabled by default |
| **Prompt Injection Defense** | Input scanning, repetition monitoring, and recursive loop blocks | Enabled by default |
| **Context Safety Guard** | Stuck-loop detectors and contextual overflow preemptive alerts | Enabled by default |

---

## Installation

Install the Python package locally:

```bash
# Using uv (highly recommended)
uv pip install servicenow-api[all]

# Using standard pip
python -m pip install servicenow-api[all]
```

---

## Repository Owners

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)

---

## Contribute

Contributions are welcome! Please ensure code quality by executing local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Execute test suites using `pytest`
