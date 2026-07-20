# solidjs-ui-page-sample

No description provided.

## Example Location
Source Code: [assets/samples/solidjs-ui-page-sample](../assets/samples/solidjs-ui-page-sample)

## Code Samples

### `index.now.ts`
Path: [solidjs-ui-page-sample/fluent/index.now.ts](../assets/samples/solidjs-ui-page-sample/fluent/index.now.ts)

```typescript
//Add your Fluent APIs here and in other now.ts files under src/fluent

```

### `incident.now.ts`
Path: [solidjs-ui-page-sample/fluent/tables/incident.now.ts](../assets/samples/solidjs-ui-page-sample/fluent/tables/incident.now.ts)

```typescript
import '@servicenow/sdk/global'
import { Table, StringColumn, DateTimeColumn, IntegerColumn } from '@servicenow/sdk/core'

// Create the incident table for our application
export const x_solidjs_example_incident = Table({
    name: 'x_solidjs_example_incident',
    label: 'Incident',
    schema: {
        number: StringColumn({
            label: 'Number',
            maxLength: 40,
            read_only: true,
            default: 'javascript:global.getNextObjNumberPadded();'
        }),
        short_description: StringColumn({
            label: 'Short Description',
            maxLength: 160,
            mandatory: true,
        }),
        description: StringColumn({
            label: 'Description',
            maxLength: 4000,
        }),
        status: StringColumn({
            label: 'Status',
            maxLength: 40,
            choices: {
                new: { label: 'New', sequence: 0 },
                in_progress: { label: 'In Progress', sequence: 1 },
                on_hold: { label: 'On Hold', sequence: 2 },
                resolved: { label: 'Resolved', sequence: 3 },
                closed: { label: 'Closed', sequence: 4 },
            },
            default: 'new',
        }),
        priority: IntegerColumn({
            label: 'Priority',
            choices: {
                '1': { label: 'Critical', sequence: 0 },
                '2': { label: 'High', sequence: 1 },
                '3': { label: 'Moderate', sequence: 2 },
                '4': { label: 'Low', sequence: 3 },
            },
            default: '3',
        }),
        opened_at: DateTimeColumn({
            label: 'Opened At',
            default: 'javascript:new GlideDateTime().getDisplayValue();',
        }),
        resolved_at: DateTimeColumn({
            label: 'Resolved At',
        }),
    },
    accessible_from: 'public',
    caller_access: 'tracking',
    actions: ['create', 'read', 'update', 'delete'],
    allow_web_service_access: true,
    auto_number: {
        prefix: 'INC',
        number: 1000,
        number_of_digits: 7
    }
})

```

### `incident-manager.now.ts`
Path: [solidjs-ui-page-sample/fluent/ui-pages/incident-manager.now.ts](../assets/samples/solidjs-ui-page-sample/fluent/ui-pages/incident-manager.now.ts)

```typescript
import '@servicenow/sdk/global'
import { UiPage } from '@servicenow/sdk/core'
import incidentPage from '../../client/index.html'

UiPage({
    $id: Now.ID['incident-manager-page'],
    endpoint: 'x_solidjs_example_incident_manager.do',
    description: 'Incident Response Manager UI Page',
    category: 'general',
    html: incidentPage,
    direct: true,
})

```
