# Hello World Sample

This is a Hello World example that shows you how to set up and do basic configuration of the SDK.

## Example Location
Source Code: [assets/samples/hello-world-sample](../assets/samples/hello-world-sample)

## Code Samples

### `sample-table.now.ts`
Path: [hello-world-sample/fluent/sample-table.now.ts](../assets/samples/hello-world-sample/fluent/sample-table.now.ts)

```typescript
import { DateTimeColumn, IntegerColumn, StringColumn, Table } from '@servicenow/sdk/core'

/**
 * This will create a table in the ServiceNow instance called x_helloworld_tableone
 */
export const x_helloworld_tableone = Table({
    name: 'x_helloworld_tableone',
    label: 'Example Table',
    schema: {
        string_field: StringColumn({ label: 'String Field', mandatory: true }),
        integer_field: IntegerColumn({ label: 'Integer Field', mandatory: true }),
        datetime_field: DateTimeColumn({ label: 'Date Time Field' }),
    },
})

```

### `sample-table-record.now.ts`
Path: [hello-world-sample/fluent/sample-table-record.now.ts](../assets/samples/hello-world-sample/fluent/sample-table-record.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

/**
 * This will create a single record in the x_helloworld_tableone table
 */
Record({
    table: 'x_helloworld_tableone',
    $id: Now.ID['x_helloworld_tableone_record1'],
    data: {
        string_field: 'Hello World 1',
        datetime_field: '01-01-2024 12:00:00',
        integer_field: 1,
    },
})

```
