import { ReferenceColumn, Table } from '@servicenow/sdk/core'


export const x_tablesample_extends = Table({
    name: 'x_tablesample_extends',
    extends: 'task',
    extensible: true,
    display: 'Extension Example Table',
    auto_number: {
        prefix: 'sample',
        number: 100,
        number_of_digits: 9,
    },
    schema: {
        user_reference_column: ReferenceColumn({
            mandatory: true,
            label: 'User Reference',
            referenceTable: 'sys_user',
        }),
    },
})
