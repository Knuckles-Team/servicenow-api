# ScriptAction Sample

This example shows the the usage of `ScriptAction` (`sysevent_script_action`)

## Example Location
Source Code: [assets/samples/scriptaction-sample](../assets/samples/scriptaction-sample)

## Code Samples

### `script-action.now.ts`
Path: [scriptaction-sample/fluent/script-action.now.ts](../assets/samples/scriptaction-sample/fluent/script-action.now.ts)

```typescript
import { ScriptAction } from '@servicenow/sdk/core'
import { insertIncident } from '../server/action.js'

ScriptAction({
    $id: Now.ID['sample-script-action'],
    name: 'SampleScriptAction',
    active: true,
    description: 'Insert an incident',
    script: insertIncident,
    eventName: 'sample.event',
    order: 100,
    conditionScript: "gs.hasRole('my_role')",
})

```
