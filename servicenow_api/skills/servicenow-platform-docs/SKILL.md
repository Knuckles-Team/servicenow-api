---
name: servicenow-platform-docs
description: >-
  ServiceNow PRODUCT documentation (concepts, not code) for the Now Platform
  build/automation and security/risk suites the fleet unifies: Flow Designer /
  Workflow Studio (no-code automation), App Engine Studio / Application Studio
  (low-code app building), Integrated Risk Management (IRM/GRC — risk, policy &
  compliance, audit, vendor/TPRM, privacy), and Security Operations (SecOps —
  Security Incident Response, Vulnerability Response, Threat Intelligence). Use
  when the agent needs to understand what these products are, their core
  concepts, component/table vocabulary, and how they fit together on the Now
  Platform. Read reference/flow-designer.md, app-engine-studio.md, irm-grc.md,
  or secops.md, and OVERVIEW.md first for the cross-cutting map. Do NOT use for
  ServiceNow SDK / Fluent (now-sdk) TypeScript syntax or the metadata-as-code
  toolchain — use servicenow-sdk-docs for code. Do NOT use for Table API CRUD
  (servicenow-table-api) or execution-oriented IRM/SecOps MCP table skills.
license: MIT
tags: [servicenow, docs, flow-designer, app-engine-studio, irm, grc, secops, skill-graph, reference]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Platform Product Docs (Flow Designer, App Engine Studio, IRM/GRC, SecOps)

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

## Reference index (open the file for the area you need)

| Area | File | Read it for |
|------|------|-------------|
| Flow Designer / Workflow Studio | [`reference/flow-designer.md`](reference/flow-designer.md) | No-code automation: flows, subflows, actions, triggers, flow logic, decision tables, data pills, spokes / IntegrationHub |
| App Engine Studio / Application Studio | [`reference/app-engine-studio.md`](reference/app-engine-studio.md) | Low-code app building: scoped apps, tables, forms, experiences/UI, flows, App Engine Management Center (AEMC), citizen-developer roles |
| Integrated Risk Management (IRM/GRC) | [`reference/irm-grc.md`](reference/irm-grc.md) | Risk Management, Policy & Compliance, Audit, Vendor/TPRM, Privacy — the GRC suite, entity/profile framework, controls & indicators |
| Security Operations (SecOps) | [`reference/secops.md`](reference/secops.md) | Security Incident Response, Vulnerability Response, Configuration Compliance, Threat Intelligence — the SOAR engine on the Now Platform |

See [`OVERVIEW.md`](OVERVIEW.md) for the one-page cross-cutting map, and
[`index.json`](index.json) / [`sources.json`](sources.json) for the machine-readable
navigation and provenance/freshness manifests.

## Freshness note

ServiceNow docs are release-bundled (…Washington DC, Xanadu, Yokohama, Zurich…). The
cited pages here were captured from recent bundles (mostly **Zurich** build/app-dev,
some **Xanadu**). Concepts are stable across releases; exact UI labels and table
availability vary by release and installed plugin. Always confirm against the live
`https://www.servicenow.com/docs/` bundle for the target instance's release.
