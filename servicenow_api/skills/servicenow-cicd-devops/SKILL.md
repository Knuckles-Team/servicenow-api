---
name: servicenow-cicd-devops
description: >-
  ServiceNow release-engineering surface — CI/CD app install/scan/rollback, DevOps
  change-control & artifact registration, update-set create/preview/commit/back-out,
  source-control apply/import, plugin activate/rollback, and ATF test-suite runs via
  the servicenow-api MCP server. Use when the agent must deploy or roll back a scoped
  app, publish/install from an app repo, run a code/instance scan, move changes with
  update sets, pull remote source-control changes, activate a plugin, or execute an
  Automated Test Framework suite. This is where the dev-tooling skill
  servicenow-sdk-lifecycle defers for remote deploy/publish/test. Do NOT use for
  generic record CRUD (servicenow-table-api), data ingest/attachments/batch
  (servicenow-import-attachment-batch), or flow rendering & email
  (servicenow-platform-utilities).
license: MIT
tags: [servicenow, cicd, devops, update-sets, atf, source-control, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow CI/CD & DevOps (release engineering)

The operational release surface: promote code between instances, scan it, gate it
through DevOps change control, and prove it with ATF. Six condensed tools cover the
whole pipeline. The full per-action catalog lives in
`references/actions-catalog.md` — read it just-in-time when you need the exact
parameter names for an action.

## When to use
- Install / publish / roll back a scoped app from a source-control app repo.
- Kick off and poll code or instance scans (full / point / combo / suite).
- Gate a deployment through DevOps change control and register artifacts/packages.
- Move configuration between instances with update sets (create → preview → commit).
- Apply remote source-control changes or import a repository.
- Activate or roll back a plugin.
- Run an Automated Test Framework (ATF) test suite.

## When NOT to use
- Generic table CRUD / aggregate / raw REST → `servicenow-table-api`.
- Bulk data ingest, attachments, or bundled REST → `servicenow-import-attachment-batch`.
- Flow-to-mermaid, email, metricbase, app metadata → `servicenow-platform-utilities`.
- Authoring an app locally (SDK scaffolding) → the dev-tooling skill
  `servicenow-sdk-lifecycle`; it **defers here** for the remote deploy/publish/test steps.

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
whose keys are passed straight to the client method. Grouped by sub-area:

| Sub-area | Condensed tool | Actions |
|----------|----------------|---------|
| App/code CI/CD | `servicenow_cicd` | `batch_install`, `batch_install_result`, `batch_rollback`, `app_repo_install`, `app_repo_publish`, `app_repo_rollback`, `full_scan`, `point_scan`, `combo_suite_scan`, `suite_scan`, `instance_scan_progress`, `progress` |
| DevOps change | `servicenow_devops` | `check_devops_change_control`, `register_devops_artifact`, `check_devops_step_mapping`, `get_devops_change_info`, `get_devops_code_schema`, `get_devops_onboarding_status`, `get_devops_orchestration_schema`, `get_devops_plan_schema` |
| Update sets | `servicenow_update_sets` | `update_set_create`, `update_set_retrieve`, `update_set_preview`, `update_set_commit`, `update_set_commit_multiple`, `update_set_back_out` |
| Source control | `servicenow_source_control` | `apply_remote_source_control_changes`, `import_repository` |
| Plugins | `servicenow_plugins` | `activate_plugin`, `rollback_plugin` |
| Testing | `servicenow_testing` | `run_test_suite` |

Exact `params_json` keys per action: **`references/actions-catalog.md`**.

## Recipes (`params_json`)
Install an app from its repo, then poll progress until done (`app_repo_install`
returns a `progress_id` / rollback link; feed it back to `progress`):
```json
{"sys_id":"<app_sys_id>","scope":"x_myco_app","auto_upgrade_base_app":true}
```
```json
{"progress_id":"<progress_id_from_install>"}
```
Create → preview → commit an update set (each step chains the returned sys_id):
```json
{"name":"promote-x_myco_app","description":"Release 1.4.0"}
```
```json
{"update_set_sys_id":"<sys_id_from_create>"}
```
```json
{"update_set_sys_id":"<sys_id_from_create>"}
```
Run an ATF suite by sys_id (`run_test_suite`):
```json
{"test_suite_sys_id":"<suite_sys_id>","os_name":"linux","browser_name":"chrome"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- CI/CD and scan calls are **asynchronous**: the install/scan actions return a
  progress/tracker id — poll `progress` (CI/CD generic) or `instance_scan_progress`
  (scans) until the status is complete before treating the result as final.
- Never `update_set_commit` without a `update_set_preview` first — preview surfaces
  collisions/errors that a blind commit would carry into the target instance.
- `batch_install` (batch descriptor) and `batch_install_result` are paired: capture
  the result-token from the install call and pass it to `batch_install_result`.
- ATF suites require the Automated Test Framework to be enabled and a runner
  available on the instance; a missing runner leaves the run pending, not failed.
- Verify exact key names in `references/actions-catalog.md` before a mutating call —
  DevOps/update-set actions differ subtly (`sys_id` vs `update_set_sys_id` vs
  `progress_id`).
