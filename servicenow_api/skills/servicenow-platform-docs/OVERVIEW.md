# Overview — ServiceNow Platform Product Docs

One-page, LLM-oriented map of the four Now Platform product areas this skill-graph
covers, and how they fit together. This is **product reference** (concepts and
vocabulary), not code — for ServiceNow SDK / Fluent syntax use `servicenow-sdk-docs`.

## The four areas as platform layers

Everything below runs on **one governed Now Platform** (shared data model / CMDB,
security & ACLs, audit, update sets). The areas stack as layers:

| Layer | Product | What it does | Reference |
|-------|---------|--------------|-----------|
| Application-building | **App Engine Studio / Application Studio** | Low-code (AES) and pro-code (Studio) building of scoped apps: tables, forms, experiences, roles | `reference/app-engine-studio.md` |
| Automation | **Flow Designer / Workflow Studio** | No-code/low-code flows, subflows, actions, triggers, decision tables, spokes (IntegrationHub) | `reference/flow-designer.md` |
| Risk & compliance | **Integrated Risk Management (IRM/GRC)** | Risk register, policy & compliance, audit, vendor/TPRM, privacy — entity/profile framework, controls, indicators | `reference/irm-grc.md` |
| Security response | **Security Operations (SecOps)** | SOAR: Security Incident Response, Vulnerability Response, Configuration Compliance, Threat Intelligence | `reference/secops.md` |

## How they connect

- **App Engine** apps are the on-ramp for custom solutions; they compose the data layer
  (tables) and consume the **automation layer** for business logic.
- **Flow Designer / Workflow Studio** is the automation engine every other product uses:
  IRM builds attestation/assessment/risk-response flows; SecOps builds **playbooks** for
  investigation and remediation.
- **IRM** and **SecOps** overlap: security findings and incidents feed operational and IT
  risk; both correlate to the **CMDB** for business-impact context.
- **SecOps** links deeply to **ITSM** (incident/problem/change) so remediation runs
  through governed IT workflows.

## Vocabulary cheat-sheet

- Flow Designer: *flow, subflow, action, trigger, flow logic, decision table, data pill,
  spoke, IntegrationHub, Action Designer, Spoke Generator*.
- App Engine: *scoped app, namespace/scope, table/field, form/question, experience,
  playbook, App Engine Management Center (AEMC), citizen developer, update set,
  template, Now Assist*.
- IRM/GRC: *entity/profile framework, risk register, control, control attestation,
  indicator, policy/citation/authoritative source, exception, TPRM/vendor risk, audit
  engagement/finding*; scoped tables `sn_risk_* / sn_compliance_* / sn_audit_* / sn_vdr_*`.
- SecOps: *SOAR, security incident (SIR), vulnerable item (VR), Configuration
  Compliance, Threat Intelligence, playbook, MITRE ATT&CK, IoC*; scoped tables
  `sn_si_* / sn_vul_*`.

## Caveats

- Docs are **release-bundled** (…Xanadu, Yokohama, Zurich…). Concepts are stable; exact
  UI labels, table availability, and plugin scoping vary by release/plugin.
- Table names listed are the commonly-used scoped names; **confirm against the live
  instance** — do not assume availability. This graph does not fabricate API/field
  specifics beyond what the cited docs describe.
