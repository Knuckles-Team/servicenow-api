---
name: ServiceNow HR
description: Capabilities for retrieving HR Profile information in ServiceNow.
---

# ServiceNow HR

This skill allows the agent to retrieve HR Profile information.

## Tools

### `get_hr_profile`

- **Description**: Retrieves HR profile information.
- **Parameters**:
    - `sys_id` (Optional[str]): HR Profile Sys ID.
    - `user` (Optional[str]): User Sys ID.

## Usage

### Getting HR Profile for a User

```python
result = get_hr_profile(user="sys_id_of_user")
```
