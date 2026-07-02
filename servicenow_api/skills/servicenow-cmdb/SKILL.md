---
name: servicenow-cmdb
description: >-
  ITOM CMDB operations on the ServiceNow CMDB + CI Lifecycle Management APIs via
  the servicenow-api MCP server — query configuration items by class, read a CI
  with its attributes and relations, create/update/patch CI instances, manage CI
  relationships, and drive the CI lifecycle (status, actions, leases, operators).
  Use when the agent must inspect or maintain the CMDB graph or govern a CI's
  lifecycle state. Do NOT use for incidents (servicenow-incident-management),
  change requests (servicenow-change-management), or generic non-CMDB table CRUD
  (servicenow-table-api); prefer those.
license: MIT
tags: [servicenow, cmdb, ci-lifecycle, itom, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow CMDB

ITOM access to the ServiceNow **CMDB** (configuration items, classes, attributes,
relationships) and **CI Lifecycle Management** (lifecycle status, actions, leases,
and operator registration). Two condensed tools cover the two concerns.

## When to use
- Query CIs by class; read one CI with its attributes and relationships.
- Create / update / patch CI instances; add or delete CI relationships.
- Bulk-ingest CMDB data.
- Get or set a CI's lifecycle status; manage lifecycle actions, leases, and
  operators.

## When NOT to use
- Incidents / change requests → their dedicated skills.
- Associating an existing CI to a change → `servicenow-change-management`.
- Generic CRUD on non-CMDB tables → `servicenow-table-api`.

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
Prefer the **condensed** tools; each takes `action` + a `params_json` **JSON
string** whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_cmdb` | `get_cmdb`, `get_cmdb_instances`, `get_cmdb_instance`, `create_cmdb_instance`, `update_cmdb_instance`, `patch_cmdb_instance`, `create_cmdb_relation`, `delete_cmdb_relation`, `ingest_cmdb_data` |
| `servicenow_cilifecycle` | `get_ci_lifecycle_status`, `set_ci_lifecycle_status`, `get_ci_lifecycle_active_actions`, `add_ci_lifecycle_action`, `delete_ci_lifecycle_action`, `extend_ci_lifecycle_lease`, `check_ci_lifecycle_compat_actions`, `check_ci_lifecycle_lease_expired`, `check_ci_lifecycle_not_allowed_action`, `check_ci_lifecycle_not_allowed_ops_transition`, `check_ci_lifecycle_requestor_valid`, `register_ci_lifecycle_operator`, `unregister_ci_lifecycle_operator` |

### Key parameters
- `class_name` (a.k.a. CMDB class, e.g. `cmdb_ci_server`, `cmdb_ci_linux_server`)
  — for `get_cmdb_instances` / `get_cmdb` and instance create.
- `sys_id` — the CI sys_id for single-instance read/update/patch and all
  lifecycle actions.
- `data` — object of field→value for create/update/patch CI instances.
- Relationship fields (`parent`, `child`, `type`) for
  `create_cmdb_relation` / `delete_cmdb_relation`.
- Lifecycle keys (`status`, `action`, operator/requestor identifiers, lease info)
  — the lifecycle-operator/action model is described in
  `references/ci-lifecycle.md`; read it before calling `servicenow_cilifecycle`.

## Recipes (`params_json`)
Query CIs of a class (`get_cmdb_instances`, few fields):
```json
{"class_name":"cmdb_ci_linux_server","sysparm_query":"operational_status=1","sysparm_fields":"name,sys_id,ip_address,operational_status","sysparm_limit":25,"sysparm_display_value":"true"}
```
Get one CI with attributes + relations (`get_cmdb_instance`):
```json
{"class_name":"cmdb_ci_linux_server","sys_id":"<ci_sys_id>"}
```
Create a CI relationship (`create_cmdb_relation`):
```json
{"parent":"<app_ci_sys_id>","child":"<server_ci_sys_id>","type":"Runs on::Runs"}
```
Get, then set, a CI's lifecycle status (`servicenow_cilifecycle`, two calls):
```json
{"sys_id":"<ci_sys_id>"}
```
```json
{"sys_id":"<ci_sys_id>","status":"in_use"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- CMDB class names are hierarchical (`cmdb_ci` → `cmdb_ci_hardware` →
  `cmdb_ci_server` → …); query the most specific class you can, and confirm the
  exact class name on the instance (they vary by installed plugins).
- `get_cmdb_instance` returns the CI's attributes **and** outbound/inbound
  relations — use it (not a raw table read) when you need the relationship graph.
- Relationship `type` is a relation-type name (e.g. `Runs on::Runs`,
  `Depends on::Used by`) — the two halves are the parent→child and child→parent
  labels; get them right or the relation renders backwards.
- Lifecycle transitions are governed — a status/action can be rejected as
  not-allowed or blocked by an expired lease; use the `check_*` actions
  (`check_ci_lifecycle_not_allowed_action`,
  `check_ci_lifecycle_not_allowed_ops_transition`,
  `check_ci_lifecycle_lease_expired`) to validate **before** mutating. See
  `references/ci-lifecycle.md`.
- `ingest_cmdb_data` is for bulk load — validate class + payload shape on a single
  instance first.

## Related
- Associate these CIs to a change → `servicenow-change-management`.
- Impacted-services recompute on changes reads the CMDB relationship graph
  maintained here.
