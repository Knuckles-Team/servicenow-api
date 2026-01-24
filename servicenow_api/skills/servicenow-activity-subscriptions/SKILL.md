---
name: ServiceNow Activity Subscriptions
description: Capabilities for managing activity subscriptions in ServiceNow.
---

# ServiceNow Activity Subscriptions

This skill allows the agent to retrieve activity subscriptions for records.

## Tools

### `get_activity_subscriptions`

- **Description**: Retrieves activity subscriptions.
- **Parameters**:
    - `sys_id` (Optional[str]): Activity Subscription Sys ID.

## Usage

### Getting All Activity Subscriptions

```python
result = get_activity_subscriptions()
```
