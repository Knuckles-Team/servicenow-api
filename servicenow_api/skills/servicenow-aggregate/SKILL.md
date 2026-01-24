---
name: ServiceNow Aggregate
description: Capabilities for computing aggregate statistics on ServiceNow tables.
---

# ServiceNow Aggregate

This skill allows the agent to compute aggregate statistics (counts, min, max, etc.) on ServiceNow tables.

## Tools

### `get_stats`

- **Description**: Retrieves aggregate statistics for a table.
- **Parameters**:
    - `table_name` (str): Table name to aggregate on.
    - `query` (Optional[str]): Encoded query string.
    - `groupby` (Optional[str]): Field to group by.
    - `stats` (Optional[str]): Statistics function.

## Usage

### Getting Incident Counts Grouped by Priority

```python
result = get_stats(
    table_name="incident",
    groupby="priority",
    stats="count"
)
```
