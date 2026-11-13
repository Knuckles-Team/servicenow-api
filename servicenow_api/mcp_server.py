import warnings

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass
warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")
import json
import sys
from threading import local

from scion_sdk.config import setting
from scion_sdk.mcp.concurrency import run_blocking
from scion_sdk.tls.resolve import resolve_tls_profile


def _delegation_enabled() -> bool:
    from scion_sdk.auth.delegation import DelegationSettings

    return DelegationSettings.from_settings().enabled


from servicenow_api.api_client import Api
from servicenow_api.auth import get_client

DEFAULT_SERVICENOW_USERNAME = setting("SERVICENOW_USERNAME", None)
DEFAULT_SERVICENOW_PASSWORD = setting("SERVICENOW_PASSWORD", None)
DEFAULT_SERVICENOW_CLIENT_ID = setting("SERVICENOW_CLIENT_ID", None)
DEFAULT_SERVICENOW_CLIENT_SECRET = setting("SERVICENOW_CLIENT_SECRET", None)


def register_misc_tools(mcp: FastMCP):
    @mcp.tool(tags={"kg_ingestion", "kg"})
    async def servicenow_ingest_incidents(
        params_json: str = Field(
            default="{}",
            description="JSON string of get_incidents filters (e.g. sysparm_limit, sysparm_query, sysparm_display_value).",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Natively ingest ServiceNow incidents into medulla as typed :Incident nodes.

        Lists incidents via the ServiceNow API and pushes them (with their affected
        :ConfigurationItem and :Person assignee, via :affects / :assignedTo links) into the
        knowledge graph through the fast engine client. Best-effort: returns
        ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        if ctx:
            await ctx.info("Ingesting ServiceNow incidents into the knowledge graph...")

        from scion_sdk.ingest import IngestError

        from servicenow_api.kg_ingest import ingest_incidents

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:
            return {"error": "Operation failed"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resp = await run_blocking(client.get_incidents, **kwargs)
        data = getattr(resp, "result", resp)
        records = data if isinstance(data, list) else [data]
        records = [r for r in records if r is not None]
        try:
            result = await ingest_incidents(records)
        except IngestError:
            return {"listed": len(records), "ingested": None}
        return {"listed": len(records), "ingested": result}


def _resolve_openapi_token_credential() -> str:
    """Resolve and return the incoming Bearer token for token-mode OpenAPI import."""
    token = getattr(local, "user_token", None)
    if not token:
        raise ValueError(
            "OpenAPI import requires --openapi-use-token and a valid Bearer token in the request"
        )
    print("Using incoming JWT for OpenAPI import", file=sys.stderr)
    return token


def _resolve_openapi_password_or_client_credential(
    args,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Resolve and return a username+password or client_id+client_secret pair."""
    username = args.openapi_username or setting("OPENAPI_USERNAME")
    password = args.openapi_password or setting("OPENAPI_PASSWORD")
    client_id = args.openapi_client_id or setting("OPENAPI_CLIENT_ID")
    client_secret = args.openapi_client_secret or setting("OPENAPI_CLIENT_SECRET")
    has_password_credential = bool(username and password)
    has_client_credential = bool(client_id and client_secret)
    if not has_password_credential and not has_client_credential:
        raise ValueError(
            "OpenAPI import requires either --openapi-use-token or (username+password) or (client_id+client_secret)"
        )
    return username, password, client_id, client_secret


def _resolve_openapi_credentials(
    args,
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    """Resolve the OpenAPI import auth credentials for ``args``; raises if none configured.

    Returns ``(token, username, password, client_id, client_secret)``. Token
    mode requires an incoming Bearer token, otherwise either a
    username+password or a client_id+client_secret pair must resolve (from
    the CLI args or the matching env/setting fallback).

    These are dedicated ``--openapi-*`` / ``OPENAPI_*`` credentials for the
    OpenAPI-import client, independent of the main ServiceNow client's
    ``SERVICENOW_*`` credentials used by ``get_client()``. WD5-FIX-03: before
    this fix, this function only validated presence — the resolved values
    were never threaded into the OpenAPI import's ``httpx.AsyncClient``,
    which authenticated solely via ``get_client()``'s unrelated
    ``SERVICENOW_*``-derived headers. Callers must now pass the returned
    values into the ``Api``/``httpx.AsyncClient`` construction.
    """
    if args.openapi_use_token:
        return _resolve_openapi_token_credential(), None, None, None, None
    username, password, client_id, client_secret = (
        _resolve_openapi_password_or_client_credential(args)
    )
    return None, username, password, client_id, client_secret


def _build_openapi_client(args) -> Api:
    """Build the OpenAPI-import ``Api`` client from its own resolved credentials.

    WD5-FIX-03: previously the OpenAPI-import ``httpx.AsyncClient`` was built
    from the unrelated ``get_client()`` (the main ``SERVICENOW_*``-credentialed
    client), so the token/username/password/client_id/client_secret resolved
    by ``_resolve_openapi_credentials`` had zero effect on the outbound
    request. This builds a dedicated ``Api`` instance from those credentials
    instead.
    """
    token, username, password, client_id, client_secret = _resolve_openapi_credentials(
        args
    )
    instance = setting("SERVICENOW_URL") or setting("SERVICENOW_INSTANCE")
    if not instance:
        raise ValueError("SERVICENOW_INSTANCE not set")
    tls_profile = resolve_tls_profile(
        "servicenow",
        profile_name=setting("SERVICENOW_TLS_PROFILE", "") or None,
        profile_ref=setting("SERVICENOW_TLS_PROFILE_REF", "") or None,
    )
    return Api(
        url=instance,
        token=token,
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        tls_profile=tls_profile,
    )
