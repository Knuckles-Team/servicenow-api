---
name: servicenow-incident-management
description: >-
  ITSM incident operations on the ServiceNow Incident API via the servicenow-api
  MCP server — list, read, and create incident records with the domain-typed
  tool (not raw table calls). Use when the agent must triage active incidents,
  fetch one incident by sys_id, or open a new incident with fields like
  short_description, urgency, impact, and caller_id. Do NOT use for generic
  record CRUD on arbitrary tables (use servicenow-table-api), change requests
  (servicenow-change-management), CMDB CIs (servicenow-cmdb), or knowledge
  articles (servicenow-knowledge); prefer those.
license: MIT
tags: [servicenow, incident, itsm, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Incident Management

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

Full env/tag matrix (do not re-document here): the mcp-client reference
`agent-tools/mcp-client/references/servicenow-api.md`. `MCP_TOOL_MODE`
(`condensed`|`verbose`|`both`) selects the condensed surface (used below) vs. the
one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_incidents` | `get_incidents`, `get_incident`, `create_incident` |

### Key parameters
- `sys_id` — required for `get_incident`.
- `data` — object of field→value for `create_incident` (`short_description`,
  `urgency`, `impact`, `caller_id`, …).
- Query/pagination controls (`sysparm_query`, `sysparm_fields`, `sysparm_limit`,
  `sysparm_offset`, `sysparm_display_value`) follow Table-API encoded-query syntax
  — see `servicenow-table-api` for the cheat-sheet.

## Recipes (`params_json`)
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
- `params_json` is a **string** of JSON, not an object — serialize it.
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
