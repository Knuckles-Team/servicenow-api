---
name: servicenow-trm
skill_type: skill
description: >-
  Manage the ServiceNow Technology Reference Model and Application Portfolio
  Management (technology portfolio, lifecycle stages, technical debt) table-
  first through the servicenow-api MCP server. Use to inventory technology,
  roll up by lifecycle or set lifecycle state. Do NOT use for generic CRUD
  (servicenow-table-api) or CMDB (servicenow-cmdb).
license: MIT
tags: [servicenow, trm, apm, technology-portfolio, software-lifecycle, technical-debt, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow TRM / APM (technology portfolio)

Scope: ServiceNow Technology Reference Model / Application Portfolio Management (APM) — manage the technology and software portfolio, software-product lifecycle (Approved / Emerging / Retirement / End-of-life), technical debt, and architecture-standard compliance. Use when the agent must inventory the tech/software portfolio, roll up records by lifecycle stage, deep-dive a technology by sys_id, or set a technology's lifecycle/approval state. APM/TRM has no dedicated REST family, so it is driven table-first via servicenow_get_table / servicenow_get_stats / servicenow_api_request against scoped tables that vary by instance and plugin version. Do NOT use for generic table CRUD (use servicenow-table-api), CMDB configuration items (servicenow-cmdb), risk/GRC (servicenow-irm-grc), or security (servicenow-secops); prefer those.

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


## Steps

1. Confirm the table with `servicenow_get_table` and `sysparm_limit` 1, and verify fields match `references/trm-tables.md`.
2. Inventory with `servicenow_get_table` and a `sysparm_query`, and verify the rows are technology or software records.
3. Roll up by stage with `servicenow_get_stats` and `groupby` on the lifecycle field, and verify the group totals match the inventory count.
4. Set a stage with `servicenow_patch_table_record` after reading `servicenow_get_table_record`, and verify the lifecycle value on a re-read.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Table not found | APM plugin absent or names differ | List `sys_db_object` with `servicenow_get_table` for the scoped prefix and use the real table |
| Lifecycle value rejected | Choice value differs from the label | Read `sys_choice` with `servicenow_get_table` and send the stored value |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

| Area | Typed tools |
|----------------|---------|
| table api | `servicenow_get_table`, `servicenow_get_table_record`, `servicenow_add_table_record`, `servicenow_update_table_record`, `servicenow_patch_table_record`, `servicenow_delete_table_record` |
| aggregate | `servicenow_get_stats` |
| custom api | `servicenow_api_request` |
## Discover first (scoped tables vary)
TRM/APM table names differ by instance and plugin version. **Never assume a schema.**
Confirm the table exists and inspect its real fields before building queries:
```json
{"table":"sn_apm_application","sysparm_limit":1,"sysparm_display_value":"all"}
```
Candidate tables/fields and the discover-first recipe: `references/trm-tables.md`.

## Recipes (tool arguments)
Encoded-query, pagination, and `get_stats` mechanics all follow `servicenow-table-api`.

Portfolio inventory (active records, newest first, few fields) via `get_table`:
```json
{"table":"sn_apm_application","sysparm_query":"active=true^ORDERBYDESCsys_created_on","sysparm_fields":"number,name,u_lifecycle_stage,owned_by","sysparm_limit":50,"sysparm_display_value":"true"}
```
Lifecycle roll-up (count per stage) via `servicenow_get_stats` — swap
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
- Pass arguments as named parameters; nested objects are plain JSON objects.
- Scoped `sn_apm_*` tables and lifecycle/approval **field names and choice values
  vary per instance/plugin** — always `get_table` with `sysparm_limit:1` first.
- Lifecycle can live on different records: technology/business-application state on
  `sn_apm_*`, software-product EOL on `cmdb_software_product_model` /
  `samp_sw_product_lifecycle` — pick the table for the question (see reference).
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.

## Related
- **Composed by:** the universal-skills `servicenow_trm_tracker` workflow (at
  `agent-packages/skills/universal-skills/universal_skills/workflows/ops/servicenow_trm_tracker/`)
  composes this skill's `servicenow_get_table`, `servicenow_get_table_record`, `servicenow_add_table_record` calls — it queries the TRM request
  table (typically `u_trm_request` / `dmn_demand`) via `get_table`, deep-dives the
  selected record via `get_table_record`, then persists results to the KG.
- Fall back to `servicenow-table-api` for any TRM/APM table this skill doesn't cover.
