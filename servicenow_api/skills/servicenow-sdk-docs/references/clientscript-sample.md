# Simple List API Sample

This example shows the basic usage of the `List` fluent interface for creating UI Lists in ServiceNow.

## Example Location
Source Code: [assets/samples/clientscript-sample](../assets/samples/clientscript-sample)

## Code Samples

### `clientscript.now.ts`
Path: [clientscript-sample/fluent/clientscript.now.ts](../assets/samples/clientscript-sample/fluent/clientscript.now.ts)

```typescript
import { ClientScript } from '@servicenow/sdk/core'

export default ClientScript({
    $id: Now.ID['sample1'],
    type: 'onLoad',
    ui_type: 'all',
    table: 'incident',
    global: true,
    name: 'sample_client_script',
    active: true,
    applies_extended: false,
    description: 'sample client script',
    isolate_script: false,
    script: Now.include('./clientscript.client.js')
})

```
