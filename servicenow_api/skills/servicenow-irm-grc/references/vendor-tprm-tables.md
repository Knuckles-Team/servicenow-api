# IRM/GRC — Vendor / Third-Party Risk (TPRM) candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** Scoped `sn_vdr_*` / `sn_tprm_*` tables, fields, and
> state values **vary by instance and plugin version** (Vendor Risk Management vs. the
> newer Third-Party Risk Management app use different prefixes). Probe before trusting:
> ```json
> {"table":"sn_vdr_risk_assessment","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `nameSTARTSWITHsn_vdr_^ORnameSTARTSWITHsn_tprm_` (fields `name,label,sys_scope`).
2. Probe each with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm assessment `state` and `tier` choices via `sys_choice`.

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_vdr_vendor` / `sn_tprm_vendor` | Vendor / third-party master record |
| `sn_vdr_risk_assessment` | Vendor risk assessment (the queue object) |
| `sn_vdr_assessment` | Assessment instance / questionnaire response |
| `sn_vdr_engagement` / `sn_tprm_engagement` | Third-party engagement / relationship |
| `sn_vdr_finding` / `sn_vdr_issue` | Vendor-risk finding / issue |
| `sn_vdr_tiering` | Vendor tiering (criticality) record |
| `sn_vdr_contract` | Vendor contract reference |

## Candidate fields (confirm per instance)
- Identity: `number`, `short_description`, `vendor` (→ vendor table).
- State/lifecycle: `state` (e.g. `draft` / `in_progress` / `review` / `closed`), `active`.
- Risk: `tier`, `risk_rating`, `inherent_risk`, `residual_risk`, `criticality`.
- Ownership: `assigned_to`, `owned_by`, `relationship_owner`, `managed_by_group`.
- Dates: `due_date`, `sys_created_on`, `next_assessment_date`.

## Common encoded queries (syntax → servicenow-table-api)
- Open assessment queue: `state=in_progress^ORstate=draft^ORDERBYDESCsys_created_on`
- Assessments for a vendor: `vendor=<sys_id>`
- High-tier / critical vendors: `tier=high^ORtier=critical`
- Overdue reassessments: `next_assessment_date<javascript:gs.beginningOfToday()`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Assessments by state: `groupby` = `state`.
- Vendors by tier: `groupby` = `tier`.
- Findings by risk rating: `groupby` = `risk_rating`.
