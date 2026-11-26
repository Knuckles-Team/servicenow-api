---
name: servicenow-studio-gitlab-app
skill_type: skill
description: >-
  Wire a ServiceNow scoped app to a GitLab repository and promote it via Path
  A (native Studio source control) or Path B (GitLab CI with now-sdk). Use to
  connect app source to GitLab, choose a path, or debug the pipeline file. Do
  NOT use for app anatomy (servicenow-app-engine) or the CI/CD action catalog
  (servicenow-cicd-devops).
license: MIT
tags: [servicenow, gitlab, source-control, ci-cd, now-sdk, app-engine, devops, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow Studio + GitLab (two integration paths)

Scope: Wire a ServiceNow scoped app (App Engine Studio / Fluent) to a GitLab repository and drive its promotion two ways — Path A: native Studio source control (`servicenow_apply_remote_source_control_changes`, `servicenow_import_repository`, then `servicenow_app_repo_install` / `servicenow_app_repo_publish`), or Path B: GitLab-CI-driven (`now-sdk build`/`install` in a pipeline job, then publish/verify through the same `sn_cicd`/Table-API endpoints). Use when the agent must connect an app's source to GitLab, pick between the two integration paths, or debug the `.gitlab-ci.yml` of a scoped-app pipeline. Do NOT use for the app's own metadata anatomy (use servicenow-app-engine), the now-sdk CLI lifecycle itself (use servicenow-sdk-lifecycle), Flow Designer authoring (use servicenow-workflow-studio), the CI/CD and DevOps action catalog once a pipeline is already promoting (use servicenow-cicd-devops), or GitLab-side pipeline mechanics unrelated to ServiceNow (use gitlab-api's own `gitlab-pipelines` skill).

Connects a scoped app's source to a GitLab repository and promotes it, via **two
independent paths** that can be used separately or together:

- **Path A — native Studio source control.** ServiceNow itself pulls from (or
  imports) the GitLab repo over `servicenow_apply_remote_source_control_changes`, `servicenow_import_repository`, then promotes with
  `servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback` (`servicenow-cicd-devops` owns that action catalog).
  Requires the instance's **outbound** reach to the GitLab host.
- **Path B — GitLab-CI-driven.** A GitLab pipeline runs `now-sdk build`/`install`
  (outbound from the GitLab runner to the instance), then the same publish/verify
  calls confirm the result. Requires a GitLab **runner** with outbound reach to
  the instance instead.

Pick the path (or both) based on which side can reach the other — see
`references/tool-map.md` for the full tool-name→file:line citations behind every
claim in this skill.

## When to use
- Deciding whether Path A or Path B fits a given network topology.
- Wiring a scoped app's GitLab repo into ServiceNow (`import_repository`) or
  pulling remote branch changes into an existing app
  (`apply_remote_source_control_changes`).
- Authoring or debugging the `.gitlab-ci.yml` that builds/deploys/promotes/verifies
  a scoped app through GitLab CI (Path B).
- Diagnosing why a Path-A or Path-B promotion didn't reach the instance (perimeter,
  credential, or runner gaps).

## When NOT to use
- The app's metadata shape (tables, ACLs, menus, `now.config.json`) →
  `servicenow-app-engine`.
- The `now-sdk` CLI lifecycle itself (init/auth/build/deploy/ATF, run locally or
  in a pipeline step) → `servicenow-sdk-lifecycle`.
- Flow Designer flows/subflows/actions → `servicenow-workflow-studio`.
- The full CI/CD & DevOps action catalog (`servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback`/`servicenow_devops`/
  `servicenow_update_set_create`, `servicenow_update_set_retrieve`, `servicenow_update_set_preview`/`servicenow_activate_plugin`, `servicenow_rollback_plugin`/`servicenow_run_test_suite` parameter
  reference) once a pipeline already exists → `servicenow-cicd-devops`.
- GitLab-side pipeline authoring/debugging unrelated to a ServiceNow target →
  gitlab-api's own `gitlab-pipelines` skill.

## Prerequisites & environment
Two MCP servers, both via the `mcp-client` skill:

| Server | Env | Notes |
|--------|-----|-------|
| `servicenow-api` | `SERVICENOW_INSTANCE` (alias `SERVICENOW_URL`), `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD` (or `SERVICENOW_CLIENT_ID`/`SERVICENOW_CLIENT_SECRET`), `SERVICENOW_SSL_VERIFY` | Full env/tag matrix: `agent-tools/mcp-client/references/servicenow-api.md` |
| `gitlab-api` | `GITLAB_URL`, `GITLAB_TOKEN` | A personal/project access token with `api` scope for the target project |

A scoped app project (`now.config.json`, `src/fluent/`) — see `servicenow-app-engine`
if it doesn't exist yet.

## Steps

1. Choose the path with the table in Choosing a path, and verify which side can reach the other using `servicenow_get_table` on `sys_app` for Path A or `gitlab_runners` for Path B.
2. For Path A run `servicenow_import_repository` with `repo_url`, `branch_name` and `credential_sys_id`, and verify the scoped app exists in `servicenow_get_table` on `sys_app`.
3. Pull later changes with `servicenow_apply_remote_source_control_changes` using `app_sys_id`, `scope` and `branch_name`, and verify the call reports success.
4. For Path B copy `assets/gitlab-ci-template.yml` to `.gitlab-ci.yml` and set the pipeline variables, and verify the pipeline created has `yaml_errors` null.
5. Promote with `servicenow_app_repo_publish` and `servicenow_app_repo_install`, and verify the `progress` action ends in success.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Import fails to reach the repository | Instance cannot reach the GitLab host | Use Path B, or ask the owner to approve a perimeter change as described in `references/path-a-native-source-control.md` |
| Pipeline jobs stay pending | No online runner assigned | Check runners with `gitlab_runners` action `get_all` and assign an online runner |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Reference map — open just-in-time
- **`references/tool-map.md`** — every tool/action this skill cites, with the
  `mcp_server.py`/client file:line it was verified against on both sides
  (`servicenow-api` and `gitlab-api`). Read to confirm a tool name before calling it.
- **`references/path-a-native-source-control.md`** — the native-Studio path: the
  `import_repository`/`apply_remote_source_control_changes` → `servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback`
  hand-off, and the hard inbound-reachability requirement when GitLab sits behind
  an access proxy (e.g. Cloudflare Access) — what that needs and why it's an
  **owner-approval-required** decision, never one this skill makes for you.
- **`references/path-b-gitlab-ci.md`** — the GitLab-CI path: pipeline stages,
  required CI/CD variables, and how to read pipeline/job status back to confirm a
  promotion actually ran (vs. sitting `pending`/`created` for lack of a runner).

## Choosing a path
| Situation | Path |
|---|---|
| ServiceNow instance can reach the GitLab host outbound (or is granted an access exception) | **A** — simpler, no external CI runner needed |
| GitLab (or its runner) can reach the ServiceNow instance outbound, but the instance can't reach GitLab | **B** — build/deploy runs from the GitLab side |
| Neither side can reach the other | Neither path works until the owner approves a perimeter change — see `references/path-a-native-source-control.md` §"What the owner must approve"; do not weaken or bypass the perimeter yourself |

## Path A — quick recipe
```json
{"repo_url":"https://gitlab.example/group/app-repo.git","branch_name":"main","credential_sys_id":"<credential_sys_id>"}
```
(`servicenow_apply_remote_source_control_changes`, `servicenow_import_repository` action `import_repository`, creates the scoped app from
the repo) → once the app exists, pull further branch changes:
```json
{"app_sys_id":"<app_sys_id>","scope":"x_myco_app","branch_name":"main"}
```
(action `apply_remote_source_control_changes`) → promote with `servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback`
(`app_repo_publish`/`app_repo_install`) — full parameter reference:
`servicenow-cicd-devops` → `references/actions-catalog.md`.

## Path B — quick recipe
1. Bundle `.gitlab-ci.yml` at the repo root — start from
   `assets/gitlab-ci-template.yml` (build → deploy → promote → verify stages).
2. Set the pipeline's CI/CD variables (`SN_INSTANCE_URL`, `SN_USERNAME`,
   `SN_PASSWORD`, app scope) — full list in `references/path-b-gitlab-ci.md`.
3. Push; confirm the pipeline was created and is syntactically valid
   (`gitlab_pipelines` action `get`, check `yaml_errors` is `null`).
4. Confirm a runner actually picks it up (`gitlab_runners` action `get_all` —
   an `online: false`/ungrouped runner leaves every job `pending`/`created`
   forever, which looks like a hang but is a runner-assignment gap, not a
   pipeline or ServiceNow defect).
5. Once a job completes, verify the ServiceNow side directly:
   `servicenow_get_table`, `servicenow_get_table_record`, `servicenow_add_table_record` action `get_table` on `sys_app`/`sys_scope`, or
   `servicenow_app_repo_install`, `servicenow_app_repo_publish`, `servicenow_app_repo_rollback` action `progress` on the returned tracker id.

## Gotchas
- **Path A requires inbound reach to GitLab from the ServiceNow instance.** If
  GitLab sits behind an access proxy (e.g. Cloudflare Access), ServiceNow's native
  git client cannot attach the custom auth header that proxy expects — see
  `references/path-a-native-source-control.md` for the two owner-approved options
  (service token + credential-injection proxy, or a scoped egress-IP bypass
  policy). Never create or weaken that perimeter yourself.
- **A "created"/"pending" GitLab job is not a hang** — it means no online runner
  is assigned to the project (or group). Check `gitlab_runners` before assuming
  the pipeline or the `.gitlab-ci.yml` is broken.
- **A `yaml_errors: null` pipeline proves CI syntax, not ServiceNow reachability.**
  The `deploy_to_instance`/`publish_to_app_repo`/`verify_app_record` jobs still need
  `SN_INSTANCE_URL` reachable from wherever the runner executes — a syntactically
  valid, successfully *created* pipeline can still fail (or never run) for that
  reason alone.
- Both paths ultimately call the same `sn_cicd`/Table-API surface — once code is
  on the instance, `servicenow-cicd-devops` owns every promotion action from there
  (scans, update sets, plugin activation, ATF).
