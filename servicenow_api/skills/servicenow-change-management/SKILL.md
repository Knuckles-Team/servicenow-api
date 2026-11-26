---
name: servicenow-change-management
skill_type: skill
description: >-
  Run ServiceNow change-request lifecycle operations via the servicenow-api
  MCP server: query, create, update, risk-calculate, conflict-check, approve
  and delete changes and tasks. Use to open a normal or standard change and
  drive it through CAB. Do NOT use for incidents (servicenow-incident-
  management) or CMDB data (servicenow-cmdb).
license: MIT
tags: [servicenow, change-management, itsm, cab, rest-api, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow Change Management

Scope: ITSM change-management operations on the ServiceNow Change API via the servicenow-api MCP server — the full change-request lifecycle: query changes, tasks, schedules, CIs, models and standard-change templates; create/update changes and change-tasks; run risk calculation and conflict checks; approve; and delete. Use when the agent must open a normal/standard change, drive it through CAB (conflict check → approve), or inspect change schedules and impacted services. Do NOT use for incidents (servicenow-incident-management), CMDB CI data (servicenow-cmdb), or generic table CRUD (servicenow-table-api); prefer those.

Domain-typed access to the ServiceNow **Change** API — the whole change-request
lifecycle (normal / standard / emergency) plus tasks, schedules, CI associations,
models, standard-change templates, risk calculation, conflict detection, and
approval.

## When to use
- Query change requests, their tasks, schedules, associated CIs, or conflicts.
- Create a normal change, or spin one from a standard-change template.
- Update a change / change-task; move to the next state.
- Run CAB flow: calculate risk → conflict check → approve.

## When NOT to use
- Incidents → `servicenow-incident-management`.
- CMDB CI records / relationships / lifecycle → `servicenow-cmdb` (this skill only
  *associates* existing CIs to a change).
- Generic CRUD on arbitrary tables → `servicenow-table-api`.

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

1. Read the allowed states and types in `references/change-states.md`, and verify the values you will send exist for the target instance.
2. Create the change with `servicenow_create_change_request` and a `data` object, and verify the response carries a `sys_id` and number.
3. Run `servicenow_check_change_request_conflict` for that `sys_id`, and verify the conflict result is empty or reviewed before approval.
4. Calculate risk with `servicenow_calculate_standard_change_request_risk` where a standard template is used, and verify the returned risk matches the expected level.
5. Approve with `servicenow_approve_change_request`, and verify via `servicenow_get_change_request` that the state advanced.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Create returns validation error | Required field or state value not valid on this instance | Look up valid choices in `references/change-states.md` and resend `data` with the allowed values |
| Conflict check reports overlaps | Another change targets the same CI in the window | Move the window with `servicenow_update_change_request_first_available` or resolve the other change, then re-check |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

**Query / read**
`get_change_requests`, `get_change_request`, `get_change_request_nextstate`,
`get_change_request_schedule`, `get_change_request_tasks`, `get_change_request_ci`,
`get_change_request_conflict`, `get_change_request_models`,
`get_change_request_worker`, `get_standard_change_request_templates`,
`get_standard_change_request_template`, `get_standard_change_request_model`

**Create**
`create_change_request`, `create_change_request_task`,
`create_change_request_ci_association`

**Update**
`update_change_request`, `update_change_request_task`,
`update_change_request_first_available`

**Risk & conflict**
`calculate_standard_change_request_risk`, `check_change_request_conflict`,
`refresh_change_request_impacted_services`

**Approve**
`approve_change_request`

**Delete**
`delete_change_request`, `delete_change_request_task`,
`delete_change_request_conflict_scan`

### Key parameters
- `sys_id` — the change-request (or task) sys_id for get/update/approve/delete.
- `data` — object of field→value for create/update (`short_description`, `type`,
  `risk`, `impact`, `assignment_group`, `start_date`, `end_date`, `cmdb_ci`, …).
- `state` / next-state values, `type` (normal|standard|emergency), and
  `risk` codes vary by instance — see `references/change-states.md` before
  hard-coding values.

## Recipes (tool arguments)
List active change requests (newest first, few fields):
```json
{"sysparm_query":"active=true^ORDERBYDESCsys_created_on","sysparm_fields":"number,short_description,type,state,risk,start_date","sysparm_limit":25,"sysparm_display_value":"true"}
```
Create a normal change:
```json
{"data":{"type":"normal","short_description":"Patch prod DB cluster to 15.6","risk":"3","impact":"2","assignment_group":"<group_sys_id>","start_date":"2026-07-05 02:00:00","end_date":"2026-07-05 04:00:00"}}
```
CAB flow — conflict check, then approve (two calls):
```json
{"sys_id":"<change_sys_id>"}
```
```json
{"sys_id":"<change_sys_id>","state":"approved"}
```
(First call → `check_change_request_conflict`; second call → `approve_change_request`. Review the returned conflicts before approving.)

## Gotchas
- Pass arguments as named parameters; nested objects are plain JSON objects.
- Field codes (`state`, `type`, `risk`, `impact`) are instance-configurable — read
  `references/change-states.md` and confirm against the target instance; don't
  assume numeric mappings.
- Standard changes are created from a **template/model**, not free-form — list
  templates (`get_standard_change_request_templates`) and use the template's model
  to create, then `calculate_standard_change_request_risk`.
- Run `check_change_request_conflict` (and review `get_change_request_conflict`)
  **before** `approve_change_request`; approving through unresolved conflicts is a
  CAB anti-pattern.
- `refresh_change_request_impacted_services` recomputes impact from CI
  associations — call it after adding CIs, before reporting impact.

## Related
- **Composed by:** the universal-skills `servicenow_change_tracker` workflow
  composes this skill for end-to-end change tracking.
- CI records and relationships behind `cmdb_ci` associations → `servicenow-cmdb`.
