# IRM/GRC — Policy & Compliance + Audit candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_compliance_*` / `sn_audit_*` tables,
> fields, and state values **vary by instance and plugin version**. Probe before
> trusting:
> ```json
> {"table":"sn_compliance_control","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `nameSTARTSWITHsn_compliance_^ORnameSTARTSWITHsn_audit_` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm control/finding `state` choices via `sys_choice`.

## Policy & Compliance — candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_compliance_policy` | Policy record |
| `sn_compliance_policy_statement` | Individual policy statement / requirement |
| `sn_compliance_control` | Control (the object rolled up by state) |
| `sn_compliance_control_objective` | Control objective grouping controls |
| `sn_compliance_control_test` / `sn_compliance_test` | Control test / test result |
| `sn_compliance_citation` | Citation from an authority document |
| `sn_compliance_authority_document` | Authority document / framework (e.g. ISO, NIST) |
| `sn_compliance_issue` | Compliance issue / remediation |

### Candidate fields
- Identity: `number`, `name`, `short_description`.
- State: `state` (e.g. `compliant` / `non_compliant` / `attest_needed` / `not_assessed`).
- Linkage: `policy`, `control_objective`, `authority_document`, `citation`, `profile`.
- Ownership: `owned_by`, `assigned_to`, `content_owner`.

### Roll-ups
- Compliance by control state: `get_stats` `groupby` = `state` on `sn_compliance_control`.
- Controls per authority document: `groupby` = `authority_document`.

## Audit Management — candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_audit_engagement` | Audit engagement (the audit itself) |
| `sn_audit_finding` | Audit finding (the object rolled up when "open findings") |
| `sn_audit_task` | Audit task / fieldwork step |
| `sn_audit_observation` | Observation captured during the audit |
| `sn_audit_workpaper` | Workpaper / evidence record |
| `sn_audit_universe` | Auditable-entity universe |

### Candidate fields
- Identity: `number`, `short_description`, `title`.
- State/lifecycle: `state`, `active`, `phase`, `rating`, `severity`.
- Linkage: `engagement` (→ `sn_audit_engagement`), `assigned_to`, `owned_by`.
- Dates: `due_date`, `sys_created_on`, `planned_start`, `planned_end`.

### Common queries (syntax → servicenow-table-api)
- Open findings: `active=true^state!=closed^ORDERBYDESCsys_created_on`
- Findings for an engagement: `engagement=<sys_id>`
- High-severity open: `severity=high^state!=closed`

### Roll-ups
- Findings by state: `get_stats` `groupby` = `state` on `sn_audit_finding`.
- Findings by severity: `groupby` = `severity`.
