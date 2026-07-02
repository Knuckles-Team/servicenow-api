---
name: servicenow-telecom-tmf
description: >-
  ServiceNow Telecom (TSM/TSOM) TM Forum Open APIs — drives service qualification
  (TMF645), product inventory (TMF637), account (TMF666/629), and any other TM Forum
  Open API (TMF622 product ordering, TMF641 service ordering, TMF642 alarm
  management) exposed by Store-installed scoped telecom apps. Use when the agent must
  run a service qualification, list product inventory, fetch an account, or call a
  raw TMF endpoint. It uses the domain-typed tools servicenow_service_qualification /
  servicenow_product_inventory / servicenow_account, and servicenow_custom_api
  api_request for other TMF endpoints whose scoped-app path depends on which TMF
  plugins are installed (discover-first). Do NOT use for generic table CRUD (use
  servicenow-table-api), CMDB CIs (servicenow-cmdb), or ITSM incidents
  (servicenow-incident-management); prefer those.
license: MIT
tags: [servicenow, telecom, tmforum, tmf, service-qualification, product-inventory, csm, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Telecom / TM Forum Open APIs

ServiceNow's telecom offering (**Telecommunications Service Management / Operations
Management — TSM/TSOM**) surfaces the **TM Forum (TMF) Open APIs** as Store-installed
scoped applications. This skill drives those APIs through the domain-typed tools where
they exist, and through the raw `servicenow_custom_api` escape-hatch for the rest —
just as `servicenow-table-api` teaches for modules without a first-class typed tool.

## When to use
- Run a **service qualification** (TMF645) — check whether a service can be delivered.
- List / delete **product inventory** (TMF637).
- Fetch an **account** (TMF666/629 party/account management).
- Call any **raw TMF endpoint** (TMF622 product ordering, TMF641 service ordering,
  TMF642 alarm management, …) via `api_request`.

## When NOT to use
- Generic CRUD on an arbitrary table → `servicenow-table-api`.
- CMDB configuration items → `servicenow-cmdb`.
- ITSM incidents → `servicenow-incident-management`.

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
Prefer the **domain-typed** tools; each takes `action` + a `params_json` **JSON
string** whose keys are passed straight to the client method (see `servicenow-table-api`).

| Condensed tool | Actions | TMF |
|----------------|---------|-----|
| `servicenow_service_qualification` | `check_service_qualification`, `get_service_qualification`, `process_service_qualification_result` | TMF645 |
| `servicenow_product_inventory` | `get_product_inventory`, `delete_product_inventory` | TMF637 |
| `servicenow_account` | `get_account` | TMF666/629 |
| `servicenow_custom_api` | `api_request` | any other TMF API |

## Discover first (scoped-app paths vary)
The exact scoped-app REST path/table for a given TMF API depends on **which TMF
plugins are installed** and their scope prefix (e.g. `sn_ind_tmt_*`, `sn_ind_tsm_*`).
**Never assume a path.** Confirm what's installed before calling raw endpoints:
```json
{"method":"GET","endpoint":"api/now/table/sys_db_object?sysparm_query=nameSTARTSWITHsn_ind_&sysparm_fields=name,label,sys_scope&sysparm_limit=100"}
```
TMF-API → purpose → typical scoped-app endpoint/table map: `references/tmf-apis.md`.

## Recipes (`params_json`)

Run a **service qualification** (TMF645) via `check_service_qualification` — the body
shape follows the TMF645 `CheckServiceQualification` resource (confirm required fields
for your app version):
```json
{"data":{"provideAlternative":true,"serviceQualificationItem":[{"service":{"serviceSpecification":{"id":"<spec_id>"},"place":[{"@type":"GeographicAddress","id":"<address_id>"}]}}]}}
```
Fetch a qualification result by id via `get_service_qualification`:
```json
{"id":"<service_qualification_id>"}
```
Process a returned qualification result via `process_service_qualification_result`:
```json
{"id":"<service_qualification_id>"}
```
List **product inventory** (TMF637) via `get_product_inventory` (query params follow
TMF filtering; keep results bounded):
```json
{"params":{"limit":25,"status":"active"}}
```
Delete a product-inventory record via `delete_product_inventory`:
```json
{"id":"<product_id>"}
```
Fetch an **account** (TMF666/629) via `get_account`:
```json
{"id":"<account_id>"}
```
Call a **raw TMF endpoint** via `servicenow_custom_api` `api_request` — endpoint is the
path after the instance base (no leading slash); the `sn_ind_tmt_*` scope prefix is a
**candidate** you must confirm during discovery:
```json
{"method":"GET","endpoint":"api/sn_ind_tmt_orchestration/tmf-api/productOrderingManagement/v4/productOrder?limit=10"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Scoped-app **endpoint paths, versions (`v4`/`v5`), and scope prefixes vary per
  installed TMF plugin** — always discover installed `sn_ind_*` scopes first; treat
  the paths in `references/tmf-apis.md` as candidates, not guarantees.
- TMF request/response bodies follow the **TM Forum resource models** (polymorphic
  `@type`, nested `serviceQualificationItem`, `relatedParty`, …) — validate the exact
  required fields against your app's API version.
- Not every TMF API has a domain-typed tool — for those (ordering, alarms,
  qualification variants), use `servicenow_custom_api` `api_request`.
- For anything backed by a plain table with no TMF endpoint, fall back to
  `servicenow-table-api`.
