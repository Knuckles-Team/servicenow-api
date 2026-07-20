# Triggers

A `Flow` has exactly one trigger, declared with `wfa.trigger(type, { $id }, { config })`.
Two families: **record triggers** (fire on table row changes) and **application
triggers** (fire on platform events). Trigger outputs are read in the body via
`params.trigger.*`.

```typescript
wfa.trigger(
  trigger.record.created,
  { $id: Now.ID['trg'] },
  { table: 'incident', condition: 'origin=NULL', run_flow_in: 'background' },
)
```

## Record triggers
| Trigger | Fires when |
|---------|-----------|
| `trigger.record.created` | A row is inserted into the table. |
| `trigger.record.updated` | A row is updated (optionally on `unique_changes`). |
| `trigger.record.createdOrUpdated` | Either insert or update. |

Common config keys (see the samples for full sets):
- `table` — the table to watch (e.g. `'incident'`, `'change_request'`).
- `condition` — an encoded query gate (e.g. `'active=true^impact=1'`, `'approval=approved'`).
- `run_flow_in` — `'background'` (typical).
- `trigger_strategy` — e.g. `'unique_changes'` for updated-triggers.
- `run_when_setting` / `run_when_user_setting` / `run_when_user_list` / `run_on_extended`
  — execution-context controls.

## Application triggers
| Trigger | Fires on |
|---------|----------|
| `trigger.application.inboundEmail` | Inbound email matching conditions (config: `email_conditions`, `target_table`). |
| `trigger.application.slaTask` | An SLA task lifecycle event (`params.trigger.task_sla_record`). |
| `trigger.application.remoteTableQuery` | A remote system querying a table (`params.trigger.query_id`, `query_parameters`, `table_name`). |
| `trigger.application.knowledgeManagement` | A knowledge-article event (`params.trigger.knowledge`). |

Application triggers often take an empty config `{}` and expose event-specific outputs on
`params.trigger`.

## Gotchas
- The `condition` is an **encoded query** (same syntax as `servicenow-table-api`'s
  `sysparm_query`) — `^` = AND, `^OR` = OR, operators like `LIKE`, `=NULL`, `ISEMPTY`.
- Match the trigger family to the event: a table change → record trigger; an email/SLA/
  knowledge/remote-query event → the matching application trigger.

## Cross-reference
Real trigger configs for every type above: `servicenow-sdk-docs` →
`references/flow-sample.md` (each `flow-trigger-*.now.ts`).
