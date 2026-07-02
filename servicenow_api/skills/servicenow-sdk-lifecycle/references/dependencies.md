# Dependencies — using platform tables you don't own

When your Fluent code references a table that is **not shipped as part of the SDK** (e.g.
`sc_cat_item`, `sys_ui_action`, `sys_script_include`), you must pull that table's schema
into the project so the types resolve and the reference compiles.

## Workflow
1. Declare the needed tables in `now.config.json` (the dependency list).
2. Run:
   ```bash
   now-sdk dependencies
   ```
3. Definitions are written under `src/fluent/generated` and **auto-imported** — you can
   now `Record({ table: 'sc_cat_item', ... })` etc. with type support.

## Cross-reference (do not copy)
The canonical worked example — seeding an `sc_cat_item`, wiring a `sys_ui_action` with
`onclick`/`condition` scripts and mapping it to a role, and exposing a `sys_script_include`
cross-scope — is bundled at:
- `servicenow-sdk-docs` → `assets/samples/dependencies-sample/`
- `servicenow-sdk-docs` → `references/dependencies-sample.md`

## Gotchas
- Re-run `now-sdk dependencies` after adding a new table to the config; missing defs
  surface as unresolved-type/compile errors at `build`.
- Treat `src/fluent/generated` as generated output — regenerate rather than hand-edit.
- Cross-scope calls to a script include require the include's `access: 'public'` and the
  right `api_name` (see the dependencies sample's `script-include.now.ts`).
