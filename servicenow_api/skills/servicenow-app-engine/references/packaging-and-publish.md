# Packaging & publishing a scoped app

Once built (`servicenow-sdk-lifecycle` → `build`), a scoped app is promoted across
instances via the `servicenow-api` MCP server. Two mechanisms: **the application repo /
CI/CD** (`servicenow_cicd`) and **update sets** (`servicenow_update_sets`). Call tools as
`servicenow_<domain>(action="...", params_json="{...}")` (JSON string). Env + tag matrix:
`agent-tools/mcp-client/references/servicenow-api.md`.

## Path A — app repo / CI/CD (`servicenow_cicd`)
Preferred for versioned, code-first apps.

1. **Publish** the app to the application repository (action `app_repo_publish`):
   ```json
   {"sys_id":"<app_sys_id>","dev_notes":"initial release","version":"1.0.0"}
   ```
2. **Install** the published version on a target instance (action `app_repo_install`):
   ```json
   {"sys_id":"<app_sys_id>","version":"1.0.0","auto_upgrade_base_app":false,"base_app_version":""}
   ```
3. **Batch install** several apps at once (action `batch_install`):
   ```json
   {"name":"asset apps","packages":[{"id":"<sys_id>","type":"application","requested_version":"1.0.0","load_demo_data":false}]}
   ```
4. **Roll back** a bad release (action `app_repo_rollback`):
   ```json
   {"name":"x_acme_asset","version":"1.0.0"}
   ```
5. **Poll** any async job (action `progress`):
   ```json
   {"progress_id":"<returned_progress_sys_id>"}
   ```
6. **Scan** for quality/compliance before promotion — actions `full_scan`, `point_scan`,
   `suite_scan`.

The `<app_sys_id>` is the app's `sys_scope`/application record id (see
`scoped-app-anatomy.md`).

## Path B — update sets (`servicenow_update_sets`)
Use when changes originate in the UI, or must be previewed for collisions before commit.

```json
{"name":"x_acme_asset v1.0.1","description":"catalog + business rule"}
```
(action `update_set_create`) → capture changes → `update_set_retrieve` on the target →
**`update_set_preview`** (surface collisions) → `update_set_commit` (or
`update_set_commit_multiple`). Reverse with `update_set_back_out`.

## Choosing a path
- **Code-first app, version-to-version promotion** → Path A (publish/install), gated by an
  ATF suite (`servicenow-sdk-lifecycle` → `references/atf-run.md`).
- **UI-originated or mixed changes needing collision preview** → Path B (update sets).

## Gotchas
- `servicenow_cicd` calls are **asynchronous** — always capture the returned progress id and
  poll `progress` before declaring success.
- **Always `update_set_preview` before commit** — it surfaces collisions/skips you must
  resolve.
- Version bumps belong in the app record / release metadata; keep `version` consistent
  across publish → install → rollback.
- Full lifecycle sequencing (build → deploy → test → publish) lives in
  `servicenow-sdk-lifecycle` → `references/deploy-and-install.md` and `source-control.md`.
