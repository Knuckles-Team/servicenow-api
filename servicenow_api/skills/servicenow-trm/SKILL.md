---
name: servicenow-trm
description: >-
  ServiceNow Technology Reference Model / Application Portfolio Management (APM) —
  manage the technology & software portfolio, software-product lifecycle (Approved /
  Emerging / Retirement / End-of-life), technical debt, and architecture-standard
  compliance. Use when the agent must inventory the tech/software portfolio, roll up
  records by lifecycle stage, deep-dive a technology by sys_id, or set a technology's
  lifecycle/approval state. APM/TRM has no dedicated REST family, so it is driven
  table-first via servicenow_table_api / servicenow_aggregate / servicenow_custom_api
  against scoped tables that vary by instance and plugin version. Do NOT use for
  generic table CRUD (use servicenow-table-api), CMDB configuration items
  (servicenow-cmdb), risk/GRC (servicenow-irm-grc), or security
  (servicenow-secops); prefer those.
license: MIT
tags: [servicenow, trm, apm, technology-portfolio, software-lifecycle, technical-debt, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow TRM / APM (technology portfolio)

Table-driven access to the ServiceNow **Technology Reference Model** and
**Application Portfolio Management (APM)** modules. These modules ship as scoped
apps with **no dedicated REST API**, so you drive them through the generic Table /
Aggregate / custom-API tools against their scoped tables — exactly the pattern
`servicenow-table-api` teaches.

## When to use
- Inventory the technology / software portfolio (business apps, software products).
- Roll up records by **lifecycle stage** (Approved / Emerging / Retirement / EOL).
- Deep-dive one technology or software product by `sys_id`.
- Set a technology's lifecycle / approval / architecture-compliance state.
- Track technical debt and architecture-standard exceptions.

## When NOT to use
- Generic CRUD on an arbitrary table → `servicenow-table-api`.
- Configuration items / CI relationships → `servicenow-cmdb`.
- Risk / policy / compliance / audit → `servicenow-irm-grc`.
- Security incidents / vulnerabilities → `servicenow-secops`.

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
whose keys are passed straight to the client method (see `servicenow-table-api`).

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_table_api` | `get_table`, `get_table_record`, `add_table_record`, `update_table_record`, `patch_table_record`, `delete_table_record` |
| `servicenow_aggregate` | `get_stats` |
| `servicenow_custom_api` | `api_request` |

## Discover first (scoped tables vary)
TRM/APM table names differ by instance and plugin version. **Never assume a schema.**
Confirm the table exists and inspect its real fields before building queries:
```json
{"table":"sn_apm_application","sysparm_limit":1,"sysparm_display_value":"all"}
```
Candidate tables/fields and the discover-first recipe: `references/trm-tables.md`.

## Recipes (`params_json`)
Encoded-query, pagination, and `get_stats` mechanics all follow `servicenow-table-api`.

Portfolio inventory (active records, newest first, few fields) via `get_table`:
```json
{"table":"sn_apm_application","sysparm_query":"active=true^ORDERBYDESCsys_created_on","sysparm_fields":"number,name,u_lifecycle_stage,owned_by","sysparm_limit":50,"sysparm_display_value":"true"}
```
Lifecycle roll-up (count per stage) via `servicenow_aggregate` `get_stats` — swap
`groupby` to the real lifecycle-stage field you found during discovery:
```json
{"table_name":"cmdb_software_product_model","query":"","groupby":"life_cycle_stage","stats":true}
```
Record deep-dive by sys_id (raw + display values) via `get_table_record`:
```json
{"table":"sn_apm_application","table_record_sys_id":"<sys_id>","sysparm_display_value":"all"}
```
Set a technology's lifecycle / approval state via `patch_table_record` (use the
choice values your instance defines — confirm them during discovery):
```json
{"table":"cmdb_software_product_model","table_record_sys_id":"<sys_id>","data":{"life_cycle_stage":"end_of_life","end_of_life":"2027-12-31"}}
```
Software EOL / end-of-support scan via `get_table` on `cmdb_software_product_model`:
```json
{"table":"cmdb_software_product_model","sysparm_query":"end_of_lifeISNOTEMPTY^end_of_life<=javascript:gs.beginningOfNextYear()^ORDERBYend_of_life","sysparm_fields":"name,manufacturer,end_of_life,end_of_support","sysparm_limit":100,"sysparm_display_value":"true"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Scoped `sn_apm_*` tables and lifecycle/approval **field names and choice values
  vary per instance/plugin** — always `get_table` with `sysparm_limit:1` first.
- Lifecycle can live on different records: technology/business-application state on
  `sn_apm_*`, software-product EOL on `cmdb_software_product_model` /
  `samp_sw_product_lifecycle` — pick the table for the question (see reference).
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.

## Related
- **Composed by:** the universal-skills `servicenow_trm_tracker` workflow (at
  `agent-packages/skills/universal-skills/universal_skills/workflows/ops/servicenow_trm_tracker/`)
  composes this skill's `servicenow_table_api` calls — it queries the TRM request
  table (typically `u_trm_request` / `dmn_demand`) via `get_table`, deep-dives the
  selected record via `get_table_record`, then persists results to the KG.
- Fall back to `servicenow-table-api` for any TRM/APM table this skill doesn't cover.
