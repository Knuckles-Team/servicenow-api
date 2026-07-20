# Automation API — Flow, Subflow, Action

All flow authoring imports come from `@servicenow/sdk/automation`; column types for
subflow inputs/outputs come from `@servicenow/sdk/core`.

```typescript
import { action, Flow, Subflow, wfa, trigger } from '@servicenow/sdk/automation'
import { BooleanColumn, ReferenceColumn, StringColumn } from '@servicenow/sdk/core'
```

## Flow
A top-level, trigger-started automation. Three positional args:
```typescript
Flow(
  { $id: Now.ID['x'], name: '...', description: '...' },  // metadata
  wfa.trigger(/* trigger */),                              // exactly one trigger
  (params) => { /* body: wfa.action / wfa.flowLogic */ },  // body
)
```
`params.trigger.*` exposes trigger outputs inside the body.

## Subflow
A reusable, callable automation with a **typed contract** — no trigger; invoked by flows
or scripts. It declares `inputs`, `outputs`, and optional `flowVariables`:
```typescript
Subflow(
  {
    $id: Now.ID['onboard'], name: '...', description: '...',
    inputs:  { user_sys_id: ReferenceColumn({ label: 'User', referenceTable: 'sys_user', mandatory: true }) },
    outputs: { laptop_assigned: BooleanColumn({ label: 'Laptop Assigned' }) },
    flowVariables: { laptop_found: BooleanColumn({ label: '...', default: false }) },
  },
  (params) => {
    // params.inputs.*  and  params.outputs.*
    wfa.flowLogic.assignSubflowOutputs({ $id: Now.ID['out'] }, params.outputs, { laptop_assigned: true })
  },
)
```
Inputs/outputs/flowVariables are declared with core Column types
(`StringColumn`, `BooleanColumn`, `ReferenceColumn`, `IntegerColumn`, …). Return values by
calling `wfa.flowLogic.assignSubflowOutputs` at the end.

## Action
Two distinct meanings — do not confuse them:
- **`action.core.*`** — the built-in *action steps* invoked inside a flow body via
  `wfa.action(...)` (log, lookUpRecord, createRecord, sendEmail, …). See
  `actions-and-script-actions.md`.
- **`ScriptAction`** (from `@servicenow/sdk/core`) — a standalone, event-driven server
  script (`sysevent_script_action`), authored independently of any flow. Also in
  `actions-and-script-actions.md`.

## The `$id` identity rule
Every construct and every step takes a `$id` — `Now.ID['stable_key']` or an explicit
sys_id. It is the **stable identity** across deploys: keep it constant so a re-deploy
updates the same flow/step; change it and you create a duplicate.

## Cross-reference
Full flow + subflow files: `servicenow-sdk-docs` → `assets/samples/flow-sample/`
(`flow-trigger-*.now.ts`, `subflow-sample.now.ts`) and `references/flow-sample.md`.
