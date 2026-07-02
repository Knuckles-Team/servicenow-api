# IRM/GRC — Risk Management candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_risk_*` tables, fields, and state choice
> values **vary by instance and plugin version**. Probe before trusting:
> ```json
> {"table":"sn_risk_risk","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find risk tables: `get_table` on `sys_db_object` with
   `sysparm_query":"nameSTARTSWITHsn_risk_"` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`; read the keys.
3. Confirm `state` (and any score/impact/likelihood) choices via `sys_choice`
   (`name=<table>^element=state`).

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_risk_risk` | Risk register entry (the core risk record) |
| `sn_risk_definition` | Risk statement / definition template |
| `sn_risk_assessment` | Risk assessment instance |
| `sn_risk_assessment_instance` | Individual assessment run/response |
| `sn_risk_risk_criteria` | Scoring criteria (impact × likelihood matrix) |
| `sn_risk_advanced_risk` | Advanced Risk Assessment record (newer IRM) |
| `sn_risk_issue` | Risk issue / remediation issue |
| `sn_grc_item` | Base GRC profile/scopable item many records link to |
| `sn_grc_profile` | Profile (entity in scope for risk/compliance) |

## Candidate fields (confirm per instance)
- Identity: `number`, `short_description`, `name`.
- State/lifecycle: `state`, `active`, `phase`.
- Scoring: `risk_score`, `calculated_risk_score`, `inherent_risk`, `residual_risk`,
  `impact`, `likelihood`, `significance`.
- Ownership: `owned_by`, `assigned_to`, `managed_by_group`, `profile` (→ `sn_grc_profile`).
- Dates: `sys_created_on`, `sys_updated_on`, `review_date`, `due_date`.

## Common encoded queries (syntax → servicenow-table-api)
- Open risks by score: `active=true^state!=closed^ORDERBYDESCrisk_score`
- High residual risk: `residual_risk>=high` (confirm choice value)
- Overdue reviews: `review_date<javascript:gs.beginningOfToday()`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Register by state: `groupby` = `state`.
- Register by owner group: `groupby` = `managed_by_group`.
- By profile/entity: `groupby` = `profile`.
