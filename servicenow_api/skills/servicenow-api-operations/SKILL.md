---
name: servicenow-api-operations
skill_type: skill
description: >-
  Operate the servicenow-api connector through its governed MCP and Arbora
  capabilities. Use for any ServiceNow read, change, automation, ingestion,
  troubleshooting or evidence request that needs routing to the right domain
  skill. Do NOT use for hand-editing connector code (servicenow-api-
  development).
---

# Servicenow Api Operations

Scope: Operate servicenow-api through its governed MCP and Arbora capabilities, including servicenow app engine, servicenow change management, servicenow cicd devops, servicenow cmdb, servicenow hr ppm, servicenow import attachment batch, servicenow incident management, servicenow irm grc, and related workflows. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.

Use the provider's governed MCP tools through Arbora delegation.

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the served tool list; never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Steps

1. Establish the session with the governed connection and call `servicenow_get_table` with `sysparm_limit` 1, and verify the response comes from the intended tenant.
2. List the served tools with the MCP `tools/list` call, and verify every tool name you plan to use appears in the result before building arguments.
3. Pick the domain skill from the catalog in `references/catalog.md` (for example `servicenow-table-api` or `servicenow-incident-management`) and verify its When to use section covers the request.
4. Run the read-only inspection call first, such as `servicenow_get_table` with `sysparm_limit` 1, and verify the response shape matches the fields you intend to change.
5. Execute the approved mutation with the matching typed tool, and verify the durable result by re-reading the record with `servicenow_get_table_record` and checking the trace entry.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Tool name missing from the served list | Stale tool name or the server exposes a different tag set | Re-run `tools/list`, use the exact served name, and consult `references/catalog.md` for the owning skill |
| Tenant or ACL state unknown | Session not established or role not granted | Stop and re-establish the verified session; treat the unknown state as a hard failure and do not guess |
| Mutation refused | Destructive or externally visible action without explicit approval | Present the impact summary and obtain explicit approval, then resubmit the call |

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
