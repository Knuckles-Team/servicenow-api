"""Connector provider metadata and deployment-name resolution.

The provider identity is part of the signed connector contract.  Deployment
service names are operational aliases and must resolve to it, never replace it.
"""

CANONICAL_PROVIDER = "servicenow-api"
DEPLOYED_MCP_SERVICE = "servicenow-mcp"


def resolve_mcp_server(name: str) -> str:
    """Resolve the deployed MCP service name to the signed provider identity.

    Unknown values are rejected so an accidental server-name typo cannot select a
    different source connector or bypass the provider/manifest gate.
    """
    if name in {CANONICAL_PROVIDER, DEPLOYED_MCP_SERVICE}:
        return CANONICAL_PROVIDER
    raise ValueError(f"unknown ServiceNow MCP server identity: {name!r}")
