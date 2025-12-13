#!/bin/sh
set -e

# Default command logic:
# 1. Use CMD environment variable if set (allows via docker run -e CMD=...)
# 2. Else use first argument (allows via docker run image command ...)
# 3. Default to servicenow-mcp (set in Dockerfile CMD, so $1 is usually this if no args)

# If default CMD (servicenow-mcp) is passed and we have an env override, ignore the argument
if [ -n "$CMD" ] && [ "$1" = "servicenow-mcp" ]; then
    shift
fi

COMMAND="${CMD:-$1}"

# If COMMAND starts with -, assume it's flags for the default tool (servicenow-mcp)
if [ "${COMMAND#-}" != "$COMMAND" ]; then
    COMMAND="servicenow-mcp"
    # Don't shift, keep the flag in $@ (Wait, if COMMAND was $1, we need to not shift it out? Or explicitly set it?)
    # If COMMAND was detected from $1 (which was --help), and we set COMMAND=servicenow-mcp.
    # We want subsequent logic to see $1 as --help.
    # So we should NOT shift if we detected a flag.
else
    # If we are taking the command from $1, shift it.
    if [ -z "$CMD" ]; then
        shift
    fi
fi

if [ "$COMMAND" = "servicenow-mcp" ]; then
    exec servicenow-mcp \
    --transport "${TRANSPORT}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --auth-type "${AUTH_TYPE}" \
    $( [ -n "${TOKEN_JWKS_URI}" ] && echo "--token-jwks-uri ${TOKEN_JWKS_URI}" ) \
    $( [ -n "${TOKEN_ISSUER}" ] && echo "--token-issuer ${TOKEN_ISSUER}" ) \
    $( [ -n "${TOKEN_AUDIENCE}" ] && echo "--token-audience ${TOKEN_AUDIENCE}" ) \
    $( [ -n "${TOKEN_ALGORITHM}" ] && echo "--token-algorithm ${TOKEN_ALGORITHM}" ) \
    $( [ -n "${TOKEN_SECRET}" ] && echo "--token-secret ${TOKEN_SECRET}" ) \
    $( [ -n "${TOKEN_PUBLIC_KEY}" ] && echo "--token-public-key ${TOKEN_PUBLIC_KEY}" ) \
    $( [ -n "${REQUIRED_SCOPES}" ] && echo "--required-scopes ${REQUIRED_SCOPES}" ) \
    $( [ -n "${OAUTH_UPSTREAM_AUTH_ENDPOINT}" ] && echo "--oauth-upstream-auth-endpoint ${OAUTH_UPSTREAM_AUTH_ENDPOINT}" ) \
    $( [ -n "${OAUTH_UPSTREAM_TOKEN_ENDPOINT}" ] && echo "--oauth-upstream-token-endpoint ${OAUTH_UPSTREAM_TOKEN_ENDPOINT}" ) \
    $( [ -n "${OAUTH_UPSTREAM_CLIENT_ID}" ] && echo "--oauth-upstream-client-id ${OAUTH_UPSTREAM_CLIENT_ID}" ) \
    $( [ -n "${OAUTH_UPSTREAM_CLIENT_SECRET}" ] && echo "--oauth-upstream-client-secret ${OAUTH_UPSTREAM_CLIENT_SECRET}" ) \
    $( [ -n "${OAUTH_BASE_URL}" ] && echo "--oauth-base-url ${OAUTH_BASE_URL}" ) \
    $( [ -n "${OIDC_CONFIG_URL}" ] && echo "--oidc-config-url ${OIDC_CONFIG_URL}" ) \
    $( [ -n "${OIDC_CLIENT_ID}" ] && echo "--oidc-client-id ${OIDC_CLIENT_ID}" ) \
    $( [ -n "${OIDC_CLIENT_SECRET}" ] && echo "--oidc-client-secret ${OIDC_CLIENT_SECRET}" ) \
    $( [ -n "${OIDC_BASE_URL}" ] && echo "--oidc-base-url ${OIDC_BASE_URL}" ) \
    $( [ -n "${REMOTE_AUTH_SERVERS}" ] && echo "--remote-auth-servers ${REMOTE_AUTH_SERVERS}" ) \
    $( [ -n "${REMOTE_BASE_URL}" ] && echo "--remote-base-url ${REMOTE_BASE_URL}" ) \
    $( [ -n "${ALLOWED_CLIENT_REDIRECT_URIS}" ] && echo "--allowed-client-redirect-uris ${ALLOWED_CLIENT_REDIRECT_URIS}" ) \
    $( [ -n "${EUNOMIA_TYPE}" ] && echo "--eunomia-type ${EUNOMIA_TYPE}" ) \
    $( [ -n "${EUNOMIA_POLICY_FILE}" ] && echo "--eunomia-policy-file ${EUNOMIA_POLICY_FILE}" ) \
    $( [ -n "${EUNOMIA_REMOTE_URL}" ] && echo "--eunomia-remote-url ${EUNOMIA_REMOTE_URL}" ) \
    $( [ -n "${OPENAPI_FILE}" ] && echo "--openapi-file ${OPENAPI_FILE}" ) \
    $( [ -n "${ENABLE_DELEGATION}" ] && echo "--enable-delegation" ) \
    $( [ -n "${SERVICENOW_AUDIENCE}" ] && echo "--audience ${SERVICENOW_AUDIENCE}" ) \
    $( [ -n "${DELEGATED_SCOPES}" ] && echo "--delegated-scopes ${DELEGATED_SCOPES}" ) \
    "$@"

elif [ "$COMMAND" = "servicenow-a2a" ]; then
    # shift 1 # Already shifted
    exec servicenow-a2a \
        --host "${HOST}" \
        --port "${PORT}" \
        $( [ -n "${PROVIDER}" ] && echo "--provider ${PROVIDER}" ) \
        $( [ -n "${MODEL_ID}" ] && echo "--model-id ${MODEL_ID}" ) \
        $( [ -n "${BASE_URL}" ] && echo "--base-url ${BASE_URL}" ) \
        $( [ -n "${API_KEY}" ] && echo "--api-key ${API_KEY}" ) \
        $( [ -n "${MCP_URL}" ] && echo "--mcp-url ${MCP_URL}" ) \
        "$@"

else
    # Allow running arbitrary commands
    exec "$COMMAND" "$@"
fi
