FROM python:3-slim

ARG HOST=0.0.0.0
ARG PORT=8000
ARG TRANSPORT="http"
ARG AUTH_TYPE="none"
ARG TOKEN_JWKS_URI=""
ARG TOKEN_ISSUER=""
ARG TOKEN_AUDIENCE=""
ARG OAUTH_UPSTREAM_AUTH_ENDPOINT=""
ARG OAUTH_UPSTREAM_TOKEN_ENDPOINT=""
ARG OAUTH_UPSTREAM_CLIENT_ID=""
ARG OAUTH_UPSTREAM_CLIENT_SECRET=""
ARG OAUTH_BASE_URL=""
ARG OIDC_CONFIG_URL=""
ARG OIDC_CLIENT_ID=""
ARG OIDC_CLIENT_SECRET=""
ARG OIDC_BASE_URL=""
ARG REMOTE_AUTH_SERVERS=""
ARG REMOTE_BASE_URL=""
ARG ALLOWED_CLIENT_REDIRECT_URIS=""
ARG EUNOMIA_TYPE="none"
ARG EUNOMIA_POLICY_FILE="mcp_policies.json"
ARG EUNOMIA_REMOTE_URL=""
ENV OPENAPI_FILE=""

ENV HOST=${HOST}
ENV PORT=${PORT}
ENV TRANSPORT=${TRANSPORT}
ENV AUTH_TYPE=${AUTH_TYPE}
ENV TOKEN_JWKS_URI=${TOKEN_JWKS_URI}
ENV TOKEN_ISSUER=${TOKEN_ISSUER}
ENV TOKEN_AUDIENCE=${TOKEN_AUDIENCE}
ENV OAUTH_UPSTREAM_AUTH_ENDPOINT=${OAUTH_UPSTREAM_AUTH_ENDPOINT}
ENV OAUTH_UPSTREAM_TOKEN_ENDPOINT=${OAUTH_UPSTREAM_TOKEN_ENDPOINT}
ENV OAUTH_UPSTREAM_CLIENT_ID=${OAUTH_UPSTREAM_CLIENT_ID}
ENV OAUTH_UPSTREAM_CLIENT_SECRET=${OAUTH_UPSTREAM_CLIENT_SECRET}
ENV OAUTH_BASE_URL=${OAUTH_BASE_URL}
ENV OIDC_CONFIG_URL=${OIDC_CONFIG_URL}
ENV OIDC_CLIENT_ID=${OIDC_CLIENT_ID}
ENV OIDC_CLIENT_SECRET=${OIDC_CLIENT_SECRET}
ENV OIDC_BASE_URL=${OIDC_BASE_URL}
ENV REMOTE_AUTH_SERVERS=${REMOTE_AUTH_SERVERS}
ENV REMOTE_BASE_URL=${REMOTE_BASE_URL}
ENV ALLOWED_CLIENT_REDIRECT_URIS=${ALLOWED_CLIENT_REDIRECT_URIS}
ENV EUNOMIA_TYPE=${EUNOMIA_TYPE}
ENV EUNOMIA_POLICY_FILE=${EUNOMIA_POLICY_FILE}
ENV EUNOMIA_REMOTE_URL=${EUNOMIA_REMOTE_URL}
ENV OPENAPI_FILE=${OPENAPI_FILE}
ENV PATH="/usr/local/bin:${PATH}"
ENV UV_HTTP_TIMEOUT=3600

RUN pip install uv \
    && uv pip install --system --upgrade servicenow-api>=1.3.27

ENTRYPOINT exec servicenow-mcp \
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
    $( [ -n "${OPENAPI_FILE}" ] && echo "--openapi-file ${OPENAPI_FILE}" )
