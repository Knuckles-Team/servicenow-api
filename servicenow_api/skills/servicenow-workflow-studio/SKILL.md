---
name: servicenow-workflow-studio
description: >-
  Author ServiceNow Flow Designer flows, subflows, and actions as code with the
  Fluent `@servicenow/sdk/automation` API (`Flow`, `Subflow`, `wfa.trigger`,
  `wfa.action`, `wfa.flowLogic`, `wfa.dataPill`), plus how each Fluent construct
  maps to the Flow Designer UI. Use when the agent must write or explain a flow,
  subflow, trigger, flow-logic branch/loop, data pill, or script action in code,
  or introspect a deployed flow's graph via the servicenow-api MCP server. Do NOT
  use for the build/deploy/ATF lifecycle of the app that contains the flow (use
  servicenow-sdk-lifecycle), for scoped-app metadata anatomy (use
  servicenow-app-engine), for the raw bundled flow samples (use
  servicenow-sdk-docs), or for record CRUD against a live instance (use
  servicenow-table-api).
license: MIT
tags: [servicenow, flow-designer, fluent, automation, subflow, trigger, low-code, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Workflow Studio (Flow Designer as code)

Flow Designer is ServiceNow's low-code automation surface. The Fluent
`@servicenow/sdk/automation` API expresses the *same* flows/subflows/actions as
TypeScript source, so they live in a repo and ship through the SDK lifecycle. This skill
is about **authoring that code and mapping it back to the UI** — it defers build/deploy
to `servicenow-sdk-lifecycle`.

## When to use
- Writing a `Flow(...)`, `Subflow(...)`, or `ScriptAction(...)` in Fluent.
- Choosing/configuring a trigger (record or application).
- Adding flow logic: if / elseIf / else / forEach / waitForCondition / endFlow.
- Wiring data pills between a trigger, action outputs, and downstream inputs.
- Introspecting a deployed flow's structure (mermaid graph, metadata) via MCP.

## When NOT to use
- Building/deploying/testing the containing app → `servicenow-sdk-lifecycle`.
- Scoped-app anatomy / App Engine Studio → `servicenow-app-engine`.
- Reading the raw samples → `servicenow-sdk-docs`.
- Ad-hoc live record CRUD → `servicenow-table-api`.

## Canonical samples (cross-reference — never copy in)
Every construct below has a worked example bundled in the sibling skill:
- Flows, subflows, triggers, flow logic, data pills:
  `servicenow-sdk-docs` → `assets/samples/flow-sample/` and `references/flow-sample.md`.
- Script actions (`sysevent_script_action`):
  `servicenow-sdk-docs` → `assets/samples/scriptaction-sample/` and
  `references/scriptaction-sample.md`.

Open those when you need a full, real file; the references here teach the *shape and
rules* so you can compose new ones.

## The shape of a flow
```typescript
import { action, Flow, wfa, trigger } from '@servicenow/sdk/automation'

export const myFlow = Flow(
  { $id: Now.ID['my_flow'], name: 'My Flow', description: '...' },
  wfa.trigger(trigger.record.created, { $id: Now.ID['trg'] }, { table: 'incident', condition: 'active=true' }),
  (params) => {
    wfa.action(action.core.log, { $id: Now.ID['log'] }, { log_level: 'info', log_message: '...' })
    // flow logic, more actions, data pills ...
  },
)
```
Three positional arguments: **metadata** (`$id`/`name`/`description`), a **trigger**
(`wfa.trigger`), and the **body** `(params) => { ... }`. `params.trigger.*` exposes trigger
outputs to the body.

## Reference map — open just-in-time
- **`references/automation-api.md`** — `Flow` vs `Subflow` vs `Action`; imports; the
  `$id`/`Now.ID` identity rule; subflow inputs/outputs/flowVariables. Read first when
  starting any flow.
- **`references/triggers.md`** — record triggers (`created`/`updated`/`createdOrUpdated`)
  and application triggers (inbound email, SLA task, remote table query, knowledge mgmt);
  their config keys. Read when picking/configuring a trigger.
- **`references/flow-logic.md`** — `wfa.flowLogic.if/elseIf/else/forEach/
  waitForCondition/endFlow/assignSubflowOutputs`. Read when adding branching/looping/waits.
- **`references/data-pills-and-values.md`** — `wfa.dataPill(value, type)`, the data-pill
  types, `TemplateValue`, `Duration`. Read when passing values between steps.
- **`references/actions-and-script-actions.md`** — the `action.core.*` catalog used by
  `wfa.action`, and standalone `ScriptAction` (event-driven server scripts). Read when
  adding a step or a script action.
- **`references/mapping-to-flow-designer.md`** — Fluent construct ↔ Flow Designer UI
  element table. Read when explaining code to a UI user or reverse-engineering a UI flow.

## Introspecting deployed flows (MCP — `servicenow_flows`)
Once a flow is deployed, inspect it on the instance with the `servicenow-api` MCP server.
Call as `servicenow_flows(action="...", params_json="{...}")` (JSON string). Env + tag
matrix: `agent-tools/mcp-client/references/servicenow-api.md`.

| Action | Purpose |
|--------|---------|
| `workflow_to_mermaid` | Render a deployed flow/workflow as a mermaid diagram (visualize/verify structure). |
| `collect_graph_for_roots` | Collect the full flow graph starting from one or more root flow sys_ids (dependencies/subflow tree). |
| `get_flow_metadata` | Fetch a flow's metadata (name, trigger, table, state) by sys_id. |

Use these to confirm a deployed flow matches the authored Fluent, or to understand an
existing UI-built flow before converting it to code.

## Gotchas
- **`$id` is identity.** A stable `$id` (`Now.ID[...]` or an explicit sys_id) makes a
  re-deploy *update* the same flow/step; changing it creates a duplicate.
- Trigger outputs are only reachable via `params.trigger.*`; action outputs via the
  variable you bound the `wfa.action(...)` call to (e.g. `const x = wfa.action(...)` →
  `x.Record.field`).
- Values crossing step boundaries must be wrapped as **data pills** — a bare
  `params.trigger.field` won't bind correctly (see `data-pills-and-values.md`).
- Authoring here does not deploy — build/install via `servicenow-sdk-lifecycle`.
