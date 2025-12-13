#!/bin/sh
set -e

# Default command logic:
# 1. Use CMD environment variable if set (allows via docker run -e CMD=...)
# 2. Else use first argument (allows via docker run image command ...)
# 3. Default to media-downloader-mcp (set in Dockerfile CMD, so $1 is usually this if no args)

COMMAND="${CMD:-$1}"

# If we are using the default from Dockerfile ($1) or an explicit argument, we shift it off
# If we are using ENV CMD, we still expect $1 to be the default "media-downloader-mcp" or empty, so shifting is generally safe if we assume standard usage.
# However, to be safe, if we are using ENV CMD, we might not want to consume $1 if $1 is actually flags meant for the command.
# But Docker CMD handling means if we pass args, they replace CMD.
# So if we use -e CMD=a2a, and run `docker run ...`, $1 IS "media-downloader-mcp". So we MUST shift.
# If user runs `docker run -e CMD=a2a image --flag`, then $1 is "--flag".
# Then COMMAND is a2a.
# If we shift, we lose --flag. This is BAD.

# improved logic:
# If CMD env is set, use it.
# Check if $1 is "media-downloader-mcp" (the default). If so, shift it.
# If $1 is NOT "media-downloader-mcp" (e.g. it's "--flag" or another command):
#   If CMD env was set, we assume $1 are args FOR that command?
#   Or if $1 is a command, it conflicts?
# Let's assume -e CMD is used purely when NO args are passed (relying on default CMD).

if [ -n "$CMD" ]; then
    # Env var set.
    # If $1 is the default Dockerfile CMD, remove it.
    if [ "$1" = "media-downloader-mcp" ]; then
        shift 1
    fi
else
    # Env var not set. Use $1.
    COMMAND="$1"
    shift 1
fi

if [ "$COMMAND" = "media-downloader-mcp" ]; then
    exec media-downloader-mcp \
    --transport "${TRANSPORT}" \
    --host "${HOST}" \
    --port "${PORT}" \
    --auth-type "${AUTH_TYPE}" \
    $( [ -n "${TOKEN_JWKS_URI}" ] && echo "--token-jwks-uri ${TOKEN_JWKS_URI}" ) \
    $( [ -n "${TOKEN_ISSUER}" ] && echo "--token-issuer ${TOKEN_ISSUER}" ) \
    $( [ -n "${TOKEN_AUDIENCE}" ] && echo "--token-audience ${TOKEN_AUDIENCE}" ) \
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
    "$@"

elif [ "$COMMAND" = "media-downloader-a2a" ]; then
    # shift 1 # Already shifted
    exec media-downloader-a2a \
        --host "${HOST}" \
        --port "${PORT}" \
        $( [ -n "${PROVIDER}" ] && echo "--provider ${PROVIDER}" ) \
        $( [ -n "${MODEL_ID}" ] && echo "--model-id ${MODEL_ID}" ) \
        $( [ -n "${BASE_URL}" ] && echo "--base-url ${BASE_URL}" ) \
        $( [ -n "${API_KEY}" ] && echo "--api-key ${API_KEY}" ) \
        $( [ -n "${MCP_URL}" ] && echo "--mcp-url ${MCP_URL}" ) \
        $( [ -n "${ALLOWED_TOOLS}" ] && echo "--allowed-tools ${ALLOWED_TOOLS}" ) \
        "$@"

elif [ "$COMMAND" = "media-downloader" ]; then
    # shift 1 # Already shifted
    exec media-downloader "$@"
else
    # Allow running arbitrary commands
    exec "$COMMAND" "$@"
fi
