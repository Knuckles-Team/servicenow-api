# Security Operations (SecOps)

> Product reference (concepts, not code). Sources:
> - Product page — https://www.servicenow.com/products/security-operations.html
> - Exploring Security Operations — https://www.servicenow.com/docs/bundle/xanadu-security-management/page/product/security-operations/concept/understanding-secops.html
> - Security Management docs — https://www.servicenow.com/docs/r/security-operations/
> - SecOps Quick Start — https://www.servicenow.com/community/secops-articles/secops-quick-start-guide/ta-p/2966738

## What it is

**Security Operations (SecOps)** is ServiceNow's **SOAR** (Security Orchestration,
Automation, and Response) engine built on the Now Platform. It connects existing
security tools, brings their vulnerability and incident data into a structured response
engine, and uses intelligent workflows, automation, and a deep connection with IT to
prioritize and resolve threats based on the impact they pose to the organization. In
short: SecOps is the collaboration layer between security and IT operations, giving
security teams a governed platform to respond faster.

## Two broad categories

The SecOps applications and workflows fall into two groups:

1. **Managing your exposures** — anticipate, understand, and remediate vulnerabilities
   and misconfigurations (Vulnerability Response, Configuration Compliance).
2. **Managing enterprise security cases** — move quickly to resolve security incidents
   and workflow threat-intelligence cases (Security Incident Response, Threat
   Intelligence).

## Core applications

- **Security Incident Response (SIR)** — case management for security incidents:
  ingest alerts, triage, investigate, contain, and remediate; orchestrate response with
  **playbooks** and automation; coordinate with IT (change/incident) for remediation.
  Security incidents commonly live in the `sn_si_incident` scoped table.
- **Vulnerability Response (VR)** — ingests findings from vulnerability scanners,
  correlates them to CMDB configuration items, and prioritizes **vulnerable items** by
  business impact for remediation (typically `sn_vul_*` tables such as vulnerable
  items). Integrates with the CMDB and change management.
- **Configuration Compliance** — identifies and prioritizes misconfigurations from
  secure-configuration assessment (SCA) tools against policies/benchmarks.
- **Threat Intelligence** — manages threat-intel indicators (IoCs), enrichment, and
  threat-intel cases; supports **MITRE ATT&CK** mapping for adversary techniques.

## Key concepts

- **SOAR** — orchestration + automation + response as one engine on the Now Platform.
- **Playbooks** — guided, automated response processes (built on the automation layer /
  Flow Designer) that standardize investigation and remediation steps.
- **Integrations** — connects to SIEMs, EDR, vulnerability scanners, and threat-intel
  feeds; alerts/findings flow in and drive response.
- **CMDB connection** — vulnerable items and security incidents are correlated to
  configuration items so prioritization reflects real business impact.
- **IT collaboration** — deep link to ITSM (incident, problem, change) so security
  remediation runs through governed IT workflows.
- **MITRE ATT&CK** — technique/tactic mapping used for enrichment and response context.

## Platform / integration notes

- SecOps modules are **scoped applications** (tables commonly under `sn_si_*` for
  incident response and `sn_vul_*` for vulnerability response). Exact tables/fields vary
  by installed plugin and release — confirm against the target instance.
- Drive SecOps table access via the generic Table / Aggregate APIs; see the sibling
  execution skill `servicenow-secops` (if present) and `servicenow-table-api`.
- SecOps consumes Flow Designer / Workflow Studio for playbooks and orchestration, and
  overlaps with IRM (security risk / findings feeding operational and IT risk).

## How it fits the Now Platform

SecOps is the platform's **security response layer**: security tools feed it data, it
prioritizes against the CMDB, and it drives remediation through IT workflows — all on
the same governed platform as ITSM, App Engine apps, and IRM.
