# CONN-SERVICENOW-API-CONNECTOR-CONTENT — Data model

Entities and records that the rows add or declare.

| Row | Entity or record | Definition |
|---|---|---|
| `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R002` | Ontology joins the parent graph | Each `<package>/ontology/*.ttl` that declares classes imports `http://knuckles.team/kg`, and each class reaches an medulla parent class through `rdfs:subClassOf`. |
| `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R003` | Declared ingest sources | `servicenow_api/ontology/ingest_sources.json` declares the `incidents` source (record type `Incident`, read-only tool `servicenow_get_incidents`, first 50 records) for the connector `servicenow-mcp`, and the record type is a key of the connector manifest `schema_mappings`. |
| `CONN-SERVICENOW-API-CONNECTOR-CONTENT-R008` | Declare access contracts for the competency reads of servicenow-api | Subsystem: connector `servicenow-api`. |

Relations follow the row text; the connector adds no table of its own.
