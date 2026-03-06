# BusinessRule Sample

This example shows the the usage of the `BusinessRule` fluent interface for creating business rules in ServiceNow

## Example Location
Source Code: [assets/samples/businessrule-sample](../assets/samples/businessrule-sample)

## Code Samples

### `business-rule-1.now.ts`
Path: [businessrule-sample/fluent/business-rule-1.now.ts](../assets/samples/businessrule-sample/fluent/business-rule-1.now.ts)

```typescript
import { BusinessRule } from '@servicenow/sdk/core'

BusinessRule({
    $id: Now.ID['br1'],
    name: 'Sample Business Rule',
    active: true,
    table: 'sc_req_item',
    when: 'before',
    script: Now.include('./business-rule-1.server.js'),
})

```

### `business-rule-2.now.ts`
Path: [businessrule-sample/fluent/business-rule-2.now.ts](../assets/samples/businessrule-sample/fluent/business-rule-2.now.ts)

```typescript
import { BusinessRule } from '@servicenow/sdk/core'
import { businessRuleProcess } from '../server/br-rule-module'

BusinessRule({
    $id: Now.ID['br2'],
    name: 'Sample Business Rule 2',
    active: true,
    table: 'sc_req_item',
    when: 'before',
    script: businessRuleProcess,
})

```
