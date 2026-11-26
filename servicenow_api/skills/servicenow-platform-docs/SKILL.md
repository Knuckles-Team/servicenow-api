---
name: servicenow-platform-docs
skill_type: skill
description: >-
  Product documentation (concepts, not code) for Flow Designer, App Engine
  Studio, IRM/GRC and SecOps on the Now Platform. Use to learn what these
  products are, their vocabulary and how they fit together. Do NOT use for
  now-sdk Fluent syntax (servicenow-sdk-docs), Table API CRUD (servicenow-
  table-api) or MCP table skills.
license: MIT
tags: [servicenow, docs, flow-designer, app-engine-studio, irm, grc, secops, skill-graph, reference]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow Platform Product Docs (Flow Designer, App Engine Studio, IRM/GRC, SecOps)

Scope: ServiceNow PRODUCT documentation (concepts, not code) for the Now Platform build/automation and security/risk suites the fleet unifies: Flow Designer / Workflow Studio (no-code automation), App Engine Studio / Application Studio (low-code app building), Integrated Risk Management (IRM/GRC — risk, policy and compliance, audit, vendor/TPRM, privacy), and Security Operations (SecOps — Security Incident Response, Vulnerability Response, Threat Intelligence). Use when the agent needs to understand what these products are, their core concepts, component/table vocabulary, and how they fit together on the Now Platform. Read references/flow-designer.md, app-engine-studio.md, irm-grc.md, or secops.md, and OVERVIEW.md first for the cross-cutting map. Do NOT use for ServiceNow SDK / Fluent (now-sdk) TypeScript syntax or the metadata-as-code toolchain — use servicenow-sdk-docs for code. Do NOT use for Table API CRUD (servicenow-table-api) or execution-oriented IRM/SecOps MCP table skills.

A **product-documentation** skill-graph (concepts and vocabulary, not code) for the
four Now Platform areas the fleet unifies. It complements the code-focused
`servicenow-sdk-docs` (Fluent / now-sdk TypeScript) — this graph answers *"what is
this product and how does it fit the platform?"*, not *"what is the SDK syntax?"*.

## When to use this vs. sibling skills

- **This skill (`servicenow-platform-docs`)** — orient on what Flow Designer / Workflow
  Studio, App Engine Studio, IRM/GRC, or SecOps *are*; their core concepts and
  component/table vocabulary; how the four fit together.
- **`servicenow-sdk-docs`** — ServiceNow SDK / Fluent (`now-sdk`) TypeScript syntax,
  decorators, metadata-as-code build/deploy toolchain. Go there for CODE.
- **`servicenow-table-api`** — generic Table API CRUD patterns.
- **`servicenow-irm-grc` / `servicenow-workflow-studio`** — execution-oriented MCP
  table skills for those specific suites.

## Steps

1. Open `references/OVERVIEW.md` first, and verify you can name which of the four product areas the question belongs to.
2. Open the matching file such as `references/flow-designer.md` or `references/secops.md`, and verify the concept appears in its headings.
3. Check `references/sources.json` for the source page and bundle release, and verify the release is noted before quoting details.
4. Route code or execution questions to `servicenow-sdk-docs` or `servicenow-irm-grc`, and verify the answer cites a page in these references rather than guessing.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Concept not found in the references | Topic belongs to another product area or is newer than the captured bundle | Search `references/index.json` for the area, and check the live product docs for the target release |
| Details differ on the instance | Release or plugin differences in UI labels and tables | Treat the references as concepts and confirm table names with `servicenow-table-api` on the instance |
| Needed code syntax missing | Question is about Fluent or now-sdk code | Switch to `servicenow-sdk-docs` and open the matching sample under its `references/` |

## Reference index (open the file for the area you need)

| Area | File | Read it for |
|------|------|-------------|
| Flow Designer / Workflow Studio | [`references/flow-designer.md`](references/flow-designer.md) | No-code automation: flows, subflows, actions, triggers, flow logic, decision tables, data pills, spokes / IntegrationHub |
| App Engine Studio / Application Studio | [`references/app-engine-studio.md`](references/app-engine-studio.md) | Low-code app building: scoped apps, tables, forms, experiences/UI, flows, App Engine Management Center (AEMC), citizen-developer roles |
| Integrated Risk Management (IRM/GRC) | [`references/irm-grc.md`](references/irm-grc.md) | Risk Management, Policy & Compliance, Audit, Vendor/TPRM, Privacy — the GRC suite, entity/profile framework, controls & indicators |
| Security Operations (SecOps) | [`references/secops.md`](references/secops.md) | Security Incident Response, Vulnerability Response, Configuration Compliance, Threat Intelligence — the SOAR engine on the Now Platform |

See [`OVERVIEW.md`](references/OVERVIEW.md) for the one-page cross-cutting map, and
[`index.json`](references/index.json) / [`sources.json`](references/sources.json) for the machine-readable
navigation and provenance/freshness manifests.

## Freshness note

ServiceNow docs are release-bundled (…Washington DC, Xanadu, Yokohama, Zurich…). The
cited pages here were captured from recent bundles (mostly **Zurich** build/app-dev,
some **Xanadu**). Concepts are stable across releases; exact UI labels and table
availability vary by release and installed plugin. Always confirm against the live
`https://www.servicenow.com/docs/` bundle for the target instance's release.
