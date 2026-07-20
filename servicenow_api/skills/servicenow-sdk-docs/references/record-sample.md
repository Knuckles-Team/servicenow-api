# Simple Table API Sample

This example shows the basic usage of the `Record` fluent interface for creating Tables in ServiceNow.
The `Record` API is the low level interface into any record in a table. By referencing the table name, you can access any field for specifying the values to set.

## Example Location
Source Code: [assets/samples/record-sample](../assets/samples/record-sample)

## Code Samples

### `record-incident.now.ts`
Path: [record-sample/fluent/record-incident.now.ts](../assets/samples/record-sample/fluent/record-incident.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

//This example generates a record in the incident table

Record({
    $id: Now.ID['incident-1'],
    table: 'incident',
    data: {
        number: 'INC0010001',
        active: true,
        short_description: 'This is a sample incident',
        description: 'This is a sample incident description',
        comments: 'This is a sample comment',
        cmdb_ci: '265e09dbeb584baf9c111a7148c99529',
        urgency: '1',
        activity_due: '2025-01-02 12:30:00',
        approval: 'not requested',
        caller_id: '77ad8176731313005754660c4cf6a7de',
        notify: '1',
        priority: '3',
        opened_at: '2025-01-01 12:30:00',
    },
})

```

### `record-cmdb-ci.now.ts`
Path: [record-sample/fluent/record-cmdb-ci.now.ts](../assets/samples/record-sample/fluent/record-cmdb-ci.now.ts)

```typescript
import { Record } from '@servicenow/sdk/core'

//This example generates a record in the incident table

Record({
    $id: Now.ID['cmdb-ci-computer-1'],
    table: 'cmdb_ci_computer',
    data: {
        asset_tag: 'ASSET001',
        assigned: '2024-04-21 07:00:00',
        category: 'Hardware',
        company: '31bea3d53790200044e0bfc8bcbe5dec',
        cost_center: '7fb1cc99c0a80a6d30c04574d14c0acf',
        cpu_manufacturer: '7aad6d00c611228400f00e0f80b67d2d',
        cpu_speed: 798,
        first_discovered: '2006-09-12 20:55:20',
        install_date: '2023-10-29 08:00:00',
        model_id: 'a9a2d0c3c6112276010db16c5ddd3461',
        name: 'Computer 1',
        os: 'Windows XP Professional',
        os_service_pack: 'Service Pack 3',
        os_version: '5.1',
        po_number: 'PO27711',
        ram: '1543',
        serial_number: 'L3BB911',
    },
})

Record({
    $id: Now.ID['cmdb-ci-computer-2'],
    table: 'cmdb_ci_computer',
    data: {
        asset_tag: 'ASSET002',
        assigned: '2024-04-21 07:30:00',
        category: 'Hardware',
        company: '31bea3d53790200044e0bfc8bcbe5dec',
        cost_center: '7fb1cc99c0a80a6d30c04574d14c0acf',
        cpu_manufacturer: '7aad6d00c611228400f00e0f80b67d2d',
        cpu_speed: 798,
        first_discovered: '2006-09-12 20:55:20',
        install_date: '2023-10-29 08:00:00',
        model_id: 'a9a2d0c3c6112276010db16c5ddd3461',
        name: 'Computer 1',
        os: 'Windows XP Professional',
        os_service_pack: 'Service Pack 3',
        os_version: '5.1',
        po_number: 'PO27711',
        ram: '1543',
        serial_number: 'L3BB911',
    },
})

```
