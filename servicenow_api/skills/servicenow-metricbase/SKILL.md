---
name: ServiceNow MetricBase
description: Capabilities for interacting with ServiceNow MetricBase for time series data.
---

# ServiceNow MetricBase

This skill allows the agent to insert time series data into MetricBase.

## Tools

### `metricbase_insert`

- **Description**: Inserts time series data into MetricBase.
- **Parameters**:
    - `table_name` (str): Table name.
    - `sys_id` (str): Record Sys ID.
    - `metric_name` (str): Metric name.
    - `values` (List[Any]): Values to insert.
    - `start_time` (Optional[str]): Start time.
    - `end_time` (Optional[str]): End time.

## Usage

### Inserting Metric Data

```python
result = metricbase_insert(
    table_name="incident_metric",
    sys_id="sys_id",
    metric_name="cpu_usage",
    values=[{"timestamp": "2023-10-27T10:00:00Z", "value": 50}]
)
```
