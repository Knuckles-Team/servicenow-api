---
name: servicenow-irm-grc
description: >-
  ServiceNow Integrated Risk Management / GRC — the ServiceNow equivalent of RSA
  Archer (GRC) and OneTrust (privacy). Covers Risk Management, Policy & Compliance,
  Audit Management, Vendor / Third-Party Risk (TPRM), and Privacy Management. Use
  when the agent must list open risks, roll up compliance by control state, list
  open audit findings, work the vendor-risk assessment queue, or handle privacy
  data-subject / processing-activity records. IRM/GRC has no dedicated REST family,
  so it is driven table-first via servicenow_table_api / servicenow_aggregate /
  servicenow_custom_api against scoped sn_risk_* / sn_compliance_* / sn_audit_* /
  sn_vdr_* tables that vary by instance and plugin version. Do NOT use for generic
  table CRUD (use servicenow-table-api), security incidents/vulnerabilities
  (servicenow-secops), or the technology portfolio (servicenow-trm); prefer those.
license: MIT
tags: [servicenow, irm, grc, risk, compliance, audit, tprm, privacy, archer, onetrust, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow IRM / GRC (risk, compliance, audit, TPRM, privacy)

Table-driven access to the ServiceNow **Integrated Risk Management (IRM/GRC)** suite
— the ServiceNow equivalent of **RSA Archer** (GRC) and **OneTrust** (privacy). These
modules are scoped apps with **no dedicated REST API**, so you drive them through the
generic Table / Aggregate / custom-API tools against their scoped tables — exactly the
pattern `servicenow-table-api` teaches.

## When to use
- **Risk Management** — list open risks, risk-register roll-ups, risk assessments.
- **Policy & Compliance** — policies, controls, citations, compliance by control state.
- **Audit Management** — audit engagements and open findings.
- **Vendor / Third-Party Risk (TPRM)** — vendor risk-assessment queue and tiers.
- **Privacy Management** — data-subject requests, processing activities, privacy assessments.

## When NOT to use
- Generic CRUD on an arbitrary table → `servicenow-table-api`.
- Security incidents / vulnerabilities / threat intel → `servicenow-secops`.
- Technology / software portfolio & lifecycle → `servicenow-trm`.
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
IRM/GRC scoped table names and fields differ by instance and plugin version.
**Never assume a schema.** Confirm the table and inspect real fields first:
```json
{"table":"sn_risk_risk","sysparm_limit":1,"sysparm_display_value":"all"}
```
Encoded-query / pagination / `get_stats` mechanics all come from `servicenow-table-api`.

## Sub-module recipes (`params_json`)

### Risk Management — candidate tables in `references/risk-tables.md`
List open risks by score (newest first) via `get_table`:
```json
{"table":"sn_risk_risk","sysparm_query":"active=true^state!=closed^ORDERBYDESCrisk_score","sysparm_fields":"number,short_description,state,risk_score,owned_by","sysparm_limit":50,"sysparm_display_value":"true"}
```
Risk-register roll-up by state via `servicenow_aggregate` `get_stats`:
```json
{"table_name":"sn_risk_risk","query":"active=true","groupby":"state","stats":true}
```

### Policy & Compliance — `references/compliance-audit-tables.md`
Roll up compliance by control **state** via `get_stats`:
```json
{"table_name":"sn_compliance_control","query":"","groupby":"state","stats":true}
```
List controls that are non-compliant / attention-needed via `get_table`:
```json
{"table":"sn_compliance_control","sysparm_query":"state=attest_needed^ORstate=non_compliant^ORDERBYDESCsys_updated_on","sysparm_fields":"number,name,state,owned_by","sysparm_limit":50,"sysparm_display_value":"true"}
```

### Audit Management — `references/compliance-audit-tables.md`
List open audit findings via `get_table`:
```json
{"table":"sn_audit_finding","sysparm_query":"active=true^state!=closed^ORDERBYDESCsys_created_on","sysparm_fields":"number,short_description,state,engagement,assigned_to","sysparm_limit":50,"sysparm_display_value":"true"}
```

### Vendor / Third-Party Risk (TPRM) — `references/vendor-tprm-tables.md`
Vendor-risk assessment queue (open assessments) via `get_table`:
```json
{"table":"sn_vdr_risk_assessment","sysparm_query":"state=in_progress^ORstate=draft^ORDERBYDESCsys_created_on","sysparm_fields":"number,vendor,state,tier,assigned_to","sysparm_limit":50,"sysparm_display_value":"true"}
```

### Privacy Management — `references/privacy-tables.md`
List open privacy data-subject requests via `get_table` (confirm the real table name
during discovery — privacy tables vary widely):
```json
{"table":"sn_privacy_dsar","sysparm_query":"active=true^state!=closed^ORDERBYdue_date","sysparm_fields":"number,short_description,state,due_date,assigned_to","sysparm_limit":50,"sysparm_display_value":"true"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Scoped `sn_risk_*` / `sn_compliance_*` / `sn_audit_*` / `sn_vdr_*` **table names,
  fields, and state choice values vary per instance/plugin** — always `get_table`
  with `sysparm_limit:1` before querying, and confirm state values via `sys_choice`.
- `state` values in the examples (`closed`, `attest_needed`, `non_compliant`,
  `in_progress`) are illustrative — discover the real choices for your instance.
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.
- Fall back to `servicenow-table-api` for any IRM table these references don't cover.
