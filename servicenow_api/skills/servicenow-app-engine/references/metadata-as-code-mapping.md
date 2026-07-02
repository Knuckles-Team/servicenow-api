# Metadata-as-code mapping

The master lookup: an App Engine Studio / Application Studio artifact → the Fluent API that
emits it → the canonical bundled sample. All samples live in the sibling
**`servicenow-sdk-docs`** skill at `assets/samples/<name>/` with a reference at
`references/<name>.md`. **Cross-reference these — never copy the `.now.ts` in.**

| App Studio / AES artifact | Underlying table | Fluent API (`import from`) | Sample (`servicenow-sdk-docs`) |
|---------------------------|------------------|----------------------------|--------------------------------|
| Table / columns | `sys_db_object`, `sys_dictionary` | `Table`, `*Column` (`@servicenow/sdk/core`) | `table-sample`, `hello-world-sample` |
| Seed / data record | any table | `Record` (`@servicenow/sdk/core`) | `record-sample`, `hello-world-sample` |
| Business rule | `sys_script` | `BusinessRule` (`@servicenow/sdk/core`) | `businessrule-sample` |
| Script action (event) | `sysevent_script_action` | `ScriptAction` (`@servicenow/sdk/core`) | `scriptaction-sample` |
| Script include | `sys_script_include` | `Record({ table: 'sys_script_include' })` | `script-include-sample`, `sys_module-sample` |
| ACL | `sys_security_acl` | `Acl` (`@servicenow/sdk/core`) | `acl-sample` |
| Role | `sys_user_role` | `Role` (`@servicenow/sdk/core`) | `acl-sample`, `applicationmenu-sample` |
| UI action | `sys_ui_action` | `Record({ table: 'sys_ui_action' })` | `uiaction-sample`, `dependencies-sample` |
| Client script | `sys_script_client` | client-script construct / `Record` | `clientscript-sample` |
| List / list view | `sys_ui_list` | `List` | `list-sample` |
| Application menu / module | `sys_app_application`, `sys_app_module` | `ApplicationMenu` (`@servicenow/sdk/core`) | `applicationmenu-sample` |
| Application category | `sys_app_category` | `Record({ table: 'sys_app_category' })` | `applicationmenu-sample` |
| Service catalog item / record producer / variable set | `sc_cat_item`, `sc_cat_item_producer`, `item_option_new` | `ServiceCatalog` | `service-catalog-sample` |
| Scripted REST API | `sys_ws_definition` (+ resources) | `RestApi` | `restapi-sample` |
| UI page | `sys_ui_page` | `UiPage` | `uipage-sample` |
| React UI page | `sys_ui_page` (+ bundle) | `UIPage` (React) | `react-ui-page-ts-sample` |
| SolidJS / Svelte / Vue UI page | `sys_ui_page` (+ bundle) | framework UI page | `solidjs-ui-page-sample`, `svelte-ui-page-sample`, `vue-ui-page-sample` |
| Service Portal widget/page | Service Portal tables | Service Portal constructs | `service-portal-sample` |
| Flow / subflow / action | `sys_hub_flow`, `sys_hub_sub_flow` | `Flow`, `Subflow`, `wfa.*` (`@servicenow/sdk/automation`) | `flow-sample` — author via `servicenow-workflow-studio` |
| ATF test / suite | `sys_atf_test` | `Test` (`@servicenow/sdk/core`) | `test-atf-sample` — run via `servicenow-sdk-lifecycle` |
| Cross-scope call | `sys_module` | `Record` + public script include | `sys_module-sample` |
| Table dependency (borrowed table) | (external table) | `now-sdk dependencies` + `Record` | `dependencies-sample` |

## How to use this table
1. Identify the artifact you need (left column) — think in App Studio / AES terms.
2. Note the **Fluent API** and its import module.
3. Open the named **sample** in `servicenow-sdk-docs` for a real, working example of the
   exact construct, then adapt it into your scope.

## Notes
- Constructs importing from `@servicenow/sdk/core` are data/metadata; the automation family
  (`Flow`/`Subflow`/`wfa`) imports from `@servicenow/sdk/automation`.
- Where no dedicated construct exists, the generic `Record({ table, data })` emitter writes
  any table's record directly (e.g. `sys_ui_action`, `sys_app_category`, `sys_script_include`).
- Column types (`StringColumn`, `IntegerColumn`, `BooleanColumn`, `DateColumn`,
  `DateTimeColumn`, `ReferenceColumn`) and table options (`extends`, `extensible`,
  `auto_number`, `index`, `display`, `choices`) are shown in `table-sample`.
