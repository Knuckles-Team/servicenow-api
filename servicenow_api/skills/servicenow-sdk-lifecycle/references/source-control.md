# Source control & update sets

Fluent projects are ordinary git repos — commit `src/`, `now.config.json`, `package.json`
(gitignore `.now-sdk/` and build output). Two instance-side surfaces move that code
between instances: **source control** (repo ↔ instance) and **update sets** (change
capture/promotion).

## Source control (MCP — `servicenow_source_control`)
Call as `servicenow_source_control(action="...", params_json="{...}")`.

Import a repository into the instance (action `import_repository`):
```json
{"repo_url":"https://<git-host>/org/app.git","branch":"main","credential_sys_id":"<cred>","auto_upgrade_base_app":false}
```

Apply remote source-control changes (pull latest onto the instance; action
`apply_remote_source_control_changes`):
```json
{"app_sys_id":"<app_sys_id>","branch_name":"main","auto_upgrade_base_app":false}
```

## Update sets (MCP — `servicenow_update_sets`)
Call as `servicenow_update_sets(action="...", params_json="{...}")`.

| Action | Purpose |
|--------|---------|
| `update_set_create` | Create a new update set on the instance. |
| `update_set_retrieve` | Retrieve a remote update set into the local instance. |
| `update_set_preview` | Preview a retrieved update set (surface collisions before commit). |
| `update_set_commit` | Commit a previewed update set. |
| `update_set_commit_multiple` | Commit several update sets in order. |
| `update_set_back_out` | Reverse a committed update set. |

Create then commit:
```json
{"name":"MyApp v1.0.1","description":"catalog + business rule"}
```
```json
{"remote_update_set_sys_id":"<sys_id>"}
```

## Choosing between them
- **Fluent-as-code shops** promote via git + `servicenow_source_control` (+ `servicenow_cicd`
  install/publish). This is the preferred path for apps built with this skill.
- **Update sets** remain the classic capture/promote mechanism and are still needed when
  changes originate in the UI or must be previewed for collisions before commit.

## Gotchas
- Always **preview** before `update_set_commit` — preview surfaces collisions/skips.
- `apply_remote_source_control_changes` overwrites instance state with the branch —
  ensure the branch is the intended source of truth.
- Store git credentials as an instance credential and pass its sys_id, never inline
  secrets in `params_json`.
