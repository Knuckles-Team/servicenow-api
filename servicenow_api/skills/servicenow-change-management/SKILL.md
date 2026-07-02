---
name: servicenow-change-management
description: >-
  ITSM change-management operations on the ServiceNow Change API via the
  servicenow-api MCP server — the full change-request lifecycle: query changes,
  tasks, schedules, CIs, models and standard-change templates; create/update
  changes and change-tasks; run risk calculation and conflict checks; approve;
  and delete. Use when the agent must open a normal/standard change, drive it
  through CAB (conflict check → approve), or inspect change schedules and impacted
  services. Do NOT use for incidents (servicenow-incident-management), CMDB CI
  data (servicenow-cmdb), or generic table CRUD (servicenow-table-api); prefer
  those.
license: MIT
tags: [servicenow, change-management, itsm, cab, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Change Management

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

Full env/tag matrix (do not re-document here): the mcp-client reference
`agent-tools/mcp-client/references/servicenow-api.md`. `MCP_TOOL_MODE`
(`condensed`|`verbose`|`both`) selects the condensed surface (used below) vs. the
one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool `servicenow_change_management`; it takes `action` +
a `params_json` **JSON string** whose keys are passed straight to the client
method. Actions grouped by lifecycle stage:

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

## Recipes (`params_json`)
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
(First `params_json` → `check_change_request_conflict`; second →
`approve_change_request`. Review the returned conflicts before approving.)

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
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
