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

*Version: 2.0.1*

> **Documentation** — Installation, deployment, and usage across the API, CLI, MCP,
> and A2A agent interfaces are maintained in the
> [official documentation](https://knuckles-team.github.io/servicenow-api/).

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

### Tool surface — `MCP_TOOL_MODE`

Set `MCP_TOOL_MODE` (in the shared `~/.config/agent-utilities/config.json` or env) to choose the surface:

- `condensed` (default) — the action-routed tools below (`servicenow_<domain>(action, params_json)`).
- `verbose` — one named, documented 1:1 tool per API method (`servicenow_get_cmdb_instance(...)`), tagged `verbose`.
- `both` — register both sets.

Filter the verbose set with `--tools tag:verbose` / `MCP_ENABLED_TAGS=verbose`. See the
agent-utilities guide *MCP Tool Modes* for details.

### Available MCP Tools

The table below is auto-generated from the MCP server — do not edit by hand.

<!-- MCP-TOOLS-TABLE:START -->

#### Condensed action-routed tools (default — `MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `ingest_incidents_to_kg` | `MISCTOOL` | Manage ingest incidents to kg operations. |
| `servicenow_account` | `ACCOUNTTOOL` | Manage servicenow account operations. |
| `servicenow_activity_subscriptions` | `ACTIVITY_SUBSCRIPTIONSTOOL` | Manage servicenow activity subscriptions operations. |
| `servicenow_aggregate` | `AGGREGATETOOL` | Manage servicenow aggregate operations. |
| `servicenow_application` | `APPLICATIONTOOL` | Manage servicenow application operations. |
| `servicenow_attachment` | `ATTACHMENTTOOL` | Manage servicenow attachment operations. |
| `servicenow_auth` | `AUTHTOOL` | Manage servicenow auth operations. |
| `servicenow_batch` | `BATCHTOOL` | Manage servicenow batch operations. |
| `servicenow_change_management` | `CHANGE_MANAGEMENTTOOL` | Manage servicenow change management operations. |
| `servicenow_cicd` | `CICDTOOL` | Manage servicenow cicd operations. |
| `servicenow_cilifecycle` | `CILIFECYCLETOOL` | Manage servicenow cilifecycle operations. |
| `servicenow_cmdb` | `CMDBTOOL` | Manage servicenow cmdb operations. |
| `servicenow_custom_api` | `CUSTOM_APITOOL` | Manage servicenow custom api operations. |
| `servicenow_data_classification` | `DATA_CLASSIFICATIONTOOL` | Manage servicenow data classification operations. |
| `servicenow_devops` | `DEVOPSTOOL` | Manage servicenow devops operations. |
| `servicenow_email` | `EMAILTOOL` | Manage servicenow email operations. |
| `servicenow_flows` | `FLOWSTOOL` | Manage servicenow flows operations. |
| `servicenow_hr` | `HRTOOL` | Manage servicenow hr operations. |
| `servicenow_import_sets` | `IMPORT_SETSTOOL` | Manage servicenow import sets operations. |
| `servicenow_incidents` | `INCIDENTSTOOL` | Manage servicenow incidents operations. |
| `servicenow_knowledge_management` | `KNOWLEDGE_MANAGEMENTTOOL` | Manage servicenow knowledge management operations. |
| `servicenow_metricbase` | `METRICBASETOOL` | Manage servicenow metricbase operations. |
| `servicenow_plugins` | `PLUGINSTOOL` | Manage servicenow plugins operations. |
| `servicenow_ppm` | `PPMTOOL` | Manage servicenow ppm operations. |
| `servicenow_product_inventory` | `PRODUCT_INVENTORYTOOL` | Manage servicenow product inventory operations. |
| `servicenow_service_qualification` | `SERVICE_QUALIFICATIONTOOL` | Manage servicenow service qualification operations. |
| `servicenow_source_control` | `SOURCE_CONTROLTOOL` | Manage servicenow source control operations. |
| `servicenow_table_api` | `TABLE_APITOOL` | Manage servicenow table api operations. |
| `servicenow_testing` | `TESTINGTOOL` | Manage servicenow testing operations. |
| `servicenow_update_sets` | `UPDATE_SETSTOOL` | Manage servicenow update sets operations. |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>119 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `servicenow_activate_plugin` | `DEVOPSTOOL` | Activate a plugin based on the provided plugin_id. |
| `servicenow_add_ci_lifecycle_action` | `CMDBTOOL` | Adds a specified CI action to a specified list of CIs. |
| `servicenow_add_table_record` | `SYSTEMTOOL` | Add a new record to the specified table. |
| `servicenow_api_request` | `SYSTEMTOOL` | Invoke the api_request operation. |
| `servicenow_app_repo_install` | `DEVOPSTOOL` | Install an application from the repository based on the provided parameters. |
| `servicenow_app_repo_publish` | `DEVOPSTOOL` | Publish an application to the repository based on the provided parameters. |
| `servicenow_app_repo_rollback` | `DEVOPSTOOL` | Rollback an application in the repository based on the provided parameters. |
| `servicenow_apply_remote_source_control_changes` | `OTHERTOOL` | Apply remote source control changes based on the provided parameters. |
| `servicenow_approve_change_request` | `CHANGETOOL` | Approve or reject a change request. |
| `servicenow_batch_install` | `OTHERTOOL` | Initiate a batch installation with the provided parameters. |
| `servicenow_batch_install_result` | `OTHERTOOL` | Get the result of a batch installation based on the provided result ID. |
| `servicenow_batch_request` | `OTHERTOOL` | Sends multiple REST API requests in a single call. |
| `servicenow_batch_rollback` | `OTHERTOOL` | Rollback a batch installation based on the provided rollback ID. |
| `servicenow_calculate_standard_change_request_risk` | `CHANGETOOL` | Calculate and update the risk of a standard change request. |
| `servicenow_check_change_request_conflict` | `CHANGETOOL` | Check for conflicts in a change request. |
| `servicenow_check_ci_lifecycle_compat_actions` | `CMDBTOOL` | Determines whether two specified CI actions are compatible. |
| `servicenow_check_ci_lifecycle_lease_expired` | `CMDBTOOL` | Determines whether the lease has expired for the requester. |
| `servicenow_check_ci_lifecycle_not_allowed_action` | `CMDBTOOL` | Determines whether a specified CI action is not allowed. |
| `servicenow_check_ci_lifecycle_not_allowed_ops_transition` | `CMDBTOOL` | Determines whether an operational state transition is allowed. |
| `servicenow_check_ci_lifecycle_requestor_valid` | `CMDBTOOL` | Determines whether the specified user is a valid requester. |
| `servicenow_check_devops_change_control` | `DEVOPSTOOL` | Checks if the orchestration task is under change control. |
| `servicenow_check_devops_step_mapping` | `DEVOPSTOOL` | Verifies that the information being passed is valid for the creation of an orchestration task. |
| `servicenow_check_service_qualification` | `OTHERTOOL` | Creates a technical service qualification request. |
| `servicenow_collect_graph_for_roots` | `CMDBTOOL` | Invoke the collect_graph_for_roots operation. |
| `servicenow_combo_suite_scan` | `OTHERTOOL` | Initiate a suite scan for a combo based on the provided combo_sys_id. |
| `servicenow_create_change_request` | `CHANGETOOL` | Create a new change request. |
| `servicenow_create_change_request_ci_association` | `CHANGETOOL` | Create associations between a change request and configuration items (CIs). |
| `servicenow_create_change_request_task` | `CHANGETOOL` | Create a new task associated with a change request. |
| `servicenow_create_cmdb_instance` | `CMDBTOOL` | Creates a single configuration item (CI). |
| `servicenow_create_cmdb_relation` | `CMDBTOOL` | Adds an inbound and/or outbound relation to the specified CI. |
| `servicenow_create_incident` | `INCIDENTTOOL` | Create a new incident record. |
| `servicenow_delete_attachment` | `OTHERTOOL` | Invoke the delete_attachment operation. |
| `servicenow_delete_change_request` | `CHANGETOOL` | Delete a change request. |
| `servicenow_delete_change_request_conflict_scan` | `CHANGETOOL` | Delete conflict scan information associated with a change request. |
| `servicenow_delete_change_request_task` | `CHANGETOOL` | Delete a task associated with a change request. |
| `servicenow_delete_ci_lifecycle_action` | `CMDBTOOL` | Removes a configuration item (CI) action for a list of CIs. |
| `servicenow_delete_cmdb_relation` | `CMDBTOOL` | Deletes the relation for the specified configuration item (CI). |
| `servicenow_delete_product_inventory` | `OTHERTOOL` | Deletes a specified product inventory record. |
| `servicenow_delete_table_record` | `SYSTEMTOOL` | Delete a record from the specified table. |
| `servicenow_extend_ci_lifecycle_lease` | `CMDBTOOL` | Extends the specified CI action's lease expiration time. |
| `servicenow_full_scan` | `OTHERTOOL` | Initiate a full instance scan. |
| `servicenow_get_account` | `OTHERTOOL` | Invoke the get_account operation. |
| `servicenow_get_activity_subscriptions` | `OTHERTOOL` | Invoke the get_activity_subscriptions operation. |
| `servicenow_get_application` | `OTHERTOOL` | Get information about an application. |
| `servicenow_get_attachment` | `OTHERTOOL` | Invoke the get_attachment operation. |
| `servicenow_get_change_request` | `CHANGETOOL` | Retrieve details of a specific change request. |
| `servicenow_get_change_request_ci` | `CHANGETOOL` | Retrieve the configuration item (CI) associated with a change request. |
| `servicenow_get_change_request_conflict` | `CHANGETOOL` | Retrieve conflict information associated with a change request. |
| `servicenow_get_change_request_models` | `CHANGETOOL` | Retrieve change request models based on specified parameters. |
| `servicenow_get_change_request_nextstate` | `CHANGETOOL` | Retrieve the next state of a specific change request. |
| `servicenow_get_change_request_schedule` | `CHANGETOOL` | Retrieve the schedule of a change request based on CI sys ID. |
| `servicenow_get_change_request_tasks` | `CHANGETOOL` | Retrieve tasks associated with a specific change request. |
| `servicenow_get_change_request_worker` | `CHANGETOOL` | Retrieve details of a change request worker. |
| `servicenow_get_change_requests` | `CHANGETOOL` | Retrieve change requests based on specified parameters. |
| `servicenow_get_ci_lifecycle_active_actions` | `CMDBTOOL` | Returns a list of active CI actions for the specified CI. |
| `servicenow_get_ci_lifecycle_status` | `CMDBTOOL` | Returns the current operational state for the specified CI. |
| `servicenow_get_cmdb` | `CMDBTOOL` | Get Configuration Management Database (CMDB) information based on specified parameters. |
| `servicenow_get_cmdb_instance` | `CMDBTOOL` | Returns attributes and relationship information for a specified CI record. |
| `servicenow_get_cmdb_instances` | `CMDBTOOL` | Returns the available configuration items (CI) for a specified CMDB class. |
| `servicenow_get_data_classification` | `OTHERTOOL` | Invoke the get_data_classification operation. |
| `servicenow_get_devops_change_info` | `DEVOPSTOOL` | Retrieves change request details for a specified orchestration pipeline execution. |
| `servicenow_get_devops_code_schema` | `DEVOPSTOOL` | Returns the schema object for a specified code resource. |
| `servicenow_get_devops_onboarding_status` | `DEVOPSTOOL` | Returns the current status of the specified onboarding event. |
| `servicenow_get_devops_orchestration_schema` | `DEVOPSTOOL` | Returns the schema object for a specified orchestration resource. |
| `servicenow_get_devops_plan_schema` | `DEVOPSTOOL` | Returns the schema object for a specific plan. |
| `servicenow_get_featured_knowledge_article` | `KNOWLEDGETOOL` | Get featured Knowledge Base articles. |
| `servicenow_get_flow_metadata` | `SYSTEMTOOL` | Fetch rich metadata for any flow/subflow. |
| `servicenow_get_hr_profile` | `OTHERTOOL` | Invoke the get_hr_profile operation. |
| `servicenow_get_import_set` | `OTHERTOOL` | Get details of a specific import set record. |
| `servicenow_get_incident` | `INCIDENTTOOL` | Retrieve details of a specific incident record. |
| `servicenow_get_incidents` | `INCIDENTTOOL` | Retrieve details of incident records. |
| `servicenow_get_knowledge_article` | `KNOWLEDGETOOL` | Get Knowledge Base article. |
| `servicenow_get_knowledge_article_attachment` | `KNOWLEDGETOOL` | Get Knowledge Base article attachment. |
| `servicenow_get_knowledge_articles` | `KNOWLEDGETOOL` | Get all Knowledge Base articles. |
| `servicenow_get_most_viewed_knowledge_articles` | `KNOWLEDGETOOL` | Get most viewed Knowledge Base articles. |
| `servicenow_get_product_inventory` | `OTHERTOOL` | Retrieves a list of all product inventories. |
| `servicenow_get_service_qualification` | `OTHERTOOL` | Retrieves a technical qualification request by ID or list all. |
| `servicenow_get_standard_change_request_model` | `CHANGETOOL` | Retrieve details of a standard change request model. |
| `servicenow_get_standard_change_request_template` | `CHANGETOOL` | Retrieve details of a standard change request template. |
| `servicenow_get_standard_change_request_templates` | `CHANGETOOL` | Retrieve standard change request templates based on specified parameters. |
| `servicenow_get_stats` | `SYSTEMTOOL` | Invoke the get_stats operation. |
| `servicenow_get_table` | `SYSTEMTOOL` | Get records from the specified table based on provided parameters. |
| `servicenow_get_table_record` | `SYSTEMTOOL` | Get a specific record from the specified table. |
| `servicenow_import_repository` | `DEVOPSTOOL` | Import a repository based on the provided parameters. |
| `servicenow_ingest_cmdb_data` | `CMDBTOOL` | Inserts records into the Import Set table associated with the data source. |
| `servicenow_insert_cost_plans` | `OTHERTOOL` | Creates cost plans. |
| `servicenow_insert_import_set` | `OTHERTOOL` | Insert a new record into the specified import set. |
| `servicenow_insert_multiple_import_sets` | `OTHERTOOL` | Insert multiple records into the specified import set. |
| `servicenow_insert_project_tasks` | `OTHERTOOL` | Creates a project and associated project tasks. |
| `servicenow_instance_scan_progress` | `OTHERTOOL` | Get progress information for an instance scan based on the provided progress ID. |
| `servicenow_metricbase_insert` | `OTHERTOOL` | Invoke the metricbase_insert operation. |
| `servicenow_patch_cmdb_instance` | `CMDBTOOL` | Replaces attributes in the specified CI record (PATCH). |
| `servicenow_patch_table_record` | `SYSTEMTOOL` | Partially update a record in the specified table. |
| `servicenow_point_scan` | `OTHERTOOL` | Initiate a point instance scan based on the provided parameters. |
| `servicenow_process_service_qualification_result` | `OTHERTOOL` | Processes a technical service qualification result. |
| `servicenow_progress` | `OTHERTOOL` | Get progress information based on the provided progress ID. |
| `servicenow_refresh_auth_token` | `SYSTEMTOOL` | Refresh the authentication token |
| `servicenow_refresh_change_request_impacted_services` | `CHANGETOOL` | Refresh impacted services for a change request. |
| `servicenow_register_ci_lifecycle_operator` | `CMDBTOOL` | Registers an operator for a non-workflow user. |
| `servicenow_register_devops_artifact` | `DEVOPSTOOL` | Enables orchestration tools to register artifacts into a ServiceNow instance. |
| `servicenow_rollback_plugin` | `DEVOPSTOOL` | Rollback a plugin based on the provided plugin_id. |
| `servicenow_run_test_suite` | `OTHERTOOL` | Run a test suite based on the provided parameters. |
| `servicenow_send_email` | `SYSTEMTOOL` | Invoke the send_email operation. |
| `servicenow_set_ci_lifecycle_status` | `CMDBTOOL` | Sets the operational state for a specified list of CIs. |
| `servicenow_suite_scan` | `OTHERTOOL` | Initiate a suite scan based on the provided suite_sys_id and sys_ids. |
| `servicenow_unregister_ci_lifecycle_operator` | `CMDBTOOL` | Unregisters an operator for non-workflow users. |
| `servicenow_update_change_request` | `CHANGETOOL` | Update details of a change request. |
| `servicenow_update_change_request_first_available` | `CHANGETOOL` | Update the schedule of a change request to the first available slot. |
| `servicenow_update_change_request_task` | `CHANGETOOL` | Update details of a task associated with a change request. |
| `servicenow_update_cmdb_instance` | `CMDBTOOL` | Updates the specified CI record (PUT). |
| `servicenow_update_set_back_out` | `DEVOPSTOOL` | Backs out an installation operation that was performed on an update set with a given sys_id. |
| `servicenow_update_set_commit` | `DEVOPSTOOL` | Commits an update set with a given sys_id. |
| `servicenow_update_set_commit_multiple` | `DEVOPSTOOL` | Commits multiple update sets in a single request according to the order that they're provided. |
| `servicenow_update_set_create` | `DEVOPSTOOL` | Creates a new update set and inserts the new record in the Update Sets [sys_update_set] table. |
| `servicenow_update_set_preview` | `DEVOPSTOOL` | Previews an update set to check for any conflicts and retrieve progress information about the update set operation. |
| `servicenow_update_set_retrieve` | `DEVOPSTOOL` | Retrieves an update set with a given sys_id and allows you to remove the existing retrieved update set from the instance. |
| `servicenow_update_table_record` | `SYSTEMTOOL` | Fully update a record in the specified table. |
| `servicenow_upload_attachment` | `OTHERTOOL` | Invoke the upload_attachment operation. |
| `servicenow_workflow_to_mermaid` | `SYSTEMTOOL` | Generates a Mermaid diagram representing the relationships between ServiceNow flows and subflows. |

</details>

_30 action-routed tool(s) (default) · 119 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (`condensed` default · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

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

<!-- MCP-CONFIG-EXAMPLES:START -->

> **Install the slim `[mcp]` extra.** All examples install `servicenow-api[mcp]` — the
> MCP-server extra that pulls only the FastMCP / FastAPI tooling (`agent-utilities[mcp]`).
> It deliberately **excludes** the heavy agent runtime (`pydantic-ai`, the epistemic-graph
> engine, `dspy`, `llama-index`), so `uvx` / container installs are far smaller. Use the
> full `[agent]` extra only when you need the integrated Pydantic AI agent.

#### stdio Transport (local IDEs — Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "servicenow-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "servicenow-api[mcp]",
        "servicenow-mcp"
      ],
      "env": {
        "MCP_TOOL_MODE": "condensed",
        "ACCOUNTTOOL": "True",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "True",
        "AGGREGATETOOL": "True",
        "APPLICATIONTOOL": "True",
        "ATTACHMENTTOOL": "True",
        "AUDIENCE": "",
        "AUTHTOOL": "True",
        "BATCHTOOL": "True",
        "CHANGE_MANAGEMENTTOOL": "True",
        "CICDTOOL": "True",
        "CILIFECYCLETOOL": "True",
        "CMDBTOOL": "True",
        "CUSTOM_APITOOL": "True",
        "DATA_CLASSIFICATIONTOOL": "True",
        "DELEGATED_SCOPES": "api",
        "DEVOPSTOOL": "True",
        "EMAILTOOL": "True",
        "FLOWSTOOL": "True",
        "HRTOOL": "True",
        "IMPORT_SETSTOOL": "True",
        "INCIDENTSTOOL": "True",
        "KNOWLEDGE_MANAGEMENTTOOL": "True",
        "METRICBASETOOL": "True",
        "MISCTOOL": "True",
        "OPENAPI_CLIENT_ID": "your_openapi_client_id_here",
        "OPENAPI_PASSWORD": "your_openapi_password_here",
        "OPENAPI_USERNAME": "your_openapi_username_here",
        "PLUGINSTOOL": "True",
        "PPMTOOL": "True",
        "PRODUCT_INVENTORYTOOL": "True",
        "SERVICENOW_CLIENT_ID": "",
        "SERVICENOW_CLIENT_SECRET": "your_servicenow_client_secret_here",
        "SERVICENOW_INSTANCE": "https://dev350360.service-now.com",
        "SERVICENOW_PASSWORD": "your_servicenow_password_here",
        "SERVICENOW_URL": "https://dev350360.service-now.com",
        "SERVICENOW_USERNAME": "admin",
        "SERVICE_QUALIFICATIONTOOL": "True",
        "SOURCE_CONTROLTOOL": "True",
        "TABLE_APITOOL": "True",
        "TESTINGTOOL": "True",
        "UPDATE_SETSTOOL": "True"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (networked / production)

```json
{
  "mcpServers": {
    "servicenow-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "servicenow-api[mcp]",
        "servicenow-mcp",
        "--transport",
        "streamable-http",
        "--port",
        "8000"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "MCP_TOOL_MODE": "condensed",
        "ACCOUNTTOOL": "True",
        "ACTIVITY_SUBSCRIPTIONSTOOL": "True",
        "AGGREGATETOOL": "True",
        "APPLICATIONTOOL": "True",
        "ATTACHMENTTOOL": "True",
        "AUDIENCE": "",
        "AUTHTOOL": "True",
        "BATCHTOOL": "True",
        "CHANGE_MANAGEMENTTOOL": "True",
        "CICDTOOL": "True",
        "CILIFECYCLETOOL": "True",
        "CMDBTOOL": "True",
        "CUSTOM_APITOOL": "True",
        "DATA_CLASSIFICATIONTOOL": "True",
        "DELEGATED_SCOPES": "api",
        "DEVOPSTOOL": "True",
        "EMAILTOOL": "True",
        "FLOWSTOOL": "True",
        "HRTOOL": "True",
        "IMPORT_SETSTOOL": "True",
        "INCIDENTSTOOL": "True",
        "KNOWLEDGE_MANAGEMENTTOOL": "True",
        "METRICBASETOOL": "True",
        "MISCTOOL": "True",
        "OPENAPI_CLIENT_ID": "your_openapi_client_id_here",
        "OPENAPI_PASSWORD": "your_openapi_password_here",
        "OPENAPI_USERNAME": "your_openapi_username_here",
        "PLUGINSTOOL": "True",
        "PPMTOOL": "True",
        "PRODUCT_INVENTORYTOOL": "True",
        "SERVICENOW_CLIENT_ID": "",
        "SERVICENOW_CLIENT_SECRET": "your_servicenow_client_secret_here",
        "SERVICENOW_INSTANCE": "https://dev350360.service-now.com",
        "SERVICENOW_PASSWORD": "your_servicenow_password_here",
        "SERVICENOW_URL": "https://dev350360.service-now.com",
        "SERVICENOW_USERNAME": "admin",
        "SERVICE_QUALIFICATIONTOOL": "True",
        "SOURCE_CONTROLTOOL": "True",
        "TABLE_APITOOL": "True",
        "TESTINGTOOL": "True",
        "UPDATE_SETSTOOL": "True"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed Streamable-HTTP instance by `url`:

```json
{
  "mcpServers": {
    "servicenow-mcp": {
      "url": "http://localhost:8000/servicenow-mcp/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name servicenow-mcp-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e MCP_TOOL_MODE=condensed \
  -e ACCOUNTTOOL=True \
  -e ACTIVITY_SUBSCRIPTIONSTOOL=True \
  -e AGGREGATETOOL=True \
  -e APPLICATIONTOOL=True \
  -e ATTACHMENTTOOL=True \
  -e AUDIENCE="" \
  -e AUTHTOOL=True \
  -e BATCHTOOL=True \
  -e CHANGE_MANAGEMENTTOOL=True \
  -e CICDTOOL=True \
  -e CILIFECYCLETOOL=True \
  -e CMDBTOOL=True \
  -e CUSTOM_APITOOL=True \
  -e DATA_CLASSIFICATIONTOOL=True \
  -e DELEGATED_SCOPES=api \
  -e DEVOPSTOOL=True \
  -e EMAILTOOL=True \
  -e FLOWSTOOL=True \
  -e HRTOOL=True \
  -e IMPORT_SETSTOOL=True \
  -e INCIDENTSTOOL=True \
  -e KNOWLEDGE_MANAGEMENTTOOL=True \
  -e METRICBASETOOL=True \
  -e MISCTOOL=True \
  -e OPENAPI_CLIENT_ID=your_openapi_client_id_here \
  -e OPENAPI_PASSWORD=your_openapi_password_here \
  -e OPENAPI_USERNAME=your_openapi_username_here \
  -e PLUGINSTOOL=True \
  -e PPMTOOL=True \
  -e PRODUCT_INVENTORYTOOL=True \
  -e SERVICENOW_CLIENT_ID="" \
  -e SERVICENOW_CLIENT_SECRET=your_servicenow_client_secret_here \
  -e SERVICENOW_INSTANCE=https://dev350360.service-now.com \
  -e SERVICENOW_PASSWORD=your_servicenow_password_here \
  -e SERVICENOW_URL=https://dev350360.service-now.com \
  -e SERVICENOW_USERNAME=admin \
  -e SERVICE_QUALIFICATIONTOOL=True \
  -e SOURCE_CONTROLTOOL=True \
  -e TABLE_APITOOL=True \
  -e TESTINGTOOL=True \
  -e UPDATE_SETSTOOL=True \
  knucklessg1/servicenow-api:mcp
```

_Auto-generated from the code-read env surface (`MCP_TOOL_MODE` + package vars) — do not edit._
<!-- MCP-CONFIG-EXAMPLES:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`servicenow-api` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/servicenow-api/deployment/) has full, copy-paste
`mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://servicenow-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

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

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` |  |
| `PORT` | `8000` |  |
| `TRANSPORT` | `stdio` | options: stdio, streamable-http, sse |
| `ENABLE_OTEL` | `True` |  |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:8080/api/public/otel` |  |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` | `pk-...` |  |
| `OTEL_EXPORTER_OTLP_SECRET_KEY` | `sk-...` |  |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |  |
| `EUNOMIA_TYPE` | `none` | options: none, embedded, remote |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` |  |
| `EUNOMIA_REMOTE_URL` | `http://eunomia-server:8000` |  |
| `SERVICENOW_INSTANCE` | `https://dev350360.service-now.com` |  |
| `SERVICENOW_URL` | `https://dev350360.service-now.com` | alias for SERVICENOW_INSTANCE |
| `SERVICENOW_USERNAME` | `admin` |  |
| `SERVICENOW_CLIENT_ID` | — |  |
| `SERVICENOW_SSL_VERIFY` | `True` |  |
| `DEBUG` | `False` |  |
| `PYTHONUNBUFFERED` | `1` |  |
| `SERVICENOW_PASSWORD` | `your_servicenow_password_here` |  |
| `SERVICENOW_CLIENT_SECRET` | `your_servicenow_client_secret_here` |  |
| `AUDIENCE` | — | downstream token audience (defaults to the ServiceNow instance) |
| `DELEGATED_SCOPES` | `api` | scopes requested during token exchange |
| `OPENAPI_USERNAME` | `your_openapi_username_here` |  |
| `OPENAPI_PASSWORD` | `your_openapi_password_here` |  |
| `OPENAPI_CLIENT_ID` | `your_openapi_client_id_here` |  |
| `OPENAPI_CLIENT_SECRET` | `your_openapi_client_secret_here` |  |
| `MISCTOOL` | `True` |  |
| `FLOWSTOOL` | `True` |  |
| `APPLICATIONTOOL` | `True` |  |
| `CMDBTOOL` | `True` |  |
| `CICDTOOL` | `True` |  |
| `PLUGINSTOOL` | `True` |  |
| `SOURCE_CONTROLTOOL` | `True` |  |
| `TESTINGTOOL` | `True` |  |
| `UPDATE_SETSTOOL` | `True` |  |
| `BATCHTOOL` | `True` |  |
| `CHANGE_MANAGEMENTTOOL` | `True` |  |
| `CILIFECYCLETOOL` | `True` |  |
| `DEVOPSTOOL` | `True` |  |
| `IMPORT_SETSTOOL` | `True` |  |
| `INCIDENTSTOOL` | `True` |  |
| `KNOWLEDGE_MANAGEMENTTOOL` | `True` |  |
| `TABLE_APITOOL` | `True` |  |
| `AUTHTOOL` | `True` |  |
| `CUSTOM_APITOOL` | `True` |  |
| `EMAILTOOL` | `True` |  |
| `DATA_CLASSIFICATIONTOOL` | `True` |  |
| `ATTACHMENTTOOL` | `True` |  |
| `AGGREGATETOOL` | `True` |  |
| `ACTIVITY_SUBSCRIPTIONSTOOL` | `True` |  |
| `ACCOUNTTOOL` | `True` |  |
| `HRTOOL` | `True` |  |
| `METRICBASETOOL` | `True` |  |
| `SERVICE_QUALIFICATIONTOOL` | `True` |  |
| `PPMTOOL` | `True` |  |
| `PRODUCT_INVENTORYTOOL` | `True` |  |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_56 package + 12 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->


Every variable the server reads. See [`.env.example`](.env.example) for a copy-paste
starting point.

### Connection & Credentials
| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICENOW_INSTANCE` | ServiceNow instance base URL | — |
| `SERVICENOW_USERNAME` | Account username (basic auth) | — |
| `SERVICENOW_PASSWORD` | Account password (basic auth) | — |
| `SERVICENOW_CLIENT_ID` | OAuth client id | — |
| `SERVICENOW_CLIENT_SECRET` | OAuth client secret | — |
| `SERVICENOW_SSL_VERIFY` | TLS certificate verification | `True` |
| `DEBUG` | Verbose logging | `False` |
| `PYTHONUNBUFFERED` | Unbuffered stdout (recommended in containers) | `1` |

### MCP server / transport
| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSPORT` | `stdio`, `streamable-http`, or `sse` | `stdio` |
| `HOST` | Bind host (HTTP transports) | `0.0.0.0` |
| `PORT` | Bind port (HTTP transports) | `8000` |
| `MCP_TOOL_MODE` | Tool surface: `condensed`, `verbose`, or `both` | `condensed` |
| `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS` | Comma-separated tool allow/deny list | — |
| `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS` | Comma-separated tag allow/deny list | — |

### Telemetry & governance
| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_OTEL` | Enable OpenTelemetry export | `True` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | — |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` / `OTEL_EXPORTER_OTLP_SECRET_KEY` | OTLP auth keys | — |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | OTLP protocol (e.g. `http/protobuf`) | — |
| `EUNOMIA_TYPE` | Authorization mode: `none`, `embedded`, `remote` | `none` |
| `EUNOMIA_POLICY_FILE` | Embedded policy file | `mcp_policies.json` |
| `EUNOMIA_REMOTE_URL` | Remote Eunomia server URL | — |

### Tool toggles
Each action-routed tool can be disabled individually via its toggle env var (set to `false`).
The full list is in the [Available MCP Tools](#available-mcp-tools) table above
(e.g. `INCIDENTSTOOL`, `CHANGE_MANAGEMENTTOOL`, `TABLE_APITOOL`, `CMDBTOOL`).

---

## Installation

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `servicenow-api[mcp]` | Slim MCP server only (`agent-utilities[mcp]` — FastMCP/FastAPI) | You only run the **MCP server** (smallest install / image) |
| `servicenow-api[agent]` | Full agent runtime (`agent-utilities[agent,logfire]` — Pydantic AI + the epistemic-graph engine) | You run the **integrated agent** |
| `servicenow-api[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# MCP server only (recommended for tool hosting — slim deps)
uv pip install "servicenow-api[mcp]"

# Full agent runtime (Pydantic AI + epistemic-graph engine)
uv pip install "servicenow-api[agent]"

# Everything (development)
uv pip install "servicenow-api[all]"      # or: python -m pip install "servicenow-api[all]"
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `knucklessg1/servicenow-api:mcp` | `--target mcp` | `servicenow-api[mcp]` — **slim**, no engine/`pydantic-ai`/`dspy`/`llama-index`/`tree-sitter` | `servicenow-mcp` |
| `knucklessg1/servicenow-api:latest` | `--target agent` (default) | `servicenow-api[agent]` — **full** agent runtime + epistemic-graph engine | `servicenow-agent` |

```bash
docker build --target mcp   -t knucklessg1/servicenow-api:mcp    docker/   # slim MCP server
docker build --target agent -t knucklessg1/servicenow-api:latest docker/   # full agent
```

`docker/mcp.compose.yml` runs the slim `:mcp` server; `docker/agent.compose.yml` runs the
agent (`:latest`) with a co-located `:mcp` sidecar.

### Knowledge-graph database (`epistemic-graph`)

The **full agent** (`[agent]` / `:latest`) embeds the **epistemic-graph** engine (pulled in
transitively via `agent-utilities[agent]`). For production — or to share one knowledge graph
across multiple agents — run **epistemic-graph as its own database container** and point the
agent at it instead of embedding it. Deployment recipes (single-node + Raft HA), connection
config, and the full database architecture (with diagrams) are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).
The slim `[mcp]` server does **not** require the database.

---

## Documentation

The complete documentation is published as the
[official documentation site](https://knuckles-team.github.io/servicenow-api/) and is
the recommended reference for installation, deployment, and day-to-day operation.

| Page | Contents |
|---|---|
| [Installation](https://knuckles-team.github.io/servicenow-api/installation/) | pip, source, extras, prebuilt Docker image |
| [Deployment](https://knuckles-team.github.io/servicenow-api/deployment/) | run the MCP and agent servers, Compose, Caddy + Technitium, env config |
| [Usage](https://knuckles-team.github.io/servicenow-api/usage/) | the MCP tools, the `Api` client, the command line |
| [Overview](https://knuckles-team.github.io/servicenow-api/overview/) | the standardized agent-package pattern and MCP configuration |
| [Concepts](https://knuckles-team.github.io/servicenow-api/concepts/) | concept registry (`CONCEPT:SNOW-*`) |

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


<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `servicenow-api` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx servicenow-mcp` · or `uv tool install servicenow-api` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `knucklessg1/servicenow-api:latest` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

<!-- END agent-os-genesis-deploy -->
