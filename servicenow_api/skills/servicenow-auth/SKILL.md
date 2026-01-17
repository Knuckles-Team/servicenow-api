---
name: servicenow-auth
description: Manages ServiceNow auth. Use for token refresh. Triggers - sessions, auth issues.
---

### Overview
Auth utils via MCP.

### Key Tools
- `refresh_auth_token`.

### Usage Instructions
1. Call when token expires.

### Examples
- Refresh: `refresh_auth_token`.

### Error Handling
- Invalid creds: Re-auth.
