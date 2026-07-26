# Tool map — every action this skill cites, with its verified location

All calls: `servicenow_<tool>(action="<action>", params_json="{...}")` /
`gitlab_<tool>(action="<action>", params_json="{...}")` — `params_json` is a JSON
**string**, not an object.

## ServiceNow side (`servicenow-api` MCP server)

| Tool | Action | Registered at | Client method |
|---|---|---|---|
| `servicenow_source_control` | `import_repository` | `servicenow_api/mcp_server.py:357` (`register_source_control_tools`) | `Api.import_repository` — `servicenow_api/api/api_client_devops.py:545` |
| `servicenow_source_control` | `apply_remote_source_control_changes` | `servicenow_api/mcp_server.py:357` | `Api.apply_remote_source_control_changes` — `servicenow_api/api/api_client_other.py:759` |
| `servicenow_cicd` | `app_repo_publish` / `app_repo_install` / `app_repo_rollback` / `progress` | `servicenow_api/mcp_server.py:242` (`register_cicd_tools`) | see `servicenow-app-engine` → `references/packaging-and-publish.md` and `servicenow-cicd-devops` → `references/actions-catalog.md` for the full parameter contract |
| `servicenow_table_api` | `get_table` / `add_table_record` | `servicenow_api/mcp_server.py:1017` (`register_table_api_tools`) | `Api.get_table` / `Api.add_table_record` — used here to create/verify the `sys_scope`/`sys_app` records the app lives in |
| `servicenow_testing` | `run_test_suite` | `servicenow_api/mcp_server.py:401` (`register_testing_tools`) | ATF gate before/after promotion — see `servicenow-cicd-devops` |

## GitLab side (`gitlab-api` MCP server)

| Tool | Action | Registered at | Client method |
|---|---|---|---|
| `gitlab_projects` | `create` | `gitlab_api/mcp_server.py:952` (`register_projects_tools`) | `client.create_project` — stand up the repo the app's source lives in |
| `gitlab_commits` | `create` | `gitlab_api/mcp_server.py:274` (`register_commits_tools`) | `client.create_commit` — push a multi-file commit (source tree + `.gitlab-ci.yml`) without a local git checkout |
| `gitlab_branches` | `get` | `gitlab_api/mcp_server.py:178` (`register_branches_tools`) | `client.get_branch`/`get_branches` — confirm the push landed and (if applicable) is protected |
| `gitlab_pipelines` | `get` | `gitlab_api/mcp_server.py:837` (`register_pipelines_tools`) | `client.get_pipeline`/`get_pipelines` — check `status` and `yaml_errors` |
| `gitlab_runners` | `get_all` | `gitlab_api/mcp_server.py:1103` (`register_runners_tools`) | `client.get_all_runners` — confirm an online runner is assigned before expecting a job to execute |
| `api_request` | (raw) | `gitlab_api/mcp_server.py:1532` (`register_custom_api_tools`) | `client.api_request` — escape hatch for anything not covered above (e.g. `GET /projects/{id}/repository/tree`) |

## Cross-references (not owned by this skill)

- Scoped-app metadata anatomy, `now.config.json`, Fluent artifacts →
  `servicenow-app-engine`.
- `now-sdk` CLI lifecycle (init/auth/build/transform/deploy/ATF) →
  `servicenow-sdk-lifecycle` → `references/build-transform.md`,
  `references/deploy-and-install.md`, `references/source-control.md`.
- Full CI/CD & DevOps action catalog (every `servicenow_cicd`/`servicenow_devops`/
  `servicenow_update_sets`/`servicenow_plugins` parameter) →
  `servicenow-cicd-devops` → `references/actions-catalog.md`.
- GitLab-side pipeline authoring/troubleshooting not tied to a ServiceNow
  target → gitlab-api's own `gitlab-pipelines` skill.
