# Full app walkthrough — assembling a scoped app

A worked assembly of the five core artifacts into one coherent scoped app. Each step names
the Fluent construct and the bundled sample to adapt from (**cross-reference — do not
copy**). Assume the project is scaffolded (`servicenow-sdk-lifecycle` →
`references/project-init.md`) with scope `x_acme_asset`.

Scenario: a lightweight **Asset Request** app — a custom table, a business rule that
stamps requests, an ACL securing writes, an application menu for navigation, and a catalog
item so users can request an asset.

## 1. Data model — `Table`
Define `x_acme_asset_request` with the fields you need (string/reference/choice/date).
Adapt column types, `choices`, `display`, `index`, and `extends`/`auto_number` from:
- `servicenow-sdk-docs` → `references/table-sample.md` (and `hello-world-sample.md`).

Seed reference/config data with `Record({ table, data })` — see `record-sample.md`.

## 2. Server logic — `BusinessRule`
Add a `before` business rule on `x_acme_asset_request` that stamps/validates on insert.
The server logic lives in `src/server/*.server.js` and is referenced via
`Now.include(...)` or an import — see:
- `servicenow-sdk-docs` → `references/businessrule-sample.md`.

For event-driven server logic instead of a table rule, use `ScriptAction`
(`scriptaction-sample.md`). For reusable/cross-scope logic, a public script include
(`script-include-sample.md`, `sys_module-sample.md`).

## 3. Security — `Acl` + `Role`
Declare a `Role` (`x_acme_asset.manager`) and `Acl` entries for `create`/`write`/`read`/
`delete` on the table, gating by role/condition/security attribute. Adapt from:
- `servicenow-sdk-docs` → `references/acl-sample.md`.

## 4. Navigation — `ApplicationMenu`
Expose the app in the nav with an `ApplicationMenu` under a `sys_app_category`, gated by
the role from step 3. Adapt from:
- `servicenow-sdk-docs` → `references/applicationmenu-sample.md`.

## 5. Request UX — `ServiceCatalog`
Publish a catalog item / record producer (with a variable set) that creates an
`x_acme_asset_request` record for end users. Adapt from:
- `servicenow-sdk-docs` → `references/service-catalog-sample.md`.

## 6. (Optional) APIs & automation
- A scripted REST endpoint for integrations → `RestApi` (`restapi-sample.md`).
- A Flow that routes/notifies on new requests → author with
  **`servicenow-workflow-studio`** (samples: `flow-sample.md`).

## 7. Build, deploy, test
Hand off to **`servicenow-sdk-lifecycle`**:
`now-sdk dependencies` (if borrowing platform tables) → `now-sdk build` →
`deploy`/`install` → run an ATF suite (`servicenow_testing`).

## Assembly gotchas
- Keep every artifact in the **same scope** (`x_acme_asset_*`); reference the role by its
  scoped name in both the ACL and the menu.
- Order of files doesn't matter (constructs are records), but a stable `$id` per construct
  is essential so re-deploys update rather than duplicate.
- Borrowing a platform table (e.g. `sc_cat_item` for the catalog) requires a dependency
  pull first — see `servicenow-sdk-lifecycle` → `references/dependencies.md` and
  `servicenow-sdk-docs` → `references/dependencies-sample.md`.
