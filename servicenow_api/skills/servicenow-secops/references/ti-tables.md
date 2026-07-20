# SecOps — Threat Intelligence (TI) candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_ti_*` tables, fields, and choice values
> **vary by instance and plugin version**. Probe before trusting:
> ```json
> {"table":"sn_ti_observable","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `sysparm_query":"nameSTARTSWITHsn_ti_"` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm observable `type` and finding choices via `sys_choice`.

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_ti_observable` | Observable / IoC (IP, domain, hash, URL, email …) |
| `sn_ti_observable_type` | Observable type definition |
| `sn_ti_task` | Threat-intelligence task |
| `sn_ti_indicator` | Threat indicator |
| `sn_ti_stix_object` | STIX object (imported threat data) |
| `sn_ti_report` | Threat-intel report |
| `sn_ti_feed` / `sn_ti_source` | TI feed / source configuration |
| `sn_ti_m2m_task_observable` | Task ↔ observable relationship |

## Candidate fields (confirm per instance)
- Observable: `value`, `type` (→ `sn_ti_observable_type`), `finding`, `reputation`.
- Enrichment: `enrichment_status`, `confidence`, `score`.
- Linkage: `security_incident` (→ `sn_si_incident`), `task`, `source`, `feed`.
- Dates: `sys_created_on`, `last_seen`, `first_seen`.

## Common encoded queries (syntax → servicenow-table-api)
- Recent observables: `ORDERBYDESCsys_created_on`
- Malicious findings: `finding=malicious` (confirm choice value)
- Observables of a type: `type=<sys_id>` (e.g. IP address / domain / hash)
- Observables tied to an incident: `security_incident=<sys_id>`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Observables by type: `groupby` = `type`.
- Observables by finding/reputation: `groupby` = `finding`.
- Observables by source/feed: `groupby` = `source`.
