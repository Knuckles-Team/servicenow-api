---
name: servicenow-knowledge
description: >-
  Read access to the ServiceNow Knowledge Management (KSM) API via the
  servicenow-api MCP server — search/list knowledge articles, fetch a single
  article, pull article attachments, and get featured or most-viewed articles.
  Use when the agent must find or retrieve published knowledge-base content to
  answer a question, cite a KB article, or surface self-service documentation.
  Do NOT use for generic table CRUD (servicenow-table-api), incidents
  (servicenow-incident-management), change (servicenow-change-management), or
  CMDB (servicenow-cmdb); this skill is read-only KB retrieval.
license: MIT
tags: [servicenow, knowledge, ksm, rest-api, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ServiceNow Knowledge

Read-only access to the ServiceNow **Knowledge Management** API for retrieving
published knowledge-base articles, their attachments, and curated
featured/most-viewed lists.

## When to use
- Search / list knowledge articles (by keyword, knowledge base, or filter).
- Fetch a single article's full body by sys_id.
- Retrieve an article's attachment.
- Surface featured or most-viewed articles.

## When NOT to use
- Creating/editing articles or generic table CRUD → `servicenow-table-api`
  against `kb_knowledge` (this skill is retrieval-only).
- Incidents, change requests, or CMDB CIs → their dedicated skills.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`servicenow-api`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `SERVICENOW_INSTANCE` | ✅ | Instance URL (alias `SERVICENOW_URL`) |
| `SERVICENOW_USERNAME` | ✅ | Basic-auth user |
| `SERVICENOW_PASSWORD` | ✅ | Basic-auth password |
| `SERVICENOW_CLIENT_ID` / `SERVICENOW_CLIENT_SECRET` | optional | OAuth2 |
| `SERVICENOW_SSL_VERIFY` | optional | TLS verification toggle |

Full env/tag matrix (do not re-document here): the mcp-client reference
`agent-tools/mcp-client/references/servicenow-api.md`. `MCP_TOOL_MODE`
(`condensed`|`verbose`|`both`) selects the condensed surface (used below) vs. the
one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `servicenow_knowledge_management` | `get_knowledge_articles`, `get_knowledge_article`, `get_knowledge_article_attachment`, `get_featured_knowledge_article`, `get_most_viewed_knowledge_articles` |

### Key parameters
- `sys_id` — the article sys_id for `get_knowledge_article` /
  `get_knowledge_article_attachment`.
- Search/filter controls follow the Knowledge API: pass a text `query`/`kb`/`filter`
  and pagination (`limit`, `offset`) as the API expects. When unsure of the exact
  key name for the instance/version, list first and inspect the response shape.

## Recipes (`params_json`)
Search / list knowledge articles by keyword (paginated):
```json
{"query":"vpn setup","limit":20,"offset":0}
```
Fetch one article by sys_id (full body):
```json
{"sys_id":"<article_sys_id>"}
```
Get featured articles:
```json
{}
```
Get most-viewed articles (top N):
```json
{"limit":10}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- The Knowledge API returns published/viewable articles subject to the caller's
  KB read criteria — an article missing from results may be a permissions/criteria
  issue, not an absent record.
- `get_knowledge_article_attachment` returns attachment content/metadata for a
  given article — expect binary or reference payloads, not article text.
- For authoring or lifecycle changes, drop to `servicenow-table-api` on
  `kb_knowledge`; this surface is intentionally read-only.
