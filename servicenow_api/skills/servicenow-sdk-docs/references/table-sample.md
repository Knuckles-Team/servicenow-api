# Simple Table API Sample

This example shows the basic usage of the `Table` fluent interface for creating Tables in ServiceNow

## Example Location
Source Code: [assets/samples/table-sample](../assets/samples/table-sample)

## Code Samples

### `table-custom-column.now.ts`
Path: [table-sample/fluent/table-custom-column.now.ts](../assets/samples/table-sample/fluent/table-custom-column.now.ts)

```typescript
import { StringColumn, Table } from '@servicenow/sdk/core'

export const incident = Table({
    name: 'incident' as any,
    schema: {
        x_tablesample_custom_column: StringColumn({
            label: 'Custom Column',
            maxLength: 40,
        }),
    },
})

```

### `table-simple.now.ts`
Path: [table-sample/fluent/table-simple.now.ts](../assets/samples/table-sample/fluent/table-simple.now.ts)

```typescript
import { Table, StringColumn, IntegerColumn, BooleanColumn, DateColumn } from '@servicenow/sdk/core'

/**
 * This example creates a table in the ServiceNow platform with 4 columns.
 */
export const x_tablesample_name = Table({
    name: 'x_tablesample_name',
    schema: {
        string_column: StringColumn({ mandatory: true, label: 'String Column' }),
        integer_column: IntegerColumn({ mandatory: true, label: 'Integer Column' }),
        boolean_column: BooleanColumn({ mandatory: true }),
        date_column: DateColumn({ mandatory: true }),
    },
})

```

### `table-index.now.ts`
Path: [table-sample/fluent/table-index.now.ts](../assets/samples/table-sample/fluent/table-index.now.ts)

```typescript
import { BooleanColumn, DateTimeColumn, StringColumn, ReferenceColumn, Table } from '@servicenow/sdk/core'

export const x_tablesample_index = Table({
    name: 'x_tablesample_index',
    schema: {
        name: StringColumn({
            label: 'Name',
            mandatory: true,
        }),
        color: StringColumn({
            label: 'Color',
            dropdown: 'suggestion',
            mandatory: true,
            choices: {
                white: { label: 'White' },
                brown: { label: 'Brown' },
                black: { label: 'Black' },
            },
        }),
        active: BooleanColumn({ mandatory: false, label: 'Active', read_only: false, active: true, default: true }),
        owner: ReferenceColumn({
            mandatory: true,
            label: 'User',
            read_only: false,
            active: true,
            referenceTable: 'sys_user',
        }),
        sys_created_by: StringColumn({
            mandatory: false,
            label: 'Created by',
            read_only: false,
            active: true,
            maxLength: 40,
            dropdown: 'none',
        }),
        sys_created_on: DateTimeColumn({ mandatory: false, label: 'Created', read_only: false, active: true }),
    },
    display: 'name',
    index: [{ element: 'color', name: 'color_index', unique: false }],
})

```

### `table-extends.now.ts`
Path: [table-sample/fluent/table-extends.now.ts](../assets/samples/table-sample/fluent/table-extends.now.ts)

```typescript
import { ReferenceColumn, Table } from '@servicenow/sdk/core'

/**
 * This example creates a table in the ServiceNow platform that extends the task table, and has a reference colun
 */
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

```
