---
name: ServiceNow Data Classification
description: Capabilities for managing data classifications in ServiceNow.
---

# ServiceNow Data Classification

This skill allows the agent to retrieve data classification information for tables and columns in ServiceNow.

## Tools

### `get_data_classification`

- **Description**: Retrieves data classification information.
- **Parameters**:
    - `sys_id` (Optional[str]): Classification record Sys ID.
    - `table_name` (Optional[str]): Table name.
    - `column_name` (Optional[str]): Column name.

## Usage

### Getting Classification for a Column

```python
result = get_data_classification(
    table_name="incident",
    column_name="short_description"
)
```
