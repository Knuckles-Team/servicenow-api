import { Record } from '@servicenow/sdk/core'



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


Record({
    $id: Now.ID['edit_in_catalog_builder_role'],
    table: 'sys_ui_action_role',
    data: {
        sys_user_role: '2831a114c611228501d4ea6c309d626d', 
        sys_ui_action: action,
    },
})
