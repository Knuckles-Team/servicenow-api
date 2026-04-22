import os
from threading import local

import requests
from agent_utilities.base_utilities import get_logger, to_boolean
from agent_utilities.exceptions import AuthError, UnauthorizedError

from servicenow_api.api_wrapper import Api

local = local()
logger = get_logger(__name__)


def get_client(
    username=os.getenv("SERVICENOW_USERNAME", None),
    password=os.getenv("SERVICENOW_PASSWORD", None),
    client_id=os.getenv("SERVICENOW_CLIENT_ID", None),
    client_secret=os.getenv("SERVICENOW_CLIENT_SECRET", None),
    verify: bool = to_boolean(string=os.getenv("SERVICENOW_SSL_VERIFY", "True")),
) -> Api:
    """
    Single entry point for ServiceNow clients.

    Auto-detects auth method:
    1. Delegation → Exchanges MCP token
    2. Basic auth → username/password (env fallback)
    """
    config = {
        "enable_delegation": to_boolean(os.environ.get("ENABLE_DELEGATION", "False")),
        "audience": os.environ.get("SERVICENOW_AUDIENCE", None),
        "delegated_scopes": os.environ.get("DELEGATED_SCOPES", "api"),
        "token_endpoint": None,
        "oidc_client_id": os.environ.get("OIDC_CLIENT_ID", None),
        "oidc_client_secret": os.environ.get("OIDC_CLIENT_SECRET", None),
        "oidc_config_url": os.environ.get("OIDC_CONFIG_URL", None),
        "jwt_jwks_uri": os.getenv("FASTMCP_SERVER_AUTH_JWT_JWKS_URI", None),
        "jwt_issuer": os.getenv("FASTMCP_SERVER_AUTH_JWT_ISSUER", None),
        "jwt_audience": os.getenv("FASTMCP_SERVER_AUTH_JWT_AUDIENCE", None),
        "jwt_algorithm": os.getenv("FASTMCP_SERVER_AUTH_JWT_ALGORITHM", None),
        "jwt_secret": os.getenv("FASTMCP_SERVER_AUTH_JWT_PUBLIC_KEY", None),
        "jwt_required_scopes": os.getenv(
            "FASTMCP_SERVER_AUTH_JWT_REQUIRED_SCOPES", None
        ),
    }
    instance = os.getenv("SERVICENOW_INSTANCE")
    if not instance:
        raise RuntimeError("SERVICENOW_INSTANCE not set")

    mcp_token = getattr(local, "user_token", None)

    if config.get("enable_delegation", False) and mcp_token:
        logger.info("Delegating MCP token to ServiceNow")
        exchange_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": mcp_token,
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "audience": config["audience"],
            "scope": config["delegated_scopes"],
        }
        try:
            resp = requests.post(
                config["token_endpoint"],
                data=exchange_data,
                auth=(config["oidc_client_id"], config["oidc_client_secret"]),
                verify=verify,
            )
            resp.raise_for_status()
            sn_token = resp.json()["access_token"]
            return Api(url=instance, token=sn_token, verify=verify)
        except Exception as e:
            print(f"Delegation failed: {e}")
            logger.error("Delegation failed", extra={"error": str(e)})
            raise

    try:
        if username or password:
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
