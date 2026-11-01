# CONN-SERVICENOW-API-CONNECTOR-IDENTITY — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-SERVICENOW-API-CONNECTOR-IDENTITY-R001` | `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name` | Every connector name in the package is `servicenow-mcp`. |

## Negative and boundary cases

Each proving test above includes the refusal or error case that its row names. A vendor outage or an unauthorised call must return the SDK typed error.

## Quality and release proof

Run `uv run pytest tests` and `pre-commit run --all-files` from the repository root. A planned test is added by the code change that lands the row.
