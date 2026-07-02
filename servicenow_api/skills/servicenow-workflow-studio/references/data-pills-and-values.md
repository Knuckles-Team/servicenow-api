# Data pills & value helpers

Data flows between steps as **data pills**. In Fluent, wrap any value crossing a step
boundary with `wfa.dataPill(value, type)` so Flow Designer binds it correctly.

## wfa.dataPill(value, type)
```typescript
wfa.dataPill(params.trigger.current.short_description, 'string')
wfa.dataPill(sender.Record.sys_id, 'reference')
wfa.dataPill(activeUsers.Records, 'records')
```
Common `type` values seen in the samples:
| type | Use for |
|------|---------|
| `'string'` | Text / most scalar fields. |
| `'reference'` | A reference field / sys_id pointer. |
| `'records'` | A collection returned by `lookUpRecords` (iterate with `forEach`). |
| `'array.string'` | A list field (e.g. `additional_assignee_list`). |
| `'table_name'` | A dynamic table name (e.g. remote-query trigger). |
| `'glide_date_time'` | A date/time field. |

## Where values come from
- **Trigger outputs** → `params.trigger.*` (e.g. `params.trigger.current.sys_id`,
  `params.trigger.from_address`).
- **Action outputs** → the variable the `wfa.action(...)` call was assigned to:
  ```typescript
  const sender = wfa.action(action.core.lookUpRecord, { $id: Now.ID['s'] }, { table: 'sys_user', conditions: '...' })
  // then: wfa.dataPill(sender.Record.email, 'string')
  ```
  Single-record lookups expose `.Record.<field>`; multi-record lookups expose `.Records`.
- **Subflow inputs/outputs** → `params.inputs.*` / `params.outputs.*`.

## Value helpers
- **`TemplateValue({...})`** — wraps a field-values object for record create/update steps:
  ```typescript
  values: TemplateValue({ priority: 1, assigned_to: wfa.dataPill(user.Record.sys_id, 'reference') })
  ```
- **`Duration({ days, hours, minutes, seconds })`** — a timespan for `waitForCondition`
  timeouts and timers.
- **String interpolation** — build log messages/conditions with template literals that
  embed pills: `` `Created: ${wfa.dataPill(params.trigger.current.short_description, 'string')}` ``.

## Gotchas
- Passing a bare `params.trigger.field` (no `dataPill`) usually fails to bind — always
  wrap boundary-crossing values.
- The pill **type must match the field** (e.g. a sys_id is `'reference'`, not `'string'`),
  or the binding/condition misbehaves.
- In `field_values`/`values`, wrap the object in `TemplateValue(...)`; pass individual
  dynamic values as pills inside it.

## Cross-reference
Extensive pill usage (references, records, arrays, glide_date_time, TemplateValue,
Duration): `servicenow-sdk-docs` → `references/flow-sample.md`.
