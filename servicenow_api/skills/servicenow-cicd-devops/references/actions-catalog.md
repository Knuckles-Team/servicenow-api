# CI/CD & DevOps — full action catalog

Reference for the six condensed release-engineering tools. Each row is an `action`
plus the common `params_json` keys it accepts. Keys are passed straight through to the
client method; discover unknown ids first with `servicenow-table-api` (e.g. app sys_id
from `sys_app`, suite sys_id from `sys_atf_test_suite`).

> All calls: `servicenow_<tool>(action="<action>", params_json="{...}")`.

## `servicenow_cicd` — application & code CI/CD
Asynchronous. Install/scan actions return a progress/tracker id; poll `progress`
(generic) or `instance_scan_progress` (scans) until complete.

| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `batch_install` | Install a batch descriptor (multiple packages) | `packages`, `name`, `notes` |
| `batch_install_result` | Fetch result of a batch install | `result_id` |
| `batch_rollback` | Roll back a completed batch install | `rollback_id` |
| `app_repo_install` | Install an app from the app repository | `sys_id`, `scope`, `version`, `auto_upgrade_base_app` |
| `app_repo_publish` | Publish an app version to the repo | `sys_id`, `scope`, `version`, `dev_notes` |
| `app_repo_rollback` | Roll back a published/installed app | `sys_id`, `scope`, `version` |
| `full_scan` | Full instance code scan | (none; instance-wide) |
| `point_scan` | Scan a single target | `target_table`, `target_sys_id` |
| `combo_suite_scan` | Run a named combo of suites | `combo_sys_id` |
| `suite_scan` | Run a specific scan suite | `suite_sys_id`, `app_scope_sys_ids` |
| `instance_scan_progress` | Poll a scan's progress | `progress_id` |
| `progress` | Poll a generic CI/CD progress tracker | `progress_id` |

## `servicenow_devops` — DevOps change & schema
Read-oriented gating and metadata; `register_devops_artifact` is the mutating one.
**Gotcha**: unlike every other tool on this page, these eight actions bypass
`CICDModel` entirely and read **camelCase** keys straight off `kwargs` (they call
`sn_devops/...` endpoints directly) — do not use the snake_case keys from the
`servicenow_cicd`/`servicenow_update_sets` tables above/below.

| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `check_devops_change_control` | Check whether change control is required/enabled | `toolId` (req), `toolType` (default `"jenkins"`), `orchestrationTaskName`, `orchestrationTaskURL`, `testConnection` |
| `register_devops_artifact` | Register a build artifact/package | `artifacts` (req, list), `orchestrationToolId`, `toolId`, `branchName`, `pipelineName`, `projectName`, `stageName`, `taskExecutionNumber` |
| `check_devops_step_mapping` | Verify a pipeline step is mapped | `toolId`, `orchestrationTaskName`, `orchestrationTaskURL` (all req), `toolType`, `branchName`, `isMultiBranch`, `parentStageName`, `parentStageURL`, `testConnection` |
| `get_devops_change_info` | Retrieve change info for an orchestration pipeline execution | `toolId`, `buildNumber` (both req), `stageName`, `pipelineName`, `projectName`, `branchName` |
| `get_devops_code_schema` | Fetch the code-change payload schema | `resource` (req) |
| `get_devops_onboarding_status` | Onboarding status for a DevOps tool | `id` (req) |
| `get_devops_orchestration_schema` | Orchestration task payload schema | `resource` (req) |
| `get_devops_plan_schema` | Planning payload schema | `resource` (req) |

## `servicenow_update_sets` — configuration promotion
Chain the returned sys_id through the lifecycle — note the id's key name changes at
each hop (`update_set_id` → `remote_update_set_id`). Always preview before commit.

| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `update_set_create` | Create a local update set | `update_set_name` (req), one of `sys_id`/`scope` (req), `description` |
| `update_set_retrieve` | Retrieve a remote update set onto this instance | `update_set_id` (req), `update_source_id`, `update_source_instance_id`, `auto_preview`, `cleanup_retrieved` |
| `update_set_preview` | Preview a retrieved update set (collisions) | `remote_update_set_id` (req) |
| `update_set_commit` | Commit a previewed update set | `remote_update_set_id` (req), `force_commit` |
| `update_set_commit_multiple` | Commit a batch/hierarchy of update sets | `remote_update_set_ids` (req, list), `force_commit` |
| `update_set_back_out` | Back out a committed update set | `update_set_id` (req), `rollback_installs` |

There is no `update_set_sys_id`/`update_set_sys_ids`/`name`/`instance_id`/`application`
key anywhere in `CICDModel` — passing those (instead of the keys above) is silently
dropped (not rejected), so the call fails with a confusing `MissingParameterError`
that gives no hint the key name was simply wrong.

## `servicenow_source_control` — repo integration
| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `apply_remote_source_control_changes` | Pull remote branch changes into the app | `app_sys_id`, `branch_name`, `auto_upgrade_base_app` |
| `import_repository` | Import a repository as a new scoped app | `repo_url`, `branch_name`, `credential_sys_id`, `auto_upgrade_base_app` |

## `servicenow_plugins` — plugin lifecycle
| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `activate_plugin` | Activate a plugin by id | `plugin_id` |
| `rollback_plugin` | Roll back a plugin activation | `plugin_id` |

## `servicenow_testing` — Automated Test Framework
| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `run_test_suite` | Run an ATF test suite | `test_suite_sys_id`, `os_name`, `browser_name`, `browser_version` |
