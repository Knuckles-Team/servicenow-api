# Concept Registry — servicenow-api

> **Prefix**: `CONCEPT:SNOW-*`
> **Version**: 1.19.0
> **Bridge**: [`CONCEPT:AU-ECO.messaging.native-backend-abstraction`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:SN-OS.governance.snow` | Account Operations | MCP tool domain `account` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-2` | Activity Subscriptions Operations | MCP tool domain `activity_subscriptions` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-3` | Aggregate Operations | MCP tool domain `aggregate` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-4` | Application Operations | MCP tool domain `application` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-5` | Attachment Operations | MCP tool domain `attachment` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-6` | Authentication & Session Management | MCP tool domain `auth` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-7` | Batch Operations | MCP tool domain `batch` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-8` | Change Management Operations | MCP tool domain `change_management` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-9` | Cicd Operations | MCP tool domain `cicd` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-10` | Cilifecycle Operations | MCP tool domain `cilifecycle` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-11` | Configuration Management DB | MCP tool domain `cmdb` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-12` | Custom Api Operations | MCP tool domain `custom_api` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-13` | Data Classification Operations | MCP tool domain `data_classification` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-14` | Devops Operations | MCP tool domain `devops` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-15` | Email Operations | MCP tool domain `email` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-16` | Flows Operations | MCP tool domain `flows` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-17` | Hr Operations | MCP tool domain `hr` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-18` | Import Sets Operations | MCP tool domain `import_sets` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-19` | Incident Management | MCP tool domain `incidents` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-20` | Knowledge Management Operations | MCP tool domain `knowledge_management` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-21` | Metricbase Operations | MCP tool domain `metricbase` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-22` | Misc Operations | MCP tool domain `misc` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-23` | Plugins Operations | MCP tool domain `plugins` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-24` | Ppm Operations | MCP tool domain `ppm` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-25` | Product Inventory Operations | MCP tool domain `product_inventory` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-26` | Service Qualification Operations | MCP tool domain `service_qualification` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-27` | Source Control Operations | MCP tool domain `source_control` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-28` | Table Api Operations | MCP tool domain `table_api` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-29` | Testing Operations | MCP tool domain `testing` — Action-routed dynamic tool registration |
| `CONCEPT:SN-OS.governance.snow-30` | Update Sets Operations | MCP tool domain `update_sets` — Action-routed dynamic tool registration |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:AU-ECO.messaging.native-backend-abstraction` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:AU-ORCH.adapter.hot-cache-invalidation` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:AU-OS.config.secrets-authentication` | Prompt Injection Defense | agent-utilities |
| `CONCEPT:AU-OS.state.cognitive-scheduler-preemption` | Cognitive Scheduler | agent-utilities |
| `CONCEPT:AU-OS.governance.reactive-multi-axis-budget` | Guardrail Engine | agent-utilities |
| `CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox` | Audit Logging | agent-utilities |
| `CONCEPT:AU-KG.query.object-graph-mapper` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

This project integrates with `agent-utilities` via `CONCEPT:AU-ECO.messaging.native-backend-abstraction` (Unified Toolkit Ingestion). The `servicenow_api` MCP server registers its tools with the agent-utilities FastMCP middleware, enabling automatic discovery, telemetry, and Knowledge Graph ingestion of all SNOW-* concepts.
