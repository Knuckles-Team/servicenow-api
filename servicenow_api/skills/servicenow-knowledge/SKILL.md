---
name: servicenow-knowledge
skill_type: skill
description: >-
  Read ServiceNow Knowledge Management articles via the servicenow-api MCP
  server: search and list articles, fetch one, pull attachments, and get
  featured or most-viewed articles. Use to find KB content to answer a
  question or cite an article. Do NOT use for generic table CRUD (servicenow-
  table-api) or incidents (servicenow-incident-management).
license: MIT
tags: [servicenow, knowledge, ksm, rest-api, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ServiceNow Knowledge

Scope: Read access to the ServiceNow Knowledge Management (KSM) API via the servicenow-api MCP server — search/list knowledge articles, fetch a single article, pull article attachments, and get featured or most-viewed articles. Use when the agent must find or retrieve published knowledge-base content to answer a question, cite a KB article, or surface self-service documentation. Do NOT use for generic table CRUD (servicenow-table-api), incidents (servicenow-incident-management), change (servicenow-change-management), or CMDB (servicenow-cmdb); this skill is read-only KB retrieval.

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


## Steps

1. Search with `servicenow_get_knowledge_articles` and a text `query`, and verify at least one article id and title is returned.
2. Fetch the chosen article with `servicenow_get_knowledge_article` and its `sys_id`, and verify the body text is present.
3. Pull files with `servicenow_get_knowledge_article_attachment` when the article references one, and verify the attachment metadata returns.
4. Use `servicenow_get_featured_knowledge_article` or `servicenow_get_most_viewed_knowledge_articles` when no query fits, and verify the list is non-empty.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| No articles returned | Query too specific or the article is not published | Broaden `query`, remove filters, and check the article workflow state via `servicenow_get_table` on `kb_knowledge` |
| Article fetch returns 404 | Wrong `sys_id` | Take the `sys_id` from a fresh `servicenow_get_knowledge_articles` result |
| Auth error (401/403) | `SERVICENOW_USERNAME`/`SERVICENOW_PASSWORD` or the OAuth pair missing or the role lacks table access | Set the variables listed under Prerequisites, then call `servicenow_get_table` with `sysparm_limit` 1 on the target table to confirm access |

## Tools & actions
Each operation is its own typed tool named `servicenow_<operation>`; pass its parameters as named arguments (the tool schema lists them).

| Area | Typed tools |
|----------------|---------|
| knowledge management | `servicenow_get_knowledge_articles`, `servicenow_get_knowledge_article`, `servicenow_get_knowledge_article_attachment`, `servicenow_get_featured_knowledge_article`, `servicenow_get_most_viewed_knowledge_articles` |
### Key parameters
- `sys_id` — the article sys_id for `get_knowledge_article` /
  `get_knowledge_article_attachment`.
- Search/filter controls follow the Knowledge API: pass a text `query`/`kb`/`filter`
  and pagination (`limit`, `offset`) as the API expects. When unsure of the exact
  key name for the instance/version, list first and inspect the response shape.

## Recipes (tool arguments)
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
- Pass arguments as named parameters; nested objects are plain JSON objects.
- The Knowledge API returns published/viewable articles subject to the caller's
  KB read criteria — an article missing from results may be a permissions/criteria
  issue, not an absent record.
- `get_knowledge_article_attachment` returns attachment content/metadata for a
  given article — expect binary or reference payloads, not article text.
- For authoring or lifecycle changes, drop to `servicenow-table-api` on
  `kb_knowledge`; this surface is intentionally read-only.
