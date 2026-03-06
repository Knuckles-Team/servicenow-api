# Dependencies Sample

This example shows you how to use other tables in your ServiceNow instance as part of your application references. For example you may need to reference a
table from your instance that is not shipped as part of the SDK. To add the schema from these table(s) as a dependency in your application you must edit the
The `now-sdk dependencies` command can be used to fetch these definitions into your project that you configured in the `now.config.json` file. These definitions will
then be stored under the `src/fluent/generated` folder and automatically imported into your project for use.

## Example Location
Source Code: [assets/samples/dependencies-sample](../assets/samples/dependencies-sample)

## Code Samples

### `cat-item-record.now.ts`
Path: [dependencies-sample/fluent/cat-item-record.now.ts](../assets/samples/dependencies-sample/fluent/cat-item-record.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

// Use the sc_cat_item table dependency that was downloaded

Record({
    $id: Now.ID['cat-item-1'],
    table: 'sc_cat_item',
    data: {
        name: 'Cat Item 1',
        description: 'This is a cat item',
        price: 100,
    },
})

```

### `ui-action.now.ts`
Path: [dependencies-sample/fluent/ui-action.now.ts](../assets/samples/dependencies-sample/fluent/ui-action.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

// Use the sys_ui_action table dependency that was downloaded

const action = Record({
    $id: Now.ID['edit_in_catalog_builder'],
    table: 'sys_ui_action',
    data: {
        table: 'sc_cat_item',
        action_name: 'edit_in_catalog_builder',
        name: 'Edit in Catalog Builder',
        order: 600,
        active: true,
        form_button: true,
        form_context_menu: true,
        show_insert: true,
        show_update: true,
        client: true,
        ui11_compatible: true,
        form_style: 'primary',
        onclick: script`openItemInCatalogBuilder()`,
        condition: script`new global.ServiceCatalogVersioningUtils().canEditInBuilder(current)`,
        script: Now.include('./ui-action.server.js'),
    },
})

//Map the ui action to a role
Record({
    $id: Now.ID['edit_in_catalog_builder_role'],
    table: 'sys_ui_action_role',
    data: {
        sys_user_role: '2831a114c611228501d4ea6c309d626d', //admin
        sys_ui_action: action,
    },
})

```

### `script-include.now.ts`
Path: [dependencies-sample/fluent/script-include.now.ts](../assets/samples/dependencies-sample/fluent/script-include.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

/**
 * This will expose a sys_module through a script include so that it can be used in other application scopes through this script include
 */
Record({
    $id: Now.ID['si-module-1'],
    table: 'sys_script_include',
    data: {
        access: 'public',
        active: true,
        api_name: 'x_sysmodulesample.SampleScriptInclude',
        client_callable: false,
        mobile_callable: false,
        name: 'SampleScriptInclude',
        sandbox_callable: false,
        script: Now.include('./script-include.server.js'),
        sys_name: 'SampleClass',
    },
})

```
