# Actions & script actions

Two things called "action" — the built-in **flow action steps** (`action.core.*`, run via
`wfa.action`) and standalone **`ScriptAction`** (event-driven server scripts).

## Flow action steps — wfa.action(action.core.X, { $id }, { params })
```typescript
wfa.action(
  action.core.updateRecord,
  { $id: Now.ID['upd'], annotation: 'Mark in progress' },
  { table_name: 'incident', record: wfa.dataPill(rec.Record.sys_id, 'reference'), values: TemplateValue({ state: '2' }) },
)
```
`action.core.*` steps seen in the samples (params abbreviated — see the sample for exact
keys):

| Action | Purpose | Key params |
|--------|---------|-----------|
| `log` | Write a flow log line | `log_level`, `log_message` |
| `lookUpRecord` | Fetch one record | `table`, `conditions`, `if_multiple_records_are_found_action` → `.Record.*` |
| `lookUpRecords` | Fetch many records | `table`, `conditions`, `max_results`, `sort_column` → `.Records` |
| `createRecord` | Insert a record | `table_name`, `values: TemplateValue({...})` → `.record` |
| `updateRecord` | Update a record | `table_name`, `record`, `values` |
| `createTask` | Create a task record | `task_table`, `field_values: TemplateValue({...})` |
| `sendEmail` | Send an email | `table_name`, `ah_to`, `ah_subject`, `ah_body`, `record` |
| `sendNotification` | Trigger a notification record | `table_name`, `record`, `notification` |
| `sendSms` | Send an SMS | `recipients`, `message` |
| `getAttachmentsOnRecord` | List attachments | `source_record` → `.parameter` |
| `copyAttachment` | Copy an attachment | `target_record`, `attachment_record`, `table` |
| `slaPercentageTimer` | Pause until % of SLA elapsed | `percentage` |
| `waitForCondition` | Pause until a record matches | `table_name`, `record`, `conditions`, `timeout_duration: Duration({...})` |

Bind the call to a `const` to consume its output downstream
(`const r = wfa.action(...)` → `wfa.dataPill(r.Record.field, ...)`).

## Standalone ScriptAction (sysevent_script_action)
An event-driven server script, authored independently of any flow, from
`@servicenow/sdk/core`:
```typescript
import { ScriptAction } from '@servicenow/sdk/core'
import { insertIncident } from '../server/action.js'

ScriptAction({
  $id: Now.ID['sample-script-action'],
  name: 'SampleScriptAction',
  active: true,
  description: 'Insert an incident',
  script: insertIncident,               // server-side function reference
  eventName: 'sample.event',            // the event that fires it
  order: 100,
  conditionScript: "gs.hasRole('my_role')",
})
```
Fields: `name`, `active`, `script` (a referenced server function), `eventName`, `order`,
`conditionScript`. Use it for reactive server logic keyed to a platform event rather than
a Flow Designer flow.

## Gotchas
- Server logic (`script`) is referenced from a server file (import or `Now.include(...)`),
  not inlined in the action object.
- `sendNotification` fires a pre-configured notification record by name; `sendEmail`
  composes an ad-hoc email inline.
- Match the output accessor to the action: single-record → `.Record`, multi → `.Records`,
  create → `.record`, attachments → `.parameter`.

## Cross-reference
- Action steps in context: `servicenow-sdk-docs` → `references/flow-sample.md`.
- ScriptAction: `servicenow-sdk-docs` → `assets/samples/scriptaction-sample/` and
  `references/scriptaction-sample.md`.
