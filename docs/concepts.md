# Concept Registry — servicenow-api

> **Prefix**: `CONCEPT:SNOW-*`
> **Version**: 1.19.0
> **Bridge**: [`CONCEPT:ECO-4.0`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:SNOW-001` | Account Operations | MCP tool domain `account` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-002` | Activity Subscriptions Operations | MCP tool domain `activity_subscriptions` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-003` | Aggregate Operations | MCP tool domain `aggregate` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-004` | Application Operations | MCP tool domain `application` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-005` | Attachment Operations | MCP tool domain `attachment` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-006` | Authentication & Session Management | MCP tool domain `auth` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-007` | Batch Operations | MCP tool domain `batch` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-008` | Change Management Operations | MCP tool domain `change_management` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-009` | Cicd Operations | MCP tool domain `cicd` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-010` | Cilifecycle Operations | MCP tool domain `cilifecycle` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-011` | Configuration Management DB | MCP tool domain `cmdb` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-012` | Custom Api Operations | MCP tool domain `custom_api` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-013` | Data Classification Operations | MCP tool domain `data_classification` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-014` | Devops Operations | MCP tool domain `devops` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-015` | Email Operations | MCP tool domain `email` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-016` | Flows Operations | MCP tool domain `flows` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-017` | Hr Operations | MCP tool domain `hr` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-018` | Import Sets Operations | MCP tool domain `import_sets` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-019` | Incident Management | MCP tool domain `incidents` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-020` | Knowledge Management Operations | MCP tool domain `knowledge_management` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-021` | Metricbase Operations | MCP tool domain `metricbase` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-022` | Misc Operations | MCP tool domain `misc` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-023` | Plugins Operations | MCP tool domain `plugins` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-024` | Ppm Operations | MCP tool domain `ppm` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-025` | Product Inventory Operations | MCP tool domain `product_inventory` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-026` | Service Qualification Operations | MCP tool domain `service_qualification` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-027` | Source Control Operations | MCP tool domain `source_control` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-028` | Table Api Operations | MCP tool domain `table_api` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-029` | Testing Operations | MCP tool domain `testing` — Action-routed dynamic tool registration |
| `CONCEPT:SNOW-030` | Update Sets Operations | MCP tool domain `update_sets` — Action-routed dynamic tool registration |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |
| `CONCEPT:OS-5.2` | Cognitive Scheduler | agent-utilities |
| `CONCEPT:OS-5.3` | Guardrail Engine | agent-utilities |
| `CONCEPT:OS-5.4` | Audit Logging | agent-utilities |
| `CONCEPT:KG-2.0` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

This project integrates with `agent-utilities` via `CONCEPT:ECO-4.0` (Unified Toolkit Ingestion). The `servicenow_api` MCP server registers its tools with the agent-utilities FastMCP middleware, enabling automatic discovery, telemetry, and Knowledge Graph ingestion of all SNOW-* concepts.
