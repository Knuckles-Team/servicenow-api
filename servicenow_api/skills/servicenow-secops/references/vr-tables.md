# SecOps — Vulnerability Response (VR) candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_vul_*` tables, fields, and state choice
> values **vary by instance and plugin version** (item states in particular changed
> across releases). Probe before trusting:
> ```json
> {"table":"sn_vul_vulnerable_item","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `sysparm_query":"nameSTARTSWITHsn_vul_"` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm `state` choices via `sys_choice`
   (`name=sn_vul_vulnerable_item^element=state`).

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_vul_vulnerable_item` | Vulnerable item — a vulnerability on a specific CI (the core VR object) |
| `sn_vul_entry` | Vulnerability entry (the vulnerability definition, e.g. from NVD) |
| `sn_vul_third_party_entry` | Third-party scanner vulnerability entry |
| `sn_vul_nvd_entry` | NVD CVE entry |
| `sn_vul_detection` | Detection record linking scanner findings to items |
| `sn_vul_remediation_task` | Remediation task |
| `sn_vul_vul_group` | Vulnerability group (bulk remediation grouping) |
| `sn_vul_cmdb_ci` | Vulnerable-item ↔ CI mapping |

## Candidate fields (confirm per instance)
- Identity: `number`, `vulnerability` (→ `sn_vul_entry`), `short_description`.
- Risk: `risk_score`, `risk_rating`, `severity`, `cvss_base_score`.
- State/lifecycle: `state`, `active`, `substate`, `closed_at`.
- Targets: `cmdb_ci`, `ip_address`, `dns`.
- Assignment: `assignment_group`, `assigned_to`.
- Dates: `sys_created_on`, `first_found`, `last_found`, `due_date`.

## Common encoded queries (syntax → servicenow-table-api)
- Open items by risk: `active=true^state!=3^ORDERBYDESCrisk_score` (confirm closed state value)
- Items for a CVE: `vulnerability.id=CVE-YYYY-NNNNN` (or filter `vulnerability=<sys_id>`)
- Overdue remediations: `due_date<javascript:gs.beginningOfToday()^active=true`
- High severity: `severity=high^active=true`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Items by state: `groupby` = `state`.
- Items by risk rating: `groupby` = `risk_rating`.
- Items by assignment group: `groupby` = `assignment_group`.
- Items by vulnerability (top CVEs): `groupby` = `vulnerability`.
