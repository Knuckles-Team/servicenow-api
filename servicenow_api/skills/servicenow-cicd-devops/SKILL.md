---
name: servicenow-cicd-devops
skill_type: skill
description: >-
  Run the ServiceNow release-engineering surface via the servicenow-api MCP
  server: CI/CD app install and rollback, scans, DevOps change control, update
  sets, source-control apply, plugins and ATF suites. Use to deploy, roll back
  or test a scoped app. Do NOT use for generic table CRUD (servicenow-table-
  api) or data import (servicenow-import-attachment-batch).
license: MIT
tags: [servicenow, cicd, devops, update-sets, atf, source-control, rest-api, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow CI/CD & DevOps (release engineering)

Scope: ServiceNow release-engineering surface — CI/CD app install/scan/rollback, DevOps change-control and artifact registration, update-set create/preview/commit/back-out, source-control apply/import, plugin activate/rollback, and ATF test-suite runs via the servicenow-api MCP server. Use when the agent must deploy or roll back a scoped app, publish/install from an app repo, run a code/instance scan, move changes with update sets, pull remote source-control changes, activate a plugin, or execute an Automated Test Framework suite. This is where the dev-tooling skill servicenow-sdk-lifecycle defers for remote deploy/publish/test. Do NOT use for generic record CRUD (servicenow-table-api), data ingest/attachments/batch (servicenow-import-attachment-batch), or flow rendering and email (servicenow-platform-utilities).

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


## Steps

1. Look up the exact parameter keys in `references/actions-catalog.md`, and verify the action you need is listed.
2. Create a change container with `servicenow_update_set_create` or select the app repo, and verify the returned id is non-empty.
3. Preview with `servicenow_update_set_preview` before any commit, and verify the preview reports no problems.
4. Deploy with `servicenow_app_repo_install` or `servicenow_app_repo_publish`, and verify via the `progress` action that the tracker reaches a successful state.
5. Run `servicenow_run_test_suite` after the deploy, and verify the suite result shows no failed tests.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Install fails mid-way | Dependency, plugin or version conflict on the target | Call `servicenow_app_repo_rollback` with the app id, fix the cause from the progress message, and redeploy |
| Preview shows problems | Collisions or missing dependencies in the update set | Resolve each reported problem and run `servicenow_update_set_preview` again before commit |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

| Sub-area | Area | Typed tools |
|----------|----------------|---------|
| App/code CI/CD | `servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback` | `batch_install`, `batch_install_result`, `batch_rollback`, `app_repo_install`, `app_repo_publish`, `app_repo_rollback`, `full_scan`, `point_scan`, `combo_suite_scan`, `suite_scan`, `instance_scan_progress`, `progress` |
| DevOps change | `servicenow_devops` | `check_devops_change_control`, `register_devops_artifact`, `check_devops_step_mapping`, `get_devops_change_info`, `get_devops_code_schema`, `get_devops_onboarding_status`, `get_devops_orchestration_schema`, `get_devops_plan_schema` |
| Update sets | `servicenow_update_set_create`, `servicenow_update_set_retrieve`, `servicenow_update_set_preview` | `update_set_create`, `update_set_retrieve`, `update_set_preview`, `update_set_commit`, `update_set_commit_multiple`, `update_set_back_out` |
| Source control | `servicenow_apply_remote_source_control_changes`, `servicenow_import_repository` | `apply_remote_source_control_changes`, `import_repository` |
| Plugins | `servicenow_activate_plugin`, `servicenow_rollback_plugin` | `activate_plugin`, `rollback_plugin` |
| Testing | `servicenow_run_test_suite` | `run_test_suite` |

Exact `params_json` keys per action: **`references/actions-catalog.md`**.

## Recipes (tool arguments)
Install an app from its repo, then poll progress until done (`app_repo_install`
returns a `progress_id` / rollback link; feed it back to `progress`):
```json
{"sys_id":"<app_sys_id>","scope":"x_myco_app","auto_upgrade_base_app":true}
```
```json
{"progress_id":"<progress_id_from_install>"}
```
Create → retrieve on the target → preview → commit an update set (the id's key name
changes at each hop — `update_set_create` returns a local sys_id, `update_set_retrieve`
returns a *different* `remote_update_set_id` for the retrieved copy):
```json
{"update_set_name":"promote-x_myco_app v1.4.0","scope":"x_myco_app","description":"Release 1.4.0"}
```
(`update_set_create`, on the source instance) →
```json
{"update_set_id":"<sys_id_from_create>","update_source_instance_id":"<source_instance_id>"}
```
(`update_set_retrieve`, on the target instance) →
```json
{"remote_update_set_id":"<remote_update_set_id_from_retrieve>"}
```
(`update_set_preview` — always preview before commit) →
```json
{"remote_update_set_id":"<remote_update_set_id_from_retrieve>"}
```
(`update_set_commit`)
Run an ATF suite by sys_id (`run_test_suite`):
```json
{"test_suite_sys_id":"<suite_sys_id>","os_name":"linux","browser_name":"chrome"}
```

## Gotchas
- Pass arguments as named parameters; nested objects are plain JSON objects.
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
  update-set actions use `update_set_id`/`remote_update_set_id`/`progress_id`
  depending on the step (there is no `update_set_sys_id` key), and every
  `servicenow_devops` action uses **camelCase** keys (`toolId`, `orchestrationTaskName`,
  …), not the snake_case keys the rest of this tool group uses — a wrong key name is
  silently dropped rather than rejected, so the failure is a confusing
  `MissingParameterError`, not a clear "unknown parameter".
