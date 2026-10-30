---
name: servicenow-api-development
skill_type: skill
domain: development
description: >-
  Develop, test, and publish the servicenow-api connector while preserving its
  typed ServiceNow clients, MCP surface, packaged content, spec evidence, and
  shared release gates.
license: MIT
tags: [servicenow-api, development, connector, testing, packaging, pages]
tier: repository
metadata:
  author: Repository Maintainers
  version: '0.1.0'
---

# servicenow-api development

This repository owns the ServiceNow API clients, connector mappings, MCP tools,
packaged prompts, skills, ontology, and connector identity. Shared transport,
MCP construction, release rendering, and delivery gates belong to
`scion-sdk` and `pipelines`; admission and durable graph state belong
to their owning repositories. Read `AGENTS.md` before changing code and keep
tenant identifiers, credentials, endpoints, and local paths out of source,
fixtures, logs, and skill content.

## Repository workflow

1. Start from a real worktree based on `origin/main` and identify the owning row
   under `specs/` before changing behavior. Generated `status.json` files are
   evidence and are never hand-edited.
2. Trace a changed request from its MCP registration through the typed client,
   authentication policy, response model, and connector mapping. Preserve the
   stable `servicenow-mcp` identity and the existing tool names.
3. Keep changes in this connector boundary. Use SDK transports, credential
   references, TLS policy, and governed request helpers rather than adding a
   second client or a local serving layer.
4. Use fake responses and task-local configuration in tests. Never call a live
   ServiceNow tenant or resolve a real secret from a local gate.

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver one small, reviewable change at a time.

- Name the owning requirement and the proof before editing. Find the row with
  `git grep -n "<term>" -- specs` and cite its ID in the commit trailer.
- Keep a slice to one connector concern: one client or mapping behavior, one
  test seam, one workflow repair, or one substantive skill. A capability owned
  by the SDK, Arbora, pipelines, or the knowledge graph belongs there instead.
- Before adding spec text, extend the existing owning spec. Audits and carry-overs
  land in that spec; they do not get a new directory. Run `pipelines-hook
  spec-status` to inspect generated evidence and never write `status.json` by hand.
- Reuse the existing `Api`, SDK client, authentication policy, MCP registration,
  ontology mappings, and package-data globs. A second implementation of a
  connector capability is a defect.
- Keep tests independent of a live tenant and credentials. Prove malformed
  input, refusal, transport failure, and successful response shapes through
  existing fakes when behavior changes.
- Put `Spec: <ID>` and the assisting agent trailer on consecutive lines in the
  final commit paragraph. Use `Spec: none (...)` for delivery wiring that is
  owned by the provider's `PIPE-CONNSPEC` rows.

## Setup and gates

Use the locked project environment when it is already available:

```bash
uv sync --locked
uvx pre-commit run --all-files
```

For focused feedback, run only the smallest affected test file with the locked
environment, for example:

```bash
uv run --frozen pytest -q tests/test_api_coverage.py
uv run --frozen pytest -q tests/test_ingest_sources.py
```

The canonical `.pre-commit-config.yaml` delegates connector-standard, secrets,
spec, tests-fast, and dependency-readiness checks to
`Knuckles-Team/pipelines` at `rev: main`. Keep those shared hooks intact and
fix their findings rather than bypassing them.

## Connector-specific checks

- Keep the REST and SDK clients, typed models, API operation registrations, and
  connector source mappings aligned with the packaged MCP surface.
- Validate configuration and authorization before provider requests; use
  governed SDK credential references and TLS verification, never literals or
  insecure fallbacks.
- Keep `servicenow_api/skills/`, prompts, ontology, mappings, and connector
  resources inside the existing package-data globs so wheels and source trees
  expose the same content.
- Use mocked table and API responses for local tests. Do not print tenant data,
  identifiers, tokens, raw responses, or private paths in test output.

## Spec delivery and Pages

The canonical Pages caller is `.github/workflows/pages.yml`. It publishes the
`docs` source, enables the version-1 dashboard from
`.github/spec-dashboard.json`, and runs on `workflow_dispatch` plus pushes that
change docs, `specs/**`, the dashboard config, or the caller. The shared
renderer owns the layout and writes `spec-delivery/snapshot.json`; generated
site output does not belong in this repository.

The Pages proof is complete only when a successful hosted run has `headSha`
equal to the source revision and the public snapshot returns HTTP 200 with the
ServiceNow connector records. Local YAML or Markdown checks prove wiring only.

## Release and landing discipline

If package content changes, bump the canonical project patch version and refresh
`uv.lock` in the same coherent release slice. The central workflow publishes
the wheel before rendering the connector image; preserve that order and leave
existing runtime images untouched. Before a push, inspect the complete diff,
stage only reviewed paths, and verify `git status --short` after each gate.
Never use `git stash`, `git add -A`, `git add .`, force-push, or claim a spec or
Pages row from a YAML marker alone.

## Safety

Never commit `.env` files, tokens, raw tenant identifiers, generated site
output, or inventory dumps. Preserve actor scoping, secret redaction,
destructive-operation guards, and bounded responses. Keep runtime behavior
unchanged when the work is only delivery wiring or packaged development
guidance.
