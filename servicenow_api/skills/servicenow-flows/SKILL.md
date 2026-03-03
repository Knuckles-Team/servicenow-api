---
name: servicenow-flows
description: Manages and visualizes ServiceNow Flow Designer workflows. Use for generating Mermaid diagrams of flows and subflows. Triggers - flows, flow designer, subflows, flow diagrams.
tags: [flows]
---

### Overview
The `servicenow-flows` skill provides advanced capabilities for analyzing and visualizing ServiceNow Flow Designer workflows. It leverages the `workflow_to_mermaid` tool to perform recursive subflow traversal and generate professional Markdown reports with embedded Mermaid diagrams.

### Key Tools
- `workflow_to_mermaid`: Generates a unified Mermaid diagram and rich Markdown report for multiple flows.
  - **Params**:
    - `flow_identifiers` (required): List of flow names or sys_ids.
    - `save_to_file` (optional, default: True): Saves a .md file.
    - `output_dir` (optional, default: "./servicenow_flow_reports"): Folder for saved reports.
    - `mermaid_name` (optional): Basename for the generated file.
    - `max_depth` (optional, default: 5): Recursion depth for subflows.

### Usage Instructions
1. Use `workflow_to_mermaid` when a user wants to "see", "visualize", or "diagram" a Flow Designer workflow.
2. The agent will recursively follow subflows and represent them in Mermaid `subgraph` blocks.
3. Branching logic (If, Switch, For Each) is automatically detected and labeled where possible.

### Examples
- Visualize a flow: `workflow_to_mermaid` with `flow_identifiers=["Order Laptop"]`.
- Recursive analysis: `workflow_to_mermaid` with `flow_identifiers=["ParentFlow"]` and `max_depth=3`.

### Error Handling
- **No Flows Found**: If the identifier doesn't match a name or sys_id in `sys_hub_flow`, the tool returns a summary indicating zero flows found.
- **Deep Recursion**: Max depth is capped to prevent infinite loops (default 5).
