# Flow logic

Branching, looping, waits, and flow termination are expressed with `wfa.flowLogic.*`
inside a flow/subflow body. Each takes a `{ $id, ... }` metadata object and (for
container logic) a callback holding the nested steps.

## Conditionals — if / elseIf / else
```typescript
wfa.flowLogic.if(
  { $id: Now.ID['check_high'], condition: `${wfa.dataPill(params.trigger.current.severity, 'string')}=1`, annotation: 'High severity' },
  () => { /* steps when true */ },
)
wfa.flowLogic.elseIf(
  { $id: Now.ID['check_med'], condition: `${wfa.dataPill(params.trigger.current.severity, 'string')}=2`, annotation: 'Medium' },
  () => { /* ... */ },
)
wfa.flowLogic.else({ $id: Now.ID['otherwise'] }, () => { /* ... */ })
```
- `condition` is a string built by interpolating **data pills** with operators
  (`=`, `!=`, `LIKE`, `ISEMPTY`, `=NULL`, `^` for AND). `annotation` is the human label
  shown in the UI.
- `elseIf`/`else` attach to the preceding `if` in source order.

## Loops — forEach
```typescript
wfa.flowLogic.forEach(
  wfa.dataPill(activeUsers.Records, 'records'),   // the collection pill
  { $id: Now.ID['loop_users'] },
  () => { /* steps per item */ },
)
```
Iterate a records/array pill (`'records'`, `'array.string'`). Steps inside run once per
item; reference the item via the same collection pill.

## Waits — waitForCondition
```typescript
wfa.action(
  action.core.waitForCondition,
  { $id: Now.ID['wait_resolved'] },
  { table_name: 'task', record: wfa.dataPill(task.Record.sys_id, 'reference'), conditions: 'state=6', timeout_duration: Duration({ days: 7 }) },
)
```
Pause until a record matches `conditions` or the `Duration(...)` timeout elapses.
(Time-based pauses like SLA milestones use `action.core.slaPercentageTimer`.)

## Termination & subflow outputs
- `wfa.flowLogic.endFlow({ $id, annotation })` — end the flow early (e.g. after a failed
  QA gate).
- `wfa.flowLogic.assignSubflowOutputs({ $id }, params.outputs, { field: value, ... })` —
  set a subflow's declared outputs before returning.

## Gotchas
- Give every branch/loop a **unique, stable `$id`**; duplicated ids collide on deploy.
- `condition` strings must interpolate data pills (`${wfa.dataPill(...)}`), not raw
  `params.*` — see `data-pills-and-values.md`.
- Nest logic by nesting callbacks; keep `if`/`elseIf`/`else` adjacent in source.

## Cross-reference
Nested if/elseIf/else, forEach, waitForCondition, endFlow, assignSubflowOutputs in
context: `servicenow-sdk-docs` → `references/flow-sample.md`.
