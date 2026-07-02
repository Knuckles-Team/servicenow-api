---
name: servicenow-platform-utilities
description: >-
  ServiceNow cross-domain platform helpers — send notification email, render deployed
  Flow Designer flows to Mermaid and read flow metadata, fetch data-classification and
  application metadata, list activity subscriptions, and push MetricBase time-series
  via the servicenow-api MCP server. Use when the agent needs a grab-bag platform
  utility: email a user, visualize or introspect a live flow, look up an app or its data
  classification, or write a metric point. Do NOT use for table CRUD
  (servicenow-table-api), release/CI-CD or update sets (servicenow-cicd-devops), data
  ingest/attachments/batch (servicenow-import-attachment-batch), or HR/PPM
  (servicenow-hr-ppm).
license: MIT
tags: [servicenow, email, flows, metricbase, platform, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Platform Utilities (cross-domain helpers)

A grab-bag of platform-level helpers that don't belong to any one domain: email,
flow introspection/visualization, classification & app metadata, activity
subscriptions, and MetricBase writes. Six condensed tools.

## When to use
- Send a notification email from the instance (`send_email`).
- Render a **deployed** flow to a Mermaid diagram, collect a flow graph from roots, or
  read a flow's metadata (`servicenow_flows`).
- Look up a record's data-classification (`get_data_classification`).
- Fetch application metadata (`get_application`).
- List activity subscriptions (`get_activity_subscriptions`).
- Insert a MetricBase time-series point (`metricbase_insert`).

## When NOT to use
- Generic table CRUD / aggregate / raw REST → `servicenow-table-api`.
- App deploy, scans, update sets, ATF → `servicenow-cicd-devops`.
- Bulk row ingest / attachments / batch → `servicenow-import-attachment-batch`.
- HR profiles / PPM inserts → `servicenow-hr-ppm`.
- Authoring/editing flows locally (Flow Designer dev-tooling) → the sibling skill
  `servicenow-workflow-studio`; `workflow_to_mermaid` here **complements** it by
  rendering an already-deployed flow.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`servicenow-api`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `SERVICENOW_INSTANCE` | ✅ | Instance URL (alias `SERVICENOW_URL`) |
| `SERVICENOW_USERNAME` | ✅ | Basic-auth user |
| `SERVICENOW_PASSWORD` | ✅ | Basic-auth password |
| `SERVICENOW_CLIENT_ID` / `SERVICENOW_CLIENT_SECRET` | optional | OAuth2 |
| `SERVICENOW_SSL_VERIFY` | optional | TLS verification toggle |

Full env/tag matrix (do not re-document here): the mcp-client reference
`agent-tools/mcp-client/references/servicenow-api.md`. `MCP_TOOL_MODE`
(`condensed`|`verbose`|`both`) selects the condensed surface (used below) vs. the
one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tools; each takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_email` | `send_email` |
| `servicenow_flows` | `workflow_to_mermaid`, `collect_graph_for_roots`, `get_flow_metadata` |
| `servicenow_data_classification` | `get_data_classification` |
| `servicenow_application` | `get_application` |
| `servicenow_activity_subscriptions` | `get_activity_subscriptions` |
| `servicenow_metricbase` | `metricbase_insert` |

### Key parameters
- Email: `recipients` (or `to`), `subject`, `body` / `html`, optional
  `cc`, `bcc`, `table` + `record_sys_id` to associate the email with a record.
- Flows: `sys_id` (the flow) for `workflow_to_mermaid` / `get_flow_metadata`;
  `root_sys_ids` (array) for `collect_graph_for_roots`.
- Data classification: `table` + `sys_id` (the record to classify).
- Application: `sys_id` (the `sys_app` record).
- Activity subscriptions: filter params (e.g. `user_sys_id`).
- MetricBase: `subject` (the record the metric belongs to), `metric`, `values`
  (timestamped points).

## Recipes (`params_json`)
Send a notification email (`send_email`):
```json
{"recipients":"ada@example.com","subject":"Deploy complete","body":"Release 1.4.0 is live.","table":"incident","record_sys_id":"<sys_id>"}
```
Render a deployed flow to Mermaid (`workflow_to_mermaid`) — pairs with the
`servicenow-workflow-studio` dev-tooling skill for authoring:
```json
{"sys_id":"<flow_sys_id>"}
```
Get application metadata (`get_application`):
```json
{"sys_id":"<sys_app_sys_id>"}
```
Insert a MetricBase point (`metricbase_insert`):
```json
{"subject":"<cmdb_ci_sys_id>","metric":"cpu_utilization","values":[{"timestamp":"2026-07-01T12:00:00Z","value":73.4}]}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `workflow_to_mermaid` visualizes an **already-deployed** flow (read-only); it does not
  author or edit — use the `servicenow-workflow-studio` dev-tooling skill for that.
- `send_email` respects instance **email/notification config** (send may be queued or
  suppressed by the outbound email settings); a successful call is not a delivery guarantee.
- `metricbase_insert` requires the **MetricBase** plugin and a metric definition bound to
  the subject table; timestamps should be ISO-8601 UTC.
- `get_data_classification` and `get_application` are metadata reads — pass the exact
  target (`table`+`sys_id`, or `sys_app` sys_id); discover ids first with
  `servicenow-table-api` if unknown.
