# Configuration, trust, and privacy

This page is the operator contract for `servicenow-api`. Package-specific endpoint,
authentication, tool-toggle, and model settings remain documented in the
repository README and the installed command's `--help` output. Runtime values
must be injected by the launcher; they do not belong in source, packaged skill
content, traces, or generated reports.

## Capability configuration

The current capability surface is defined by three versioned artifacts:

- the action-routed MCP tools described in the README and `docs/usage.md`;
- the compact canonical skill plus any specialist `WORKFLOW.md` procedures;
- `connector_manifest.yml` and its ontology, mappings, shapes, fixtures,
  migrations, tool-schema fingerprints, and certification metadata.

Treat those artifacts as a unit during release and deployment. Do not enable a
skill whose certification or tool-schema fingerprint does not match the
installed package. Use the compact/intent-oriented tool surface for delegated
agents; expose verbose per-operation tools only for compatibility or debugging.

## Runtime values and secrets

- Supply service endpoints, tenant identifiers, credentials, and model keys
  through environment variables or a mounted secret provider.
- Use non-personal agent aliases and opaque tenant/correlation identifiers.
- Keep developer directories, workstation names, and deployment hostnames out
  of checked-in configuration.
- Bind network transports to an explicitly chosen interface and require the
  deployment's MCP authentication policy before accepting remote traffic.
- Enable optional agent, embedding, evolution, or observability features only
  when their dependencies and backends are configured and healthy.

The checked-in examples use `localhost` for loopback-only development and
`example.invalid` for replaceable network endpoints. Neither value is a
production default.

## TLS trust

Certificate verification is required. For a private certificate authority,
mount a PEM bundle containing the required intermediate and root certificates,
then configure the client environment with `SSL_CERT_FILE` and, for
Requests-compatible clients, `REQUESTS_CA_BUNDLE`. When `uvx` must use the
native platform trust store while resolving packages, set `UV_NATIVE_TLS=true`.

Do not disable verification to work around an incomplete server chain. Keep CA
bundle locations environment-configured and stable for the runtime; never embed
a workstation path or certificate material in MCP configuration.

## Privacy and data governance

The default observability posture is metadata-only. Do not persist prompts,
message bodies, tool inputs/results, document content, raw traces, credentials,
local paths, hostnames, or personal identity unless an approved data contract
explicitly requires it. Keep Langfuse or OTLP content capture disabled unless a
reviewed retention and access policy authorizes it.

When connector ingestion is enabled, each change must carry tenant, ACL,
classification, retention, provenance, and checkpoint/delta metadata. Reject or
quarantine records that cannot satisfy that contract; never silently widen a
tenant scope. Logs and reports should contain counts, status, and opaque
references only.

## Deployment verification

1. Validate the capability bundle and skill metadata against the installed tool
   schemas.
2. Confirm required secrets are present without printing their values.
3. Verify the complete TLS chain with certificate verification enabled.
4. Exercise health/readiness and one least-privilege read operation.
5. Confirm traces arrive under the expected opaque tenant/run identifiers and
   contain no captured content.
6. Record only sanitized pass/fail evidence and version identifiers.

## Staged ServiceNow validation campaign

The signed provider/package identity is `servicenow-api`; the deployed MCP
service identity is `servicenow-mcp`. Source-sync presets retain the signed
provider identity, and `servicenow_api.connectors.resolve_mcp_server()` maps the
deployed service identity to it at runtime. Unknown names fail closed.
Run the offline contract first with `python -c "from servicenow_api.validation_campaign import build_campaign; print(build_campaign()['status'])"`.
It neither loads credentials nor contacts ServiceNow.

The campaign is ordered and fail-closed:

1. Validate the signed provider bundle, tenant/ACL/provenance contract, every
   packaged skill, and both condensed and verbose MCP catalogs.
2. An operator verifies secret references (not values), TLS, MCP authentication,
   and performs one bounded least-privilege read.
3. Run bounded `source_sync` and repeat it to confirm the no-change path.
4. Review `graph_writeback` only with `dry_run=true`.
5. Any live mutation is a separately approved, reversible change; keep
   `SERVICENOW_ENABLE_WRITE` unset until that approval.

Materialization requires opaque `SERVICENOW_TENANT_REF` and
`SERVICENOW_ACL_REF` runtime references. Missing or unresolved tenant/ACL data
is a hard stop, never a fallback to a shared tenant.
