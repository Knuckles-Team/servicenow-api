---
name: servicenow-app-engine
description: >-
  Build scoped ServiceNow applications as metadata-as-code — the scope/`x_`
  prefix/now.config.json anatomy, how Fluent artifacts assemble into a whole app
  (table + business rule + ACL + menu + catalog), and how that reconciles with
  App Engine Studio / Application Studio. Use when the agent must design a scoped
  app's structure, map an App Engine Studio artifact to its Fluent API and sample,
  assemble a multi-artifact app, or package/publish a scoped app. Do NOT use for
  the now-sdk build/deploy/ATF lifecycle mechanics (use servicenow-sdk-lifecycle),
  for authoring Flow Designer flows/subflows (use servicenow-workflow-studio), for
  the raw bundled Fluent samples (use servicenow-sdk-docs), or for ad-hoc record
  CRUD against a live instance (use servicenow-table-api).
license: MIT
tags: [servicenow, scoped-app, metadata-as-code, app-engine-studio, fluent, packaging, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow App Engine (scoped apps as metadata-as-code)

A scoped ServiceNow application is a namespaced bundle of metadata records (tables, rules,
ACLs, menus, catalog items…). App Engine Studio (AES) / Application Studio build that
bundle through a UI; this skill builds the **same bundle as Fluent code** and reconciles
the two views. It defers the build/deploy/test mechanics to `servicenow-sdk-lifecycle`.

## When to use
- Designing a scoped app's shape: scope, `x_` prefix, `now.config.json`, file layout.
- Mapping an App Engine Studio artifact to the Fluent API that produces it.
- Assembling a coherent app from multiple artifacts (data model + logic + security + nav +
  request UX).
- Packaging/publishing a scoped app across instances.

## When NOT to use
- CLI lifecycle mechanics (init/build/transform/deploy/ATF) → `servicenow-sdk-lifecycle`.
- Flow Designer flows/subflows/actions → `servicenow-workflow-studio`.
- Reading the raw samples → `servicenow-sdk-docs`.
- Ad-hoc live record CRUD → `servicenow-table-api`.

## Prerequisites
- A Fluent project (scaffold via `servicenow-sdk-lifecycle` → `references/project-init.md`).
- For packaging/publish: the `servicenow-api` MCP server via the `mcp-client` skill. Env +
  tag matrix: `agent-tools/mcp-client/references/servicenow-api.md`.

## The mental model
Everything in a scoped app is a **record in a `sys_*` table, namespaced to a scope**.
Fluent constructs (`Table`, `BusinessRule`, `Acl`, `ApplicationMenu`, `ServiceCatalog`,
`Record`, …) are typed emitters for those records. "Build the app as code" = author those
constructs, then ship them via the SDK lifecycle.

## Reference map — open just-in-time
- **`references/scoped-app-anatomy.md`** — `sys_scope`, the `x_<prefix>_` namespace,
  `now.config.json`, `package.json`, and the `src/fluent/` layout. Read first when
  starting or structuring an app.
- **`references/app-engine-studio-concepts.md`** — what AES / Application Studio are, their
  artifact vocabulary (data tables, experiences, logic-and-automation, security), and how
  a code-first project coexists with them. Read when reconciling with the UI.
- **`references/metadata-as-code-mapping.md`** — the master table: **App Studio artifact →
  Fluent API → canonical `servicenow-sdk-docs` sample**. Read when you know *what* you want
  and need the *construct + example*.
- **`references/full-app-walkthrough.md`** — assemble a working app end-to-end (table +
  business rule + ACL + application menu + catalog item), cross-referencing the samples.
  Read when building a whole app rather than one artifact.
- **`references/packaging-and-publish.md`** — package and promote the scoped app across
  instances via `servicenow_cicd` + `servicenow_update_sets`. Read at release time.

## Quick artifact map (full table in metadata-as-code-mapping.md)
| App concern | Fluent API | Sample (in `servicenow-sdk-docs`) |
|-------------|-----------|-----------------------------------|
| Data model | `Table` / `Record` | `table-sample`, `record-sample`, `hello-world-sample` |
| Server logic | `BusinessRule`, `ScriptAction`, script includes | `businessrule-sample`, `scriptaction-sample`, `script-include-sample` |
| Security | `Acl`, `Role` | `acl-sample` |
| Navigation | `ApplicationMenu` | `applicationmenu-sample` |
| Request UX | `ServiceCatalog` | `service-catalog-sample` |
| APIs | `RestApi` | `restapi-sample` |
| Automation | `Flow` / `Subflow` | `flow-sample` (author via `servicenow-workflow-studio`) |

## Gotchas
- **The scope is fixed at init.** The `x_<prefix>_` namespace is baked into `now.config.json`
  and every table/artifact name — plan it up front (see `scoped-app-anatomy.md`).
- **Custom tables carry the scope prefix** (`x_<prefix>_<table>`); referencing platform
  tables you don't own needs a dependency pull (`servicenow-sdk-lifecycle` →
  `references/dependencies.md`).
- **Code-first and AES edit the same records.** Round-tripping via `now-sdk transform` /
  `init --from` keeps them in sync, but simultaneous edits from both sides collide — pick a
  source of truth.
- Building the app here does not deploy it — hand off to `servicenow-sdk-lifecycle`.
