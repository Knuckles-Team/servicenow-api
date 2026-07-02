# Integrated Risk Management (IRM / GRC)

> Product reference (concepts, not code). Sources:
> - Product page — https://www.servicenow.com/products/integrated-risk-management.html
> - GRC docs (Governance, Risk, and Compliance) — https://www.servicenow.com/docs/r/governance-risk-compliance/
> - Metrics in IRM — https://www.servicenow.com/docs/r/governance-risk-compliance/grc-risk-management-workspace/using-metrics-in-irm.html
> - GRC IRM knowledge & troubleshooting — https://www.servicenow.com/community/grc-articles/grc-integrated-risk-management-knowledge-amp-troubleshooting/ta-p/3133662
>
> For execution against IRM tables via MCP, see the sibling `servicenow-irm-grc` skill.

## What it is

**Integrated Risk Management (IRM)** — historically branded **GRC (Governance, Risk,
and Compliance)** — is ServiceNow's suite for identifying, assessing, and managing risk
and compliance across the enterprise on the Now Platform. It centralizes risk activity
and drives it with automated workflows so organizations can make informed decisions,
address risk proactively, and stay compliant with regulations. It is ServiceNow's
counterpart to tools like RSA Archer (GRC) and OneTrust (privacy).

## The GRC / IRM applications

- **GRC: Policy and Compliance Management** — author and publish policies; define
  authoritative sources, citations, and controls; run control attestation and manage
  compliance by control state; handle policy exceptions.
- **GRC: Risk Management** — the risk register and lifecycle: identify risks, assess
  impact and likelihood, respond, and monitor over time with **indicators**.
- **GRC: Advanced Risk** — advanced/quantitative risk assessments and methodologies.
- **GRC: Profiles** — the **entity / profile framework** that scopes risks, controls,
  and compliance to organizational entities (business units, assets, processes).
- **Vendor Risk Management / Third-Party Risk Management (TPRM)** — assess and monitor
  third-party/vendor risk; run the vendor-assessment queue.
- **Operational Risk Management** and **Privacy Management** — operational risk and
  data-privacy (processing activities, data-subject records) modules.
- **Audit Management** — plan and execute audits; manage engagements, findings, and
  remediation.

## Core concepts

- **Entity / Profile framework** — the backbone: entities are profiled, and risks,
  controls, and compliance requirements are attached to them.
- **Risk lifecycle** — identify → assess (impact × likelihood) → respond → monitor.
  Response strategies include **accept, mitigate, share (transfer), or decline/avoid**.
- **Controls & control attestation** — controls implement policy/compliance
  requirements; their state is attested and rolled up into compliance posture.
- **Indicators / continuous monitoring** — automated indicators continuously test
  controls and risks, surfacing exposures without manual review.
- **Policy lifecycle** — draft → review → publish policies mapped to authoritative
  sources and citations; request and track exceptions.
- **Metrics & workspaces** — role-based workspaces (e.g., Risk Management Workspace)
  present metrics, roll-ups, and dashboards for risk/compliance/audit.

## Platform / integration notes

- IRM/GRC modules are **scoped applications** (tables commonly under `sn_risk_*`,
  `sn_compliance_*`, `sn_audit_*`, `sn_vdr_*` / vendor-risk scopes). Exact tables and
  fields vary by installed plugin and release — confirm against the target instance.
- IRM has **no dedicated REST API family**; it is driven table-first via the generic
  Table / Aggregate APIs (see `servicenow-table-api` and `servicenow-irm-grc`).
- IRM consumes the automation layer (Flow Designer / Workflow Studio) for attestation
  campaigns, assessment routing, and risk-response workflows, and connects to the CMDB
  for entity/asset context.

## How it fits the Now Platform

IRM is the platform's **risk & compliance layer**. It shares the data model (CMDB
entities, control/risk records), the automation layer (flows), and platform governance
with the rest of the Now Platform, and integrates closely with SecOps (security risk /
findings feeding operational and IT risk).
