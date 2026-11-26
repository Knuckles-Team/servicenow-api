---
name: servicenow-irm-grc
skill_type: skill
description: >-
  Work ServiceNow Integrated Risk Management and GRC (risk, compliance, audit,
  vendor risk, privacy) table-first through the servicenow-api MCP server. Use
  to list open risks, roll up control states, list audit findings or work
  vendor and privacy records. Do NOT use for generic table CRUD (servicenow-
  table-api) or security incidents (servicenow-secops).
license: MIT
tags: [servicenow, irm, grc, risk, compliance, audit, tprm, privacy, archer, onetrust, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow IRM / GRC (risk, compliance, audit, TPRM, privacy)

Scope: ServiceNow Integrated Risk Management / GRC — the ServiceNow equivalent of RSA Archer (GRC) and OneTrust (privacy). Covers Risk Management, Policy and Compliance, Audit Management, Vendor / Third-Party Risk (TPRM), and Privacy Management. Use when the agent must list open risks, roll up compliance by control state, list open audit findings, work the vendor-risk assessment queue, or handle privacy data-subject / processing-activity records. IRM/GRC has no dedicated REST family, so it is driven table-first via servicenow_get_table / servicenow_get_stats / servicenow_api_request against scoped sn_risk_ / sn_compliance_ / sn_audit_ / sn_vdr_ tables that vary by instance and plugin version. Do NOT use for generic table CRUD (use servicenow-table-api), security incidents/vulnerabilities (servicenow-secops), or the technology portfolio (servicenow-trm); prefer those.

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


## Steps

1. Confirm the scoped table exists with `servicenow_get_table` and `sysparm_limit` 1 on the candidate table, and verify the fields returned match the reference tables in `references/`.
2. Query the working set with `servicenow_get_table` and a `sysparm_query`, and verify the rows returned belong to the requested domain.
3. Roll up counts with `servicenow_get_stats` using `groupby`, and verify the totals equal the sum of the groups.
4. Update a record with `servicenow_patch_table_record` only after reading it with `servicenow_get_table_record`, and verify the changed field on a re-read.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Table not found | Plugin not installed or table name differs by version | Inspect `sys_db_object` with `servicenow_get_table` for names starting `sn_risk_` or `sn_compliance_` and use the real name |
| Stats call returns nothing | Query or `groupby` field invalid on this table | Run `servicenow_get_table` with `sysparm_limit` 1 to see real field names and retry with one of them |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

| Area | Typed tools |
|----------------|---------|
| table api | `servicenow_get_table`, `servicenow_get_table_record`, `servicenow_add_table_record`, `servicenow_update_table_record`, `servicenow_patch_table_record`, `servicenow_delete_table_record` |
| aggregate | `servicenow_get_stats` |
| custom api | `servicenow_api_request` |
## Discover first (scoped tables vary)
IRM/GRC scoped table names and fields differ by instance and plugin version.
**Never assume a schema.** Confirm the table and inspect real fields first:
```json
{"table":"sn_risk_risk","sysparm_limit":1,"sysparm_display_value":"all"}
```
Encoded-query / pagination / `get_stats` mechanics all come from `servicenow-table-api`.

## Recipes (tool arguments)

### Risk Management — candidate tables in `references/risk-tables.md`
List open risks by score (newest first) via `get_table`:
```json
{"table":"sn_risk_risk","sysparm_query":"active=true^state!=closed^ORDERBYDESCrisk_score","sysparm_fields":"number,short_description,state,risk_score,owned_by","sysparm_limit":50,"sysparm_display_value":"true"}
```
Risk-register roll-up by state via `servicenow_get_stats`:
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
- Pass arguments as named parameters; nested objects are plain JSON objects.
- Scoped `sn_risk_*` / `sn_compliance_*` / `sn_audit_*` / `sn_vdr_*` **table names,
  fields, and state choice values vary per instance/plugin** — always `get_table`
  with `sysparm_limit:1` before querying, and confirm state values via `sys_choice`.
- `state` values in the examples (`closed`, `attest_needed`, `non_compliant`,
  `in_progress`) are illustrative — discover the real choices for your instance.
- `get_stats` maps `groupby`→`sysparm_group_by` and `stats:true`→`sysparm_count=true`.
- Fall back to `servicenow-table-api` for any IRM table these references don't cover.
