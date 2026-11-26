---
name: servicenow-incident-management
skill_type: skill
description: >-
  Work ITSM incidents on the ServiceNow Incident API via the servicenow-api
  MCP server: list, read and create incidents with domain-typed tools. Use to
  triage active incidents, fetch one by sys_id, or open a new one. Do NOT use
  for generic table CRUD (servicenow-table-api), changes (servicenow-change-
  management) or CMDB CIs (servicenow-cmdb).
license: MIT
tags: [servicenow, incident, itsm, rest-api, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow Incident Management

Scope: ITSM incident operations on the ServiceNow Incident API via the servicenow-api MCP server — list, read, and create incident records with the domain-typed tool (not raw table calls). Use when the agent must triage active incidents, fetch one incident by sys_id, or open a new incident with fields like short_description, urgency, impact, and caller_id. Do NOT use for generic record CRUD on arbitrary tables (use servicenow-table-api), change requests (servicenow-change-management), CMDB CIs (servicenow-cmdb), or knowledge articles (servicenow-knowledge); prefer those.

Domain-typed access to the ServiceNow **Incident** table (`incident`) for ITSM
triage and intake. Prefer these tools over raw table CRUD — they carry the
incident field conventions and return incident-shaped records.

## When to use
- List / triage active incidents (e.g. ordered by priority).
- Fetch a single incident by `sys_id`.
- Create a new incident (short_description + urgency/impact/caller_id).

## When NOT to use
- Generic CRUD on any other table → `servicenow-table-api`.
- Change requests, CMDB CIs, or knowledge articles → their dedicated skills
  (`servicenow-change-management`, `servicenow-cmdb`, `servicenow-knowledge`).
- Bulk state transitions or fields the typed tool doesn't expose → fall back to
  `servicenow-table-api` against the `incident` table.

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

1. List active incidents with `servicenow_get_incidents` and `sysparm_query` `active=true^ORDERBYpriority`, and verify the rows come back with number and priority.
2. Fetch one incident with `servicenow_get_incident` and its `sys_id`, and verify the `number` matches the one you expected.
3. Look up the caller `sys_id` with `servicenow_get_table` on `sys_user` if only a name is known, and verify one user is returned.
4. Create the incident with `servicenow_create_incident` and `data` holding `short_description`, `urgency`, `impact`, `caller_id`, and verify the response has a new incident number.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Create returns validation error | `urgency` or `impact` is not a valid choice or `caller_id` is not a sys_id | Use choice values 1 to 3 and a real `sys_user` sys_id from `servicenow_get_table` |
| Empty list | `sysparm_query` too narrow or wrong state filter | Drop the filter, set `sysparm_limit` to 5, and re-add conditions one at a time |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

| Area | Typed tools |
|----------------|---------|
| incidents | `servicenow_get_incidents`, `servicenow_get_incident`, `servicenow_create_incident` |
### Key parameters
- `sys_id` — required for `get_incident`.
- `data` — object of field→value for `create_incident` (`short_description`,
  `urgency`, `impact`, `caller_id`, …).
- Query/pagination controls (`sysparm_query`, `sysparm_fields`, `sysparm_limit`,
  `sysparm_offset`, `sysparm_display_value`) follow Table-API encoded-query syntax
  — see `servicenow-table-api` for the cheat-sheet.

## Recipes (tool arguments)
List active incidents ordered by priority (newest first, few fields):
```json
{"sysparm_query":"active=true^ORDERBYpriority^ORDERBYDESCsys_created_on","sysparm_fields":"number,short_description,priority,state,assigned_to","sysparm_limit":25,"sysparm_display_value":"true"}
```
Get one incident by sys_id (with both raw + display values):
```json
{"sys_id":"<sys_id>","sysparm_display_value":"all"}
```
Create an incident:
```json
{"data":{"short_description":"VPN gateway unreachable from HQ","urgency":"1","impact":"2","caller_id":"<user_sys_id>"}}
```

## Gotchas
- Pass arguments as named parameters; nested objects are plain JSON objects.
- `urgency`/`impact` are choice values (typically `1`=High … `3`=Low); the derived
  `priority` is calculated by the platform, not set directly.
- `caller_id` expects a `sys_user` **sys_id** (or a value the instance can resolve);
  look it up via `servicenow-table-api` on `sys_user` if you only have a name.
- Prefer `sysparm_fields` + a sane `sysparm_limit`; unbounded reads are slow.

## Related
- An internal `ingest_incidents_to_kg` misc tool exists for KG plumbing (pull
  incidents into the knowledge graph). It is not part of the operational surface —
  use it only for ingestion, not for the triage/intake recipes above.
- **Composed by:** the universal-skills `servicenow_incident_tracker` workflow
  composes this skill for end-to-end incident tracking.
