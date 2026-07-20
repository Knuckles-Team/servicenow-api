# IRM/GRC — Privacy Management candidate tables & fields (discover-first)

> **CANDIDATE / typical names.** ServiceNow Privacy Management (the OneTrust-equivalent
> module) is a scoped app whose tables, fields, and state values **vary widely by
> instance and plugin version** — privacy table naming is less standardized than the
> risk/compliance/audit families, so discovery is especially important here. Probe
> before trusting any name:
> ```json
> {"table":"sn_privacy_dsar","sysparm_limit":1,"sysparm_display_value":"all"}
> ```
> All query/aggregate mechanics come from the `servicenow-table-api` skill.

## Discover-first recipe
1. Find tables: `get_table` on `sys_db_object` with
   `nameSTARTSWITHsn_privacy_^ORlabelLIKEprivacy` (fields `name,label,sys_scope`).
   If nothing matches, the plugin may use a different prefix — widen the search.
2. Probe each candidate with `sysparm_limit:1` + `sysparm_display_value:all`.
3. Confirm request `state` and request-type choices via `sys_choice`.

## Candidate tables

| Candidate table | Typical purpose |
|-----------------|-----------------|
| `sn_privacy_dsar` | Data-subject access request (DSAR) |
| `sn_privacy_request` | Generic privacy / data-subject request |
| `sn_privacy_processing_activity` | Processing activity / RoPA record |
| `sn_privacy_assessment` | Privacy assessment (PIA / DPIA) |
| `sn_privacy_data_map` / `sn_privacy_data_inventory` | Data mapping / personal-data inventory |
| `sn_privacy_data_category` | Personal-data category |
| `sn_privacy_consent` | Consent record |
| `sn_privacy_breach` | Privacy breach / incident record |

## Candidate fields (confirm per instance)
- Identity: `number`, `short_description`, `data_subject`, `requester`.
- Request type: `request_type` (e.g. access / erasure / rectification / portability).
- State/lifecycle: `state`, `active`, `stage`.
- SLA: `due_date`, `sys_created_on`, `received_date`, `completion_date`.
- Linkage: `processing_activity`, `data_category`, `assigned_to`, `owned_by`.

## Common encoded queries (syntax → servicenow-table-api)
- Open DSARs by due date: `active=true^state!=closed^ORDERBYdue_date`
- Erasure requests: `request_type=erasure`
- Overdue requests: `due_date<javascript:gs.beginningOfToday()^state!=closed`

## Aggregate roll-ups (servicenow_aggregate `get_stats`)
- Requests by state: `groupby` = `state`.
- Requests by type: `groupby` = `request_type`.
- Processing activities by data category: `groupby` = `data_category`.
