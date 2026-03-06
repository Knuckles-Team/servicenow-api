# UiAction Sample

This example shows the the usage of `UiAction` (`sys_ui_action`)

## Example Location
Source Code: [assets/samples/uiaction-sample](../assets/samples/uiaction-sample)

## Code Samples

### `ui-action.now.ts`
Path: [uiaction-sample/fluent/ui-action.now.ts](../assets/samples/uiaction-sample/fluent/ui-action.now.ts)

```typescript
import { UiAction } from '@servicenow/sdk/core'

UiAction({
    $id: Now.ID['car_info'],
    table: 'x_uiactionsample_ts_custom_cars',
    actionName: 'Car Information',
    name: 'View car info',
    active: true,
    showInsert: true,
    showUpdate: true,
    hint: 'View car info',
    condition: "current.type == 'SUV'",
    form: {
        showButton: true,
        showLink: true,
        showContextMenu: false,
        style: 'destructive',
    },
    list: {
        showLink: true,
        style: 'primary',
        showButton: true,
        showContextMenu: false,
        showListChoice: false,
        showBannerButton: true,
        showSaveWithFormButton: true,
    },
    workspace: {
        isConfigurableWorkspace: true,
        showFormButtonV2: true,
        showFormMenuButtonV2: true,
        clientScriptV2: `function onClick(g_form) {
                        }`,
    },
    script: `current.name =  "updated by script";
                current.update();`,
    roles: ['u_requestor'],
    client: {
        isClient: true,
        isUi11Compatible: true,
        isUi16Compatible: true,
    },
    order: 100,
    showQuery: false,
    showMultipleUpdate: false,
    isolateScript: false,
    includeInViews: ['specialView'],
    excludeFromViews: [],
})

```
