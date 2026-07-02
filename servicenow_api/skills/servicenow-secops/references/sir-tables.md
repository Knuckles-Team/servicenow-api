# SecOps — Security Incident Response (SIR) candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_si_*` tables, fields, and state/priority
> choice values **vary by instance and plugin version**. Probe before trusting:
> ```json
> {"table":"sn_si_incident","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `sysparm_query":"nameSTARTSWITHsn_si_"` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm `state` / `priority` choices via `sys_choice` (`name=sn_si_incident^element=state`).

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_si_incident` | Security incident (the core SIR record) |
| `sn_si_task` | Security incident response task |
| `sn_si_m2m_incident_ci` | Security incident ↔ affected CI relationship |
| `sn_si_incident_response_task` | Response / playbook task |
| `sn_si_playbook` | Response playbook definition |
| `sn_si_affected_user` | Affected user on a security incident |
| `sn_si_alert` | Security alert (source of an incident) |

## Candidate fields (confirm per instance)
- Identity: `number`, `short_description`, `description`.
- Triage: `priority`, `state`, `severity`, `risk_score`, `category`, `subcategory`.
- Assignment: `assignment_group`, `assigned_to`, `opened_by`.
- Linkage: `cmdb_ci`, `affected_user`, `business_criticality`.
- Dates: `sys_created_on`, `sys_updated_on`, `opened_at`, `resolved_at`.

## Common encoded queries (syntax → servicenow-table-api)
- Open by priority: `active=true^ORDERBYpriority^ORDERBYDESCsys_created_on`
- Critical open: `priority=1^active=true`
- Assigned to a group: `assignment_group=<sys_id>^active=true`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- By priority: `groupby` = `priority`.
- By state: `groupby` = `state`.
- By assignment group: `groupby` = `assignment_group`.
