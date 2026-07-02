---
name: servicenow-hr-ppm
description: >-
  ServiceNow HR Service Delivery and Project Portfolio Management surface — fetch an
  employee HR profile and insert PPM cost plans and project tasks via the servicenow-api
  MCP server. Use when the agent must read a worker's HR profile or seed project
  financials (cost plans) and project task breakdowns through the dedicated HR/PPM
  endpoints. Do NOT use for generic table CRUD (servicenow-table-api), release/CI-CD
  (servicenow-cicd-devops), data ingest/attachments (servicenow-import-attachment-batch),
  or email/flows/metricbase (servicenow-platform-utilities).
license: MIT
tags: [servicenow, hr, ppm, project, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow HR & PPM

The dedicated endpoints for HR Service Delivery profiles and Project Portfolio
Management financials/work-breakdown. Two condensed tools.

## When to use
- Retrieve an employee's HR profile (`get_hr_profile`).
- Insert PPM cost plans against a project/demand (`insert_cost_plans`).
- Insert project tasks (work breakdown) under a project (`insert_project_tasks`).

## When NOT to use
- Generic reads/writes on `hr_*` or `pm_*` tables the dedicated API doesn't cover →
  `servicenow-table-api` (drive the scoped tables directly).
- App deploy, scans, update sets, ATF → `servicenow-cicd-devops`.
- Bulk row ingest / attachments / batch → `servicenow-import-attachment-batch`.
- Email, flow rendering, metricbase, app metadata → `servicenow-platform-utilities`.

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
Prefer the **condensed** tools; each takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_hr` | `get_hr_profile` |
| `servicenow_ppm` | `insert_cost_plans`, `insert_project_tasks` |

### Key parameters
- HR: `sys_id` (the HR profile / worker `sys_user` reference) — discover it via
  `servicenow-table-api` on `sys_user` / `sn_hr_core_profile` if you only have a name.
- PPM cost plans: `project_sys_id` (or demand), `cost_plans` — an array of plan rows
  (name, cost, fiscal period, unit).
- PPM project tasks: `project_sys_id`, `project_tasks` — an array of task rows
  (short_description, parent, planned start/end, effort).

## Recipes (`params_json`)
Fetch an HR profile (`get_hr_profile`):
```json
{"sys_id":"<hr_profile_or_user_sys_id>"}
```
Insert cost plans on a project (`insert_cost_plans`):
```json
{"project_sys_id":"<project_sys_id>","cost_plans":[{"name":"FY26 licenses","cost":12000,"fiscal_year":"2026"},{"name":"FY26 contractors","cost":48000,"fiscal_year":"2026"}]}
```
Insert project tasks / work breakdown (`insert_project_tasks`):
```json
{"project_sys_id":"<project_sys_id>","project_tasks":[{"short_description":"Discovery","planned_start_date":"2026-07-01","planned_end_date":"2026-07-14"},{"short_description":"Build","planned_start_date":"2026-07-15","planned_end_date":"2026-08-15"}]}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- These endpoints need the corresponding plugins active — **HR Service Delivery** for
  `servicenow_hr`, **Project Portfolio Management (PPM)** for `servicenow_ppm`; a
  missing plugin surfaces as a 404/ACL error, not empty data.
- `get_hr_profile` expects the **HR profile / worker** reference — a plain `sys_user`
  sys_id may not resolve if that user has no HR profile; discover the right id first
  with `servicenow-table-api`.
- Cost plans and project tasks attach to an existing **project sys_id** — create the
  project first (via `servicenow-table-api` on `pm_project`) and pass its sys_id.
- The insert actions take **arrays** (`cost_plans`, `project_tasks`); send even a single
  row as a one-element array.
