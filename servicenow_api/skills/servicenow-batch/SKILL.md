---
name: servicenow-batch
description: Manages batch requests in ServiceNow. Use for sending multiple REST API requests in a single call.
---

### Overview
Handles batch processing of REST API requests via MCP.

### Key Tools
- `batch_request`: Sends multiple REST API requests in a single call. Params: batch_request_id (optional), rest_requests (required list).

### Usage Instructions
1. Construct a list of `BatchRequestItem` objects (method, url, body, etc.).
2. Call `batch_request` with the list.

### Examples
- Batch request: `batch_request` with rest_requests=[{"method": "GET", "url": "/api/now/table/incident"}]

### Error Handling
- 400: Invalid parameters or request structure.
