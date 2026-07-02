---
name: servicenow-sdk-lifecycle
description: >-
  The procedural spine for building ServiceNow applications as code with the
  `now-sdk` (`@servicenow/sdk`) CLI — the ordered lifecycle from init → auth →
  author Fluent → dependencies → build/transform → deploy/install →
  source-control → ATF, plus a "CLI vs MCP tool" decision table. Use when the
  agent must scaffold, authenticate, build, transform, deploy, install, version,
  source-control, or ATF-test a scoped app locally, or orchestrate the same steps
  against a remote instance via the servicenow-api MCP server. Do NOT use for
  authoring Flow Designer flows/subflows/actions (use servicenow-workflow-studio),
  for scoped-app metadata anatomy and App Engine Studio reconciliation (use
  servicenow-app-engine), for the bundled Fluent code samples (use
  servicenow-sdk-docs), or for plain table CRUD against a live instance (use
  servicenow-table-api).
license: MIT
tags: [servicenow, now-sdk, fluent, cli, lifecycle, ci-cd, source-control, atf, deploy]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow SDK Lifecycle (the procedural spine)

The end-to-end procedure for taking a ServiceNow scoped application from an empty
folder to an installed, tested app — driven by the **`now-sdk`** command-line
interface (published as **`@servicenow/sdk`**) for local authoring/build/deploy, and
handed off to the **`servicenow-api` MCP server** for remote-instance orchestration
(CI/CD pipelines, update sets, plugins, source-control import).

Sibling skills own the *content* of each artifact; this skill owns the *ordering*.

## When to use
- Standing up a new Fluent project or converting an existing scoped app to code.
- Authenticating the CLI to an instance and managing multiple instance profiles.
- The build → transform → deploy/install loop for a local project.
- Versioning, source-control import/apply, and running ATF suites as part of CI/CD.

## When NOT to use
- Authoring flows/subflows/actions → `servicenow-workflow-studio`.
- Scoped-app anatomy / App Engine Studio reconciliation → `servicenow-app-engine`.
- Reading the bundled Fluent samples → `servicenow-sdk-docs`.
- Ad-hoc record CRUD / queries against a live instance → `servicenow-table-api`.

## Prerequisites
- **Node** v20+ and **pnpm** v9+ (matches the `servicenow-sdk-docs` samples).
- The CLI: `npx @servicenow/sdk <command>`, or install it and call `now-sdk <command>`.
- For MCP-driven steps: connect via the `mcp-client` skill to the **`servicenow-api`**
  server. Env: `SERVICENOW_INSTANCE`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`
  (+ optional OAuth `SERVICENOW_CLIENT_ID`/`SERVICENOW_CLIENT_SECRET`,
  `SERVICENOW_SSL_VERIFY`). Full env/tag matrix (do not duplicate):
  `agent-tools/mcp-client/references/servicenow-api.md`. `MCP_TOOL_MODE`
  (`condensed`|`verbose`|`both`) selects the 30 condensed tools (used below) vs. the
  119 one-to-one verbose tools.

## The lifecycle (ordered)
1. **Init** the project — scaffold or convert from an installed app. → `references/project-init.md`
2. **Auth** the CLI to the target instance and pick a profile. → `references/auth-and-profiles.md`
3. **Author Fluent** metadata under `src/fluent/` (tables, business rules, ACLs, flows, …).
   The *what* lives in the sibling skills and `servicenow-sdk-docs`; this skill only
   sequences it.
4. **Dependencies** — pull schema/type definitions for platform tables you reference.
   → `references/dependencies.md`
5. **Build / transform** — compile Fluent to a deployable package; transform existing
   XML metadata into Fluent. → `references/build-transform.md`
6. **Deploy / install** — push the built package to the instance. → `references/deploy-and-install.md`
7. **Source-control** — commit; import a repo or apply remote changes on the instance.
   → `references/source-control.md`
8. **ATF** — run Automated Test Framework suites to validate. → `references/atf-run.md`

Every `now-sdk` subcommand and its flags is catalogued in `references/cli-commands.md` —
open it whenever the exact command syntax is needed.

## CLI vs MCP tool — decision table
Do the local, authoring-side work with the **CLI**; do remote-instance orchestration
with **MCP tools**. Rule of thumb: *if it writes files in your project or talks to your
keychain, it's the CLI; if it acts on a running instance's pipelines/records, it's an
MCP tool.*

| Task | Use the `now-sdk` CLI | Use a `servicenow-api` MCP tool |
|------|:---------------------:|:-------------------------------:|
| Scaffold / convert a project (`init`) | ✅ | — |
| Store instance credentials (`auth`) | ✅ | — (MCP uses its own env creds) |
| Pull table type defs (`dependencies`) | ✅ | — |
| Compile package (`build`) / XML→Fluent (`transform`) | ✅ | — |
| Deploy the built package to *your* dev instance | ✅ (`deploy`/`install`) | — |
| Install an app **from a source-control repo** on a remote instance | — | `servicenow_cicd` → `app_repo_install` |
| Publish an app to the app repo | — | `servicenow_cicd` → `app_repo_publish` |
| Roll an app back | — | `servicenow_cicd` → `app_repo_rollback` |
| Batch install multiple apps | — | `servicenow_cicd` → `batch_install` |
| Instance scans (compliance) | — | `servicenow_cicd` → `full_scan`/`point_scan`/`suite_scan` |
| Poll a running CI/CD job | — | `servicenow_cicd` → `progress` |
| Import a repo / apply remote SC changes | — | `servicenow_source_control` |
| Create/preview/commit/back-out update sets | — | `servicenow_update_sets` |
| Run an ATF suite on the instance | — | `servicenow_testing` → `run_test_suite` |
| Activate / roll back a plugin | — | `servicenow_plugins` |

## MCP handoff — condensed tools
Call condensed tools as `servicenow_<domain>(action="...", params_json="{...}")` where
`params_json` is a **JSON string** (serialize it — it is not an object).

| Condensed tool | Actions (lifecycle-relevant) |
|----------------|------------------------------|
| `servicenow_source_control` | `apply_remote_source_control_changes`, `import_repository` |
| `servicenow_cicd` | `app_repo_install`, `app_repo_publish`, `app_repo_rollback`, `batch_install`, `full_scan`, `point_scan`, `suite_scan`, `progress` |
| `servicenow_update_sets` | `update_set_create`, `update_set_retrieve`, `update_set_preview`, `update_set_commit`, `update_set_commit_multiple`, `update_set_back_out` |
| `servicenow_testing` | `run_test_suite` |
| `servicenow_plugins` | `activate_plugin`, `rollback_plugin` |

Details, parameters, and `params_json` recipes for each handoff live in
`references/source-control.md`, `references/deploy-and-install.md`, and
`references/atf-run.md`. Open them just-in-time.

## Gotchas
- **Build before deploy.** `deploy`/`install` push a package that `build` produced — a
  stale or missing build ships old metadata.
- **Auth is per-instance and lives in the OS keychain**, not in the repo. CI uses
  non-interactive auth (password- or OAuth-via-env); see `references/auth-and-profiles.md`.
- **CLI acts on the instance you authed; MCP acts on `SERVICENOW_INSTANCE`.** Confirm
  they point where you intend before deploying.
- **`transform` is destructive to the source XML** it converts (it removes converted
  metadata and scaffolds Fluent into the generated dir) — commit first.
- CLI subcommands and flags evolve per family release; treat `references/cli-commands.md`
  as a summary and confirm against the [official CLI docs](https://www.servicenow.com/docs/r/application-development/servicenow-sdk/servicenow-sdk-cli-commands.html)
  when a flag is load-bearing.
