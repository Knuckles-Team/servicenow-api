# Deploy & install

Two paths: the **CLI** pushes your local built package to your dev instance; **MCP
tools** orchestrate installs/publishes/rollbacks on remote instances from a
source-control repo or the app repo (the CI/CD path).

## Local (CLI)
```bash
now-sdk build            # required first
now-sdk deploy           # push built package to active instance
# or
now-sdk install --auth <alias>   # push to the profile's instance
```
`install` supports the OAuth `client_credentials` flow via env vars for CI/CD.

## Remote orchestration (MCP — `servicenow_cicd`)
Call as `servicenow_cicd(action="...", params_json="{...}")` (JSON string).

Install an app from a linked source-control repo:
```json
{"name":"<app_name_or_scope>","sys_id":"<app_sys_id>","auto_upgrade_base_app":false,"base_app_version":"","version":"1.0.0"}
```
(action `app_repo_install`)

Publish an app to the application repository (action `app_repo_publish`):
```json
{"sys_id":"<app_sys_id>","dev_notes":"release notes","version":"1.0.1"}
```

Roll an app back (action `app_repo_rollback`):
```json
{"name":"<app_scope>","version":"1.0.0"}
```

Batch install several apps (action `batch_install`):
```json
{"name":"my batch","packages":[{"id":"<sys_id>","type":"application","load_demo_data":false,"requested_version":"1.0.0"}]}
```

Poll a running job (action `progress`):
```json
{"progress_id":"<returned_progress_sys_id>"}
```

Instance scans for compliance/quality — actions `full_scan`, `point_scan`, `suite_scan`
(params vary by scan type; `point_scan` targets a table/record, `suite_scan` a suite sys_id).

## Choosing a path
- Deploying your own working copy to *your* dev instance → **CLI** (`deploy`/`install`).
- Promoting a versioned app across environments via repo/app-repo → **`servicenow_cicd`**.
- Field-level promotion via update sets → `servicenow_update_sets` (see `source-control.md`).

## Gotchas
- `deploy`/`install` fail or ship stale metadata without a fresh `build`.
- `servicenow_cicd` calls are asynchronous — capture the returned progress id and poll
  `progress` until complete before asserting success.
- Exact param keys differ slightly by instance family version; when a key is uncertain,
  discover with a minimal call and inspect the response, or check the verbose 1:1 tool.
