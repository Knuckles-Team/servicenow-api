# Flow Designer / Workflow Studio

> Product reference (concepts, not code). Sources:
> - Flow Designer overview — https://www.servicenow.com/docs/bundle/zurich-build-workflows/page/administer/flow-designer/concept/flow-designer.html
> - Architecture overview — https://www.servicenow.com/docs/bundle/zurich-build-workflows/page/administer/flow-designer/concept/flow-designer-arch-overview.html
> - Workflow Studio — https://www.servicenow.com/docs/r/zurich/build-workflows/workflow-studio/workflow-studio.html
> - Product page — https://www.servicenow.com/products/platform-flow-designer.html

## What it is

**Flow Designer** lets you create end-to-end digital workflows on the Now Platform in a
**no-code / low-code** environment. You build automation visually — no scripting
required for common cases — and view complex structured data in a graphical interface.

**Workflow Studio** is the newer, centralized automation hub (introduced through the
Washington DC → Zurich releases) that brings flows, subflows, actions, decision tables,
and integrations into a single, cohesive design surface. It supersedes the older
standalone Flow Designer UI and the legacy Workflow (`wf_workflow`) engine as the
recommended way to author automation, while surfacing the same underlying flow engine.

## Core building blocks

- **Flow** — the primary, executable automation unit: a trigger plus an ordered
  sequence of actions and flow-logic steps. Flows run when their trigger fires.
- **Subflow** — a reusable flow segment invoked from a parent flow (modular design).
  Supports standard and conversational modes.
- **Action** — an individual automation step (create/update a record, send email, call
  a REST endpoint, etc.). Actions are pre-built or custom-authored in the **Action
  Designer**, and can be packaged for reuse.
- **Trigger** — what initiates a flow. Trigger types include:
  - **Record-based** — on insert / update / delete of a record.
  - **Scheduled** — time-based (daily, weekly, cron-like).
  - **Application / external events** — including inbound email and message-bus events.
  - **Service Catalog** — a catalog item request kicks off a flow.
  - **SLA / conversational / other** application-specific triggers.

## Flow logic and data

- **Flow Logic** — control-flow constructs that manage execution paths: conditional
  branching (**If / Else**), loops (**For Each**, **Do Until**), **parallel** execution,
  error handling (**Try / Catch**-style blocks), and wait/timer steps.
- **Decision Tables** — rules-based logic evaluated without scripting; map input
  conditions to outputs for complex conditional scenarios.
- **Data Pills** — dynamic values surfaced from the trigger, prior steps, or flow
  variables, drag-mapped into later steps to pass data through the flow.

## Integration

- **Spokes** — packaged integration connectors that bundle domain-specific actions
  (e.g., ITSM, Field Service, Customer Service, Microsoft, Slack). Spokes are part of
  **IntegrationHub**.
- **Spoke Generator** — builds custom spokes from OpenAPI / Postman specifications so
  external APIs become drag-and-drop actions.
- **IntegrationHub** — the runtime/entitlement layer that executes spoke actions and
  outbound integrations from within flows.

## How it fits the Now Platform

Flow Designer / Workflow Studio is the platform's **automation layer**. Other products
(App Engine apps, IRM, SecOps) consume it: an App Engine app wires business logic as
flows; IRM uses flows/decision tables for control attestation and risk response; SecOps
uses flows and **playbooks** to orchestrate response. Flows execute on the same governed
platform (security, audit, update sets) as everything else.

## Notable capabilities

- Undo / Redo in the flow canvas (Washington DC+).
- Reusable actions and subflows; flow variables; test/execution details with per-step
  state for debugging.
- Domain separation and multi-step approval patterns supported.
