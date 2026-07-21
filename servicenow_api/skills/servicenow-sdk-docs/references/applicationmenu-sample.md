# Simple Table API Sample

This example shows the basic usage of the `ApplicationMenu` fluent interface for creating Application Menus in ServiceNow.

## Example Location
Source Code: [assets/samples/applicationmenu-sample](../assets/samples/applicationmenu-sample)

## Code Samples

### `application-menu.now.ts`
Path: [applicationmenu-sample/fluent/application-menu.now.ts](../assets/samples/applicationmenu-sample/fluent/application-menu.now.ts)

```typescript
import { ApplicationMenu } from '@servicenow/sdk/core'
import { activity_admin, appCategory } from './menu-category-roles.now'

export const menu = ApplicationMenu({
    $id: Now.ID['My App Menu'],
    title: 'My App Menu',
    hint: 'This is a hint',
    description: 'This is a description',
    category: appCategory,
    roles: [activity_admin],
    active: true,
})

export const menu2 = ApplicationMenu({
    $id: Now.ID['Menu 2'],
    title: 'Menu 2',
    hint: 'hint 2',
    description: 'This is a description',
    category: appCategory,
    active: true,
})

```

### `menu-category-roles.now.ts`
Path: [applicationmenu-sample/fluent/menu-category-roles.now.ts](../assets/samples/applicationmenu-sample/fluent/menu-category-roles.now.ts)

```typescript
import { Record, Role } from '@servicenow/sdk/core'

export const appCategory = Record({
    $id: Now.ID['sys_app_category_my_app'],
    table: 'sys_app_category',
    data: {
        name: 'My App Category',
        style: 'border: 1px solid #96bcdc; background-color: #FBFBFB;',
        default_order: 100,
    },
})

export const activity_admin = Role({
    name: 'x_appmenu.activity_admin',
    description: 'my role description',
})

```
