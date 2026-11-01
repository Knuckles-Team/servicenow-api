# servicenow-api constitution

This repository inherits the [organization constitution](https://github.com/Knuckles-Team/pipelines/blob/main/.specify/memory/constitution.md) version 1.5.0. Every article of that constitution applies here. This file adds only the rules and limits of this repository. `.specify/templates/` is vended by pipelines; do not edit it.

**Inherits**: organization constitution v1.5.0 | **Version**: 1.0.0 | **Ratified**: 2026-11-01 | **Last amended**: 2026-11-01

## Organization standards

- [Spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, computed states, `Spec:` trailers.
- [Ecosystem boundaries](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md): which repository owns which requirement.
- [Wording standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ste.md): sentences of 20 words or fewer, with `must`, `should`, or `may`.

## Repository articles

### R-I. Connector scope

This repository owns the calls, mappings and MCP tools of one external system: Python ServiceNow API Wrapper. It depends on scion-sdk only and adds no store, no policy table and no second client of another connector.

**Enforced by:** `connector-standard` and the spec standard.

**Plan check:** Does the change stay inside this connector's one external system and reuse the SDK for shared capabilities?

## Repository limits

This repository sets no numeric limit of its own. It follows the organization limits table.

Amend this file in a reviewed change. State the impact in the pull request. When the organization constitution changes its version, update the **Inherits** line in the same change.
