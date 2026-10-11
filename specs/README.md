# servicenow-api specifications

These specs follow the ecosystem [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, extend an existing spec before creating one, audits and reviews land in the owning spec, one ID and title form, one file set. The `spec-standard` gate enforces it.

## Owner

This repository owns the specs with the ID prefix `CONN-SERVICENOW-API`. The connector contract, certification, and transport rules belong to [agent-connector-sdk](https://github.com/Knuckles-Team/agent-connector-sdk/tree/main/specs). The spec-delivery page rules belong to [pipelines](https://github.com/Knuckles-Team/pipelines/tree/main/specs).

## Add a spec

Read the existing specs first. Extend the spec that owns the behavior. Create a spec only for a capability that no spec owns. Copy [`_template/`](_template/) to `specs/<area>/`, set the ID to `CONN-SERVICENOW-API` or `CONN-SERVICENOW-API-<AREA>`, and add one index line below.

## Local specifications

This repository has no local spec yet.
