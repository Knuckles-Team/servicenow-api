---
name: servicenow-table-api
description: >-
  Foundational ServiceNow data access — generic Table API CRUD, Aggregate/stats
  roll-ups, and raw REST escape-hatch via the servicenow-api MCP server. Use when
  the agent must read, insert, update, patch, delete, count, or aggregate records in
  ANY ServiceNow table (including scoped app tables with no dedicated API), or call a
  REST endpoint the typed tools do not cover. Teaches encoded-query (sysparm_query)
  syntax, field/pagination controls, and group-by aggregation. Do NOT use for a
  domain that has its own skill (incidents → servicenow-incident-management, change →
  servicenow-change-management, CMDB → servicenow-cmdb, TRM/APM → servicenow-trm,
  risk/GRC → servicenow-irm-grc, security → servicenow-secops); prefer those.
license: MIT
tags: [servicenow, table-api, aggregate, custom-api, rest-api, crud, encoded-query, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Table API (foundational)

The generic, table-agnostic primitive that every other ServiceNow skill builds on.
When a module has **no dedicated REST API** (TRM/APM, IRM/GRC, SecOps, custom scoped
apps), you drive it through **these** tools against its scoped tables.

## When to use
- CRUD on any table by name (`incident`, `cmdb_ci`, `sn_apm_*`, `sn_risk_*`, `u_*` …).
- Server-side counts / group-by roll-ups (Aggregate API).
- Any REST call the typed tools don't expose (raw escape-hatch).

## When NOT to use
- A domain with its own skill — use it instead (it has richer, safer recipes):
  `servicenow-incident-management`, `servicenow-change-management`, `servicenow-cmdb`,
  `servicenow-knowledge`, `servicenow-trm`, `servicenow-irm-grc`, `servicenow-secops`,
  `servicenow-telecom-tmf`. Fall back here only for tables those skills don't cover.

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
(`condensed`|`verbose`|`both`) selects the 30-tool condensed surface (used below) vs.
the 119 one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tools; each takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_table_api` | `get_table`, `get_table_record`, `add_table_record`, `update_table_record`, `patch_table_record`, `delete_table_record` |
| `servicenow_aggregate` | `get_stats` |
| `servicenow_custom_api` | `api_request` |
| `servicenow_auth` | `refresh_auth_token` |

### Key parameters (Table API)
- `table` (required) — table name.
- `table_record_sys_id` — sys_id for single-record get/update/patch/delete.
- `data` — object of field→value for add/update/patch.
- `sysparm_query` — encoded query (see below).
- `sysparm_fields` — comma-separated fields to return (keep responses small).
- `sysparm_limit`, `sysparm_offset` — pagination.
- `sysparm_display_value` — `true` | `false` | `all` (resolve reference/choice labels).
- `name_value_pairs` — simple field filters as an alternative to `sysparm_query`.

## Encoded-query (`sysparm_query`) cheat-sheet
- Equality: `active=true`, `priority=1`
- AND: `^` → `active=true^priority=1`
- OR: `^OR` → `state=1^ORstate=2`
- Operators: `!=`, `>`, `<`, `>=`, `<=`, `STARTSWITH`, `ENDSWITH`, `LIKE` (contains),
  `IN` → `state=IN1,2,3`, `ISEMPTY`, `ISNOTEMPTY`
- Dates: `sys_created_onONToday@...` or `>=javascript:gs.beginningOfLastMonth()`
- Order: `^ORDERBYfield` (asc) / `^ORDERBYDESCfield` (desc)
- Example: `active=true^priority<=2^ORDERBYDESCsys_created_on`

## Recipes (`params_json`)
Query open, high-priority records (return a few fields, newest first):
```json
{"table":"incident","sysparm_query":"active=true^priority<=2^ORDERBYDESCsys_created_on","sysparm_fields":"number,short_description,priority,state","sysparm_limit":20,"sysparm_display_value":"true"}
```
Get one record by sys_id:
```json
{"table":"cmdb_ci","table_record_sys_id":"<sys_id>","sysparm_display_value":"all"}
```
Insert a record (`add_table_record`):
```json
{"table":"u_my_table","data":{"u_name":"example","u_active":"true"}}
```
Partial update (`patch_table_record`):
```json
{"table":"incident","table_record_sys_id":"<sys_id>","data":{"state":"6","close_notes":"resolved"}}
```
Group-by roll-up via `servicenow_aggregate` `get_stats` (counts per group):
```json
{"table_name":"incident","query":"active=true","groupby":"priority","stats":true}
```
Raw escape-hatch via `servicenow_custom_api` `api_request` (endpoint is the path after
the instance base, no leading slash):
```json
{"method":"GET","endpoint":"api/now/table/sys_user?sysparm_limit=1"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Prefer `sysparm_fields` + a sane `sysparm_limit`; unbounded reads are slow and large.
- `sysparm_display_value=true` returns human labels but hides raw values — use `all` to
  get both when you need the sys_id/reference behind a label.
- When a table name is uncertain (scoped/plugin tables vary by instance/version),
  **discover first**: `get_table` with `sysparm_limit:1` and inspect the fields before
  assuming a schema. The GRC/security/TRM skills rely on this pattern.
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.
