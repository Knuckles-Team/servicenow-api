"""ServiceNow Authentication Module.

Authentication priority:
1. **OIDC Delegation** — If ``ENABLE_DELEGATION`` is active, exchanges
   the IdP-issued user token for a downstream ServiceNow access token
   via RFC 8693 Token Exchange using ``agent_connector_sdk.auth.delegation``.
2. **OAuth client credentials** — If ``SERVICENOW_GRANT_TYPE`` is
   ``client_credentials`` and ``SERVICENOW_CLIENT_ID`` /
   ``SERVICENOW_CLIENT_SECRET`` are set, authenticates as the OAuth
   application itself (no username/password).
3. **Basic Auth** — Falls back to ``SERVICENOW_USERNAME`` /
   ``SERVICENOW_PASSWORD`` with optional OAuth client credentials.
"""

import logging
from threading import local

from agent_connector_sdk.config import setting
from agent_connector_sdk.exceptions import AuthError, UnauthorizedError
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile

local = local()
from servicenow_api.api_client import Api

logger = logging.getLogger(__name__)


def _is_delegation_enabled() -> bool:
    """Whether the OIDC delegation path should be attempted."""
    from agent_connector_sdk.auth.delegation import DelegationSettings

    return DelegationSettings.from_settings().enabled


def _delegated_client(instance: str, profile: ResolvedTLSProfile) -> Api:
    """Path 1: OIDC Delegation (RFC 8693 Token Exchange).

    Reads delegation settings (``OIDC_TOKEN_URL``/``OIDC_CLIENT_ID``/
    ``OIDC_CLIENT_SECRET_REF``/``AUDIENCE``/``DELEGATED_SCOPES``) from the
    process settings via ``agent_connector_sdk.auth.delegation.DelegationSettings``.
    """
    import httpx
    from agent_connector_sdk.auth.delegation import (
        DelegationSettings,
        current_user_token,
        exchange_token,
    )
    from agent_connector_sdk.exceptions import LoginRequiredError

    try:
        settings = DelegationSettings.from_settings()
        subject_token = current_user_token()
        if not subject_token:
            raise LoginRequiredError("no verified caller token to delegate")
        with httpx.Client(timeout=30) as http_client:
            access_token = exchange_token(
                settings, subject_token=subject_token, http_client=http_client
            )
        logger.info("Using OIDC delegated token for ServiceNow API")
        return Api(url=instance, token=access_token.value, tls_profile=profile)
    except Exception as e:
        logger.error("OIDC delegation failed", extra={"error": "Operation failed"})
        raise RuntimeError(f"Token exchange failed: {type(e).__name__}") from e


def get_client(
    username=None,
    password=None,
    client_id=None,
    client_secret=None,
    tls_profile: ResolvedTLSProfile | None = None,
) -> Api:
    """Single entry point for ServiceNow clients.

    Credentials resolve live through the shared config layer (the one XDG
    ``config.json`` / env), so they are read at call time rather than frozen at
    import. Auto-detects auth method:
    1. OIDC Delegation → exchanges MCP token via the SDK's delegation helper
    2. OAuth client credentials → application credentials
    3. Basic auth → username/password (config fallback)
    """
    username = username if username is not None else setting("SERVICENOW_USERNAME")
    password = password if password is not None else setting("SERVICENOW_PASSWORD")
    client_id = client_id if client_id is not None else setting("SERVICENOW_CLIENT_ID")
    client_secret = (
        client_secret
        if client_secret is not None
        else setting("SERVICENOW_CLIENT_SECRET")
    )
    profile = tls_profile or resolve_tls_profile(
        "servicenow",
        profile_name=setting("SERVICENOW_TLS_PROFILE", "") or None,
        profile_ref=setting("SERVICENOW_TLS_PROFILE_REF", "") or None,
    )

    instance = setting("SERVICENOW_URL") or setting("SERVICENOW_INSTANCE")
    if not instance:
        raise RuntimeError("SERVICENOW_INSTANCE not set")

    # --- Path 1: OIDC Delegation (RFC 8693 Token Exchange) ---
    if _is_delegation_enabled():
        return _delegated_client(instance, profile)

    # --- Path 2: OAuth 2.0 client credentials grant ---
    # Set SERVICENOW_GRANT_TYPE=client_credentials to authenticate as an OAuth
    # application (client_id/client_secret) with no username/password — e.g. an
    # integration account backed by an OAuth application registration.
    grant_type = setting("SERVICENOW_GRANT_TYPE", "password")
    if grant_type == "client_credentials":
        if not client_id or not client_secret:
            raise ValueError(
                "OAuth client_credentials requires client_id and client_secret"
            )
        logger.info("Using OAuth client_credentials credentials for ServiceNow API")
        return Api(
            url=instance,
            client_id=client_id,
            client_secret=client_secret,
            grant_type="client_credentials",
            tls_profile=profile,
        )

    # --- Path 3: Basic Auth (username/password + optional OAuth client) ---
    try:
        if username or password:
            logger.info("Using username/password credentials for ServiceNow API")
            return Api(
                url=instance,
                username=username,
                password=password,
                client_id=client_id,
                client_secret=client_secret,
                tls_profile=profile,
            )
    except (AuthError, UnauthorizedError) as e:
        logger.error("Operation failed: error_type=%s", type(e).__name__)
        raise RuntimeError(
            "AUTHENTICATION ERROR: The ServiceNow credentials provided are not valid for the account used. "
            "Please check your SERVICENOW_USERNAME and SERVICENOW_PASSWORD environment variables, "
            "or verify your OAuth client configuration if applicable."
        ) from e

    raise ValueError(
        "No auth method: Provide token, enable delegation, set "
        "SERVICENOW_GRANT_TYPE=client_credentials with client_id/secret, or set "
        "SERVICENOW_USERNAME/PASSWORD"
    )
