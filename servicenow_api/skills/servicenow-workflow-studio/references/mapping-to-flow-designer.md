# Mapping Fluent ↔ Flow Designer UI

The Fluent automation API is a 1:1 code representation of the Flow Designer canvas. Use
this table to explain code to a UI user, or to reverse-engineer a UI-built flow into code.

| Flow Designer UI | Fluent construct |
|------------------|------------------|
| A **Flow** (canvas with a trigger + steps) | `Flow({ $id, name, description }, wfa.trigger(...), (params) => {...})` |
| A **Subflow** (reusable, with Inputs/Outputs panel) | `Subflow({ $id, name, inputs, outputs, flowVariables }, (params) => {...})` |
| The **Trigger** card at the top | `wfa.trigger(trigger.<family>.<event>, { $id }, { config })` |
| Trigger's **table / condition** fields | `table` / `condition` in the trigger config |
| An **Action** step | `wfa.action(action.core.<name>, { $id, annotation }, { params })` |
| The step's **annotation / label** | `annotation` in the step metadata |
| **Data pills** dragged into a field | `wfa.dataPill(value, type)` |
| A field set from a record template | `TemplateValue({ field: value, ... })` |
| **If / Else If / Else** flow-logic blocks | `wfa.flowLogic.if / elseIf / else` |
| **For Each** loop | `wfa.flowLogic.forEach(collectionPill, { $id }, () => {...})` |
| **Wait for a duration/condition** | `action.core.waitForCondition` + `Duration({...})` / `slaPercentageTimer` |
| **End Flow** | `wfa.flowLogic.endFlow({ $id })` |
| **Set Subflow Outputs** (return values) | `wfa.flowLogic.assignSubflowOutputs({ $id }, params.outputs, {...})` |
| Trigger outputs in the pill picker | `params.trigger.*` |
| A prior step's outputs in the pill picker | the variable bound to that `wfa.action(...)` (`.Record` / `.Records` / `.record`) |
| A **Script Action** (Server → Script Actions) | `ScriptAction({ $id, name, eventName, script, ... })` (`sysevent_script_action`) |
| An **Application menu / module** exposing the flow | see `servicenow-app-engine` |

## Reverse-engineering a deployed flow
To go UI → code understanding, introspect the deployed flow with the `servicenow-api` MCP
server (`servicenow_flows`): `workflow_to_mermaid` to see the branch/step structure,
`collect_graph_for_roots` to map subflow/dependency trees, `get_flow_metadata` for the
trigger/table/state. Then re-express each node using the table above.

## Gotchas
- The **canvas order** of steps equals **source order** of `wfa.action` / `wfa.flowLogic`
  calls in the body — reorder in code to reorder on the canvas.
- The UI's "stage/annotation" text is the `annotation` field; keep it meaningful so the
  generated canvas is readable.
- A flow authored in code and one built in the UI are the same records on the instance —
  editing the same `$id`/sys_id from both sides will conflict; pick one source of truth.
