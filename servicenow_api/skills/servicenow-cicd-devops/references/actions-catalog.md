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

| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `check_devops_change_control` | Check whether change control is required/enabled | `tool_id`, `pipeline`, `stage` |
| `register_devops_artifact` | Register a build artifact/package | `tool_id`, `artifacts`, `pipeline_name`, `stage_name`, `branch_name` |
| `check_devops_step_mapping` | Verify a pipeline step is mapped | `tool_id`, `pipeline`, `stage` |
| `get_devops_change_info` | Retrieve change info for a change request | `change_request_sys_id` |
| `get_devops_code_schema` | Fetch the code-change payload schema | (none) |
| `get_devops_onboarding_status` | Onboarding status for a DevOps tool | `tool_id` |
| `get_devops_orchestration_schema` | Orchestration task payload schema | (none) |
| `get_devops_plan_schema` | Planning payload schema | (none) |

## `servicenow_update_sets` — configuration promotion
Chain the returned sys_id through the lifecycle. Always preview before commit.

| Action | Purpose | Common params_json keys |
|--------|---------|-------------------------|
| `update_set_create` | Create a local update set | `name`, `description`, `application` |
| `update_set_retrieve` | Retrieve a remote update set onto this instance | `update_set_sys_id`, `instance_id` |
| `update_set_preview` | Preview a retrieved update set (collisions) | `update_set_sys_id` |
| `update_set_commit` | Commit a previewed update set | `update_set_sys_id` |
| `update_set_commit_multiple` | Commit a batch/hierarchy of update sets | `update_set_sys_ids` |
| `update_set_back_out` | Back out a committed update set | `update_set_sys_id` |

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
