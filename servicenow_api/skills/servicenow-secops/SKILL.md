---
name: servicenow-secops
description: >-
  ServiceNow Security Operations (SecOps) — Security Incident Response (SIR),
  Vulnerability Response (VR), and Threat Intelligence (TI). Use when the agent must
  triage security incidents by priority, list vulnerable items by risk/state, or
  work threat-intel observables. SecOps areas expose only limited REST, so the
  reliable path is table-first via servicenow_table_api / servicenow_aggregate /
  servicenow_custom_api against scoped sn_si_* (SIR), sn_vul_* (VR), and sn_ti_* (TI)
  tables that vary by instance and plugin version. Do NOT use for regular ITSM
  incidents (use servicenow-incident-management), generic table CRUD
  (servicenow-table-api), risk/GRC (servicenow-irm-grc), or CMDB CIs
  (servicenow-cmdb); prefer those.
license: MIT
tags: [servicenow, secops, security-incident-response, vulnerability-response, threat-intelligence, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow SecOps (SIR / VR / TI)

Table-driven access to the ServiceNow **Security Operations** suite:
**Security Incident Response (SIR)**, **Vulnerability Response (VR)**, and **Threat
Intelligence (TI)**. Some SecOps areas expose limited REST, but the reliable,
consistent path is the generic Table / Aggregate / custom-API tools against the
scoped SecOps tables — exactly the pattern `servicenow-table-api` teaches.

## When to use
- **SIR** — triage open security incidents by priority/state.
- **VR** — list vulnerable items by risk/state, roll up by CVE or assignment group.
- **TI** — query threat-intel observables and indicators.

## When NOT to use
- **Regular ITSM incidents** (`incident` table) → `servicenow-incident-management`.
- Generic CRUD on an arbitrary table → `servicenow-table-api`.
- Risk / policy / compliance / audit → `servicenow-irm-grc`.
- CMDB configuration items → `servicenow-cmdb`.

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
SecOps scoped table names, fields, and state/priority choice values differ by instance
and plugin version. **Never assume a schema.** Confirm the table and inspect real
fields first:
```json
{"table":"sn_si_incident","sysparm_limit":1,"sysparm_display_value":"all"}
```
Encoded-query / pagination / `get_stats` mechanics all come from `servicenow-table-api`.

## Sub-module recipes (`params_json`)

### Security Incident Response (SIR) — candidate tables in `references/sir-tables.md`
Open security incidents by priority (newest first) via `get_table`:
```json
{"table":"sn_si_incident","sysparm_query":"active=true^ORDERBYpriority^ORDERBYDESCsys_created_on","sysparm_fields":"number,short_description,priority,state,assignment_group,risk_score","sysparm_limit":25,"sysparm_display_value":"true"}
```
Roll up security incidents by priority via `servicenow_aggregate` `get_stats`:
```json
{"table_name":"sn_si_incident","query":"active=true","groupby":"priority","stats":true}
```

### Vulnerability Response (VR) — `references/vr-tables.md`
Vulnerable items by risk/state (highest risk first) via `get_table`:
```json
{"table":"sn_vul_vulnerable_item","sysparm_query":"active=true^state!=3^ORDERBYDESCrisk_score","sysparm_fields":"number,vulnerability,cmdb_ci,risk_score,state,assignment_group","sysparm_limit":50,"sysparm_display_value":"true"}
```
Roll up vulnerable items by state via `get_stats`:
```json
{"table_name":"sn_vul_vulnerable_item","query":"active=true","groupby":"state","stats":true}
```

### Threat Intelligence (TI) — `references/ti-tables.md`
List threat-intel observables (most recent first) via `get_table`:
```json
{"table":"sn_ti_observable","sysparm_query":"ORDERBYDESCsys_created_on","sysparm_fields":"value,type,finding,sys_created_on","sysparm_limit":50,"sysparm_display_value":"true"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Scoped `sn_si_*` / `sn_vul_*` / `sn_ti_*` **table names, fields, and state/priority
  choice values vary per instance/plugin** — always `get_table` with `sysparm_limit:1`
  first, and confirm state values via `sys_choice` before filtering on them.
- The `state` values used above (`3`, etc.) are illustrative choice values — discover
  the real ones for your instance (VR item states differ across releases).
- Don't confuse `sn_si_incident` (security incident) with the ITSM `incident` table —
  for the latter use `servicenow-incident-management`.
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.
- Fall back to `servicenow-table-api` for any SecOps table these references don't cover.
