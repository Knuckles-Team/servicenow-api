import os
import requests
import threading
from fastmcp.server.middleware import MiddlewareContext, Middleware
from fastmcp.utilities.logging import get_logger
from servicenow_api.servicenow_api import Api
from servicenow_api.utils import to_boolean

local = threading.local()
logger = get_logger(name="TokenMiddleware")


class UserTokenMiddleware(Middleware):
    def __init__(self, config: dict):
        self.config = config

    async def on_request(self, context: MiddlewareContext, call_next):
        logger.debug(f"Delegation enabled: {self.config['enable_delegation']}")
        if self.config["enable_delegation"]:
            headers = getattr(context.message, "headers", {})
            auth = headers.get("Authorization")
            if auth and auth.startswith("Bearer "):
                token = auth.split(" ")[1]
                local.user_token = token
                local.user_claims = None

                if hasattr(context, "auth") and hasattr(context.auth, "claims"):
                    local.user_claims = context.auth.claims
                    logger.info(
                        "Stored JWT claims for delegation",
                        extra={"subject": context.auth.claims.get("sub")},
                    )
                else:
                    logger.debug("JWT claims not yet available (will be after auth)")

                logger.info("Extracted Bearer token for delegation")
            else:
                logger.error("Missing or invalid Authorization header")
                raise ValueError("Missing or invalid Authorization header")
        return await call_next(context)


class JWTClaimsLoggingMiddleware(Middleware):
    async def on_response(self, context: MiddlewareContext, call_next):
        response = await call_next(context)
        logger.info(f"JWT Response: {response}")
        if hasattr(context, "auth") and hasattr(context.auth, "claims"):
            logger.info(
                "JWT Authentication Success",
                extra={
                    "subject": context.auth.claims.get("sub"),
                    "client_id": context.auth.claims.get("client_id"),
                    "scopes": context.auth.claims.get("scope"),
                },
            )


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

    if username or password:
        return Api(
            url=instance,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            verify=verify,
        )

    raise ValueError(
        "No auth method: Provide token, enable delegation, or set SERVICENOW_USERNAME/PASSWORD"
    )
