# Path B — GitLab-CI-driven promotion

A GitLab pipeline builds the scoped app with the `now-sdk` CLI and promotes it
through the same `sn_cicd`/Table-API surface `servicenow_cicd`/`servicenow_table_api`
wrap — reachability runs the other direction from Path A: the **GitLab runner**
reaches outbound to the ServiceNow instance, not the instance reaching GitLab.

## The template

`assets/gitlab-ci-template.yml` — four stages, one job each:

| Stage | Job | Does |
|---|---|---|
| `build` | `build` | `now-sdk build` the Fluent project into installable artifacts |
| `deploy` | `deploy_to_instance` | `now-sdk install` against `$SN_INSTANCE_URL` |
| `promote` | `publish_to_app_repo` | `POST /api/sn_cicd/app_repo/publish` — the same endpoint `servicenow_cicd` action `app_repo_publish` wraps (`servicenow_api/api/api_client_devops.py`) |
| `verify` | `verify_app_record` | `GET /api/now/table/sys_app` filtered by scope — the same endpoint `servicenow_table_api` action `get_table` wraps |

Jobs `needs:` the previous stage's job, so a failure anywhere stops the chain.

## Required CI/CD variables

Set these as **masked, protected** GitLab CI/CD variables on the project (never
commit them):

| Variable | Used by | Notes |
|---|---|---|
| `SN_INSTANCE_URL` | `deploy_to_instance`, `promote`, `verify` | e.g. `https://dev12345.service-now.com` |
| `SN_USERNAME` | all ServiceNow-facing jobs | Basic-auth user with rights to install/publish |
| `SN_PASSWORD` | all ServiceNow-facing jobs | Mask + protect — never echo it in `script:` |
| `SN_APP_SYS_ID` | `promote`, `verify` | The app's `sys_scope`/application record id |
| `SN_APP_SCOPE` | `verify` | The app's scope name, e.g. `x_myco_app` |

## Reading pipeline/job status correctly

A pipeline that was **created** and has `"yaml_errors": null` proves the
`.gitlab-ci.yml` is syntactically valid GitLab CI — it proves **nothing** about
whether the jobs will actually run or reach ServiceNow. Two independent gaps can
each leave every job stuck at `pending`/`created` forever, and they look
identical from the pipeline status alone:

1. **No online runner assigned to the project (or its group).** Check
   `gitlab_runners` action `get_all` — an `"online": false"` or
   wrong-group-scoped runner means the job never starts. This is a CI/ops
   configuration gap (assign or enable a runner), not a defect in this skill or
   the template.
2. **`SN_INSTANCE_URL` unreachable from wherever the runner executes.** Even
   with a runner attached, `deploy_to_instance`/`publish_to_app_repo`/
   `verify_app_record` will fail (or hang, depending on timeout config) if the
   runner's network can't reach the instance. This is independent of the
   runner-assignment gap above — a project can have both, either, or neither.

Confirm forward progress with `gitlab_pipelines` action `get` (status per job)
before assuming either gap is the cause.

## Local `now-sdk build` note

`now-sdk` is published as `@servicenow/sdk` on the public npm registry. A GitLab
runner's own outbound network is what matters for `npm`/`pnpm install` and the
`build`/`deploy` steps — a sandboxed *authoring* environment without npm
registry access is a property of that sandbox, not of the pipeline or this
skill; it does not need to be worked around here.
