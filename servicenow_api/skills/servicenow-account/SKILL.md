---
name: ServiceNow Account
description: Capabilities for managing CSM Accounts in ServiceNow.
---

# ServiceNow Account

This skill allows the agent to retrieve Customer Service Management (CSM) Account information.

## Tools

### `get_account`

- **Description**: Retrieves CSM account information.
- **Parameters**:
    - `sys_id` (Optional[str]): Account Sys ID.
    - `name` (Optional[str]): Account name.
    - `number` (Optional[str]): Account number.

## Usage

### Getting Account by Name

```python
result = get_account(name="Acme Corp")
```
