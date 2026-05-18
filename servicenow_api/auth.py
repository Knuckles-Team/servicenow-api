"""ServiceNow Authentication Module.

Authentication priority:
1. **OIDC Delegation** — If ``ENABLE_DELEGATION`` is active, exchanges
   the IdP-issued user token for a downstream ServiceNow access token
   via RFC 8693 Token Exchange using the shared ``delegated_auth`` helper.
2. **Basic Auth** — Falls back to ``SERVICENOW_USERNAME`` /
   ``SERVICENOW_PASSWORD`` with optional OAuth client credentials.

See ``docs/guides/oauth_sso.md`` in agent-utilities for full details.
"""

import os
from threading import local

from agent_utilities.base_utilities import get_logger, to_boolean
from agent_utilities.core.exceptions import AuthError, UnauthorizedError

from servicenow_api.api_client import Api

local = local()
logger = get_logger(__name__)


def get_client(
    username=os.getenv("SERVICENOW_USERNAME", None),
    password=os.getenv("SERVICENOW_PASSWORD", None),
    client_id=os.getenv("SERVICENOW_CLIENT_ID", None),
    client_secret=os.getenv("SERVICENOW_CLIENT_SECRET", None),
    verify: bool = to_boolean(string=os.getenv("SERVICENOW_SSL_VERIFY", "True")),
) -> Api:
    """Single entry point for ServiceNow clients.

    Auto-detects auth method:
    1. OIDC Delegation → exchanges MCP token via shared helper
    2. Basic auth → username/password (env fallback)
    """
    from agent_utilities.mcp.delegated_auth import (
        get_delegated_token,
        get_user_identity,
        is_delegation_enabled,
    )

    instance = os.getenv("SERVICENOW_INSTANCE")
    if not instance:
        raise RuntimeError("SERVICENOW_INSTANCE not set")

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    if is_delegation_enabled():
        try:
            delegated_token = get_delegated_token(
                audience=os.environ.get("AUDIENCE", instance),
                scopes=os.environ.get("DELEGATED_SCOPES", "api"),
                verify=verify,
            )
            identity = get_user_identity()
            logger.info(
                "Using OIDC delegated token for ServiceNow API",
                extra={
                    "user_email": identity.get("email"),
                    "instance": instance,
                },
            )
            return Api(url=instance, token=delegated_token, verify=verify)
        except Exception as e:
            logger.error("OIDC delegation failed", extra={"error": str(e)})
            raise

    # --- Path 2: Basic Auth (username/password + optional OAuth client) ---
    try:
        if username or password:
            logger.info("Using username/password credentials for ServiceNow API")
            return Api(
                url=instance,
                username=username,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
                verify=verify,
            )
    except (AuthError, UnauthorizedError) as e:
        logger.error(f"ServiceNow authentication failed: {e}")
        raise RuntimeError(
            "AUTHENTICATION ERROR: The ServiceNow credentials provided are not valid for the account used. "
            "Please check your SERVICENOW_USERNAME and SERVICENOW_PASSWORD environment variables, "
            "or verify your OAuth client configuration if applicable."
        ) from e

    raise ValueError(
        "No auth method: Provide token, enable delegation, or set SERVICENOW_USERNAME/PASSWORD"
    )
