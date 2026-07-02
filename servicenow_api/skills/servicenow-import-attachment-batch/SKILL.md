---
name: servicenow-import-attachment-batch
description: >-
  ServiceNow data-ingest, file, and batched-REST surface — push rows through Import
  Sets (single & bulk), upload/get/delete record attachments, and bundle many REST
  calls into one batch request via the servicenow-api MCP server. Use when the agent
  must load external data through a transform-mapped import set, attach or fetch a file
  on a record, or minimize round-trips by batching multiple operations. Do NOT use for
  direct table CRUD without a transform map (servicenow-table-api), release/CI-CD or
  update-set promotion (servicenow-cicd-devops), or HR/PPM inserts
  (servicenow-hr-ppm).
license: MIT
tags: [servicenow, import-sets, attachments, batch, integration, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Import Sets, Attachments & Batch (integration)

The integration on-ramp: land external data through transform-mapped **import sets**,
manage **attachments** (files) on records, and collapse many REST calls into a single
**batch** request. Three condensed tools.

## When to use
- Bulk-load external rows into a staging import-set table (transform map does the mapping).
- Insert a single import-set row and read back the transform result.
- Upload a file to a record, fetch an attachment, or delete one.
- Reduce latency/round-trips by bundling several REST operations into one call.

## When NOT to use
- Plain table CRUD / aggregate / raw REST (no transform map) → `servicenow-table-api`.
- App deploy, scans, update sets, plugins, ATF → `servicenow-cicd-devops`.
- HR profiles or PPM cost-plan/project-task inserts → `servicenow-hr-ppm`.
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
| `servicenow_import_sets` | `get_import_set`, `insert_import_set`, `insert_multiple_import_sets` |
| `servicenow_attachment` | `get_attachment`, `upload_attachment`, `delete_attachment` |
| `servicenow_batch` | `batch_request` |

### Key parameters
- Import sets: `table` (the import-set/staging table, e.g. `u_imp_users`), `data`
  (single row object) or `records` (array of row objects for the multiple insert),
  `sys_id` (an import-set row/result for `get_import_set`).
- Attachments: `table_name` + `table_sys_id` (the target record), `file_name`,
  `content_type`, `file_path` (or `data`) for upload; `sys_id` for get/delete.
- Batch: `requests` — an array of sub-request objects (`id`, `method`, `url`,
  `headers`, `body`); the response returns each keyed by its `id`.

## Recipes (`params_json`)
Bulk insert rows via an import set (`insert_multiple_import_sets`) — the transform map
on the staging table routes each row to its target table:
```json
{"table":"u_imp_users","records":[{"u_name":"Ada Lovelace","u_email":"ada@example.com"},{"u_name":"Alan Turing","u_email":"alan@example.com"}]}
```
Insert one row and inspect the transform outcome (`insert_import_set`):
```json
{"table":"u_imp_users","data":{"u_name":"Grace Hopper","u_email":"grace@example.com"}}
```
Upload an attachment to a record (`upload_attachment`):
```json
{"table_name":"incident","table_sys_id":"<incident_sys_id>","file_name":"evidence.png","content_type":"image/png","file_path":"/tmp/evidence.png"}
```
Bundle several calls into one round-trip (`batch_request`):
```json
{"requests":[{"id":"r1","method":"GET","url":"/api/now/table/incident?sysparm_limit=1"},{"id":"r2","method":"POST","url":"/api/now/table/incident","headers":[{"name":"Content-Type","value":"application/json"}],"body":"{\"short_description\":\"batched create\"}"}]}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it. In `batch_request`
  each sub-request `body` is itself a **string**, so it is double-encoded.
- Import sets stage into an **import table**, not the target — the row's real fate is
  decided by its **transform map**. Read `get_import_set` for the row's
  `sys_import_state` / `sys_transform_map` result; a "success" import can still map to
  ignore/error at transform time.
- Point attachments at the **target record** (`table_name` + `table_sys_id`), not at a
  staging row; large files may need a chunked/streaming upload rather than inline `data`.
- Batch responses come back **per sub-request** keyed by the `id` you assigned — check
  each sub-status; a 200 on the batch envelope does not mean every sub-request passed.
- Prefer `insert_multiple_import_sets` over looping single inserts for bulk loads — it
  is one call and lets the platform batch the transform.
