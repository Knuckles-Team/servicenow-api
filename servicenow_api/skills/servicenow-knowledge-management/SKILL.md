---
name: servicenow-knowledge-management
description: Manages ServiceNow KB. Use for articles, attachments, featured/most viewed. Triggers - docs, self-help.
---

### Overview
KB queries via MCP.

### Key Tools
- Get articles, attachments, featured, most viewed.

### Usage Instructions
1. Filters: kb, language.

### Examples
- Get article: `get_knowledge_article` with article_sys_id="kb1".
- Most viewed: `get_most_viewed_knowledge_articles`.

### Error Handling
- No access: Check KB perms.
