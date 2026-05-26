#!/usr/bin/python

import base64
import gzip
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
from agent_utilities.base_utilities import get_logger
from agent_utilities.core.exceptions import (
    MissingParameterError,
    ParameterError,
)
from pydantic import ValidationError

from servicenow_api.servicenow_models import (
    AggregateModel,
    Authentication,
    EmailModel,
    FlowGraph,
    FlowReportResult,
    Response,
    Table,
    TableModel,
)

logger = get_logger(__name__)


def decode_values(raw_values: str | None) -> list[dict[str, Any]]:
    if not raw_values or not isinstance(raw_values, str):
        return []
    try:
        if "," in raw_values and len(raw_values.split(",", 1)[0]) < 10:
            raw_values = raw_values.split(",", 1)[1]
        decoded_b64 = base64.b64decode(raw_values)
        decompressed = gzip.decompress(decoded_b64).decode("utf-8")
        parsed = json.loads(decompressed)
        return parsed if isinstance(parsed, list) else [parsed]
    except Exception as e:
        logger.error(f"Failed to decode values: {e}")
        return []


def extract_action_details(
    decoded: list[dict[str, Any]], action_type: str
) -> list[str]:
    """
    Extracts specific metadata from decoded action values based on the action type.
    """
    details = []
    params: dict[str, Any] = {}

    for p in decoded:
        name = p.get("name")

        val = p.get("displayValue") or p.get("value")
        if name and val:
            params[name] = val

    at_clean = (action_type or "").lower()

    if "approval" in at_clean:
        table = params.get("table_name") or params.get("table")
        rules = params.get("approval_conditions")
        if table:
            details.append(f"Table: {table}")
        if rules:
            details.append(f"Rules: {rules}")

    elif "create record" in at_clean or "update record" in at_clean:
        table = (
            params.get("table_name") or params.get("ah_table") or params.get("table")
        )
        fields = params.get("values") or params.get("ah_fields")
        if table:
            details.append(f"Table: {table}")
        if fields and isinstance(fields, str):
            important = [f.split("=")[0] for f in fields.split("^") if "=" in f]
            if important:
                details.append(f"Fields: {', '.join(important[:5])}...")

    elif "look up record" in at_clean:
        table = params.get("table")
        conds = params.get("conditions")
        if table:
            details.append(f"Table: {table}")
        if conds:
            details.append(f"Cond: {conds}")

    elif "worknote" in at_clean or "comment" in at_clean:
        note = (
            params.get("ah_work_note")
            or params.get("ah_comment")
            or params.get("note")
            or params.get("comment")
        )
        if note:
            details.append(f"Note: {note}")

    return details


def find_subflow_sys_id(decoded: list[dict[str, Any]]) -> str | None:
    for item in decoded:
        for val in item.values():
            if (
                isinstance(val, str)
                and len(val) == 32
                and all(c in "0123456789abcdefABCDEF" for c in val)
            ):
                return val
    return None


def determine_node_type(action: dict[str, Any], decoded: list[dict[str, Any]]) -> str:
    action_name = action.get("name", "").lower()
    act = action.get("action", {})
    act_name = (act.get("display_value") or "").lower()

    if (
        "if" in action_name
        or "if" in act_name
        or "decision" in action_name
        or "switch" in action_name
    ):
        return "decision"
    if (
        "for each" in action_name
        or "for each" in act_name
        or "do the following" in action_name
    ):
        return "loop"

    sub = find_subflow_sys_id(decoded)
    if sub:
        return "subflow_call"

    return "action"


def sanitize_mermaid_label(label: str) -> str:
    """Sanitize and quote labels for Mermaid syntax."""
    if not label:
        return ""

    sanitized = label.replace('"', "'").replace("\n", " ").replace("\r", " ")
    return f'"{sanitized}"'


def get_reachable_subgraph(graph: FlowGraph, root_id: str) -> FlowGraph:
    """
    Extracts a subgraph containing only the nodes and edges reachable from the given root_id.
    """

    start_node = f"root_{root_id[:8]}_trigger_{root_id[:8]}"
    if not any(node.id == start_node for node in graph.nodes):
        start_node = f"trigger_{root_id[:8]}"
        if not any(node.id == start_node for node in graph.nodes):
            return FlowGraph(nodes=[], edges=[], summary="Root not found")

    adj: defaultdict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        adj[edge.from_id].append(edge.to_id)

    node_by_id = {node.id: node for node in graph.nodes}
    reachable_nodes: set[str] = set()
    stack = [start_node]
    while stack:
        curr = stack.pop()
        if curr not in reachable_nodes:
            reachable_nodes.add(curr)
            for neighbor in adj[curr]:
                if neighbor not in reachable_nodes:
                    stack.append(neighbor)

    sub_nodes = [node_by_id[nid] for nid in reachable_nodes]
    sub_edges = [
        edge
        for edge in graph.edges
        if edge.from_id in reachable_nodes and edge.to_id in reachable_nodes
    ]
    return FlowGraph(
        nodes=sub_nodes,
        edges=sub_edges,
        summary=f"Reachable from {root_id}",
    )


def find_connected_components(graph: FlowGraph) -> list[FlowGraph]:
    """
    Splits a single large global FlowGraph into a list of smaller FlowGraphs,
    where each sub-graph represents a completely disconnected component of flows/subflows.
    """
    if not graph.nodes:
        return []

    adj: defaultdict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        adj[edge.from_id].append(edge.to_id)
        adj[edge.to_id].append(edge.from_id)

    all_node_ids = {node.id for node in graph.nodes}
    node_by_id = {node.id: node for node in graph.nodes}

    visited: set[str] = set()
    components: list[FlowGraph] = []

    for start_node in all_node_ids:
        if start_node not in visited:
            component_nodes: set[str] = set()
            stack = [start_node]
            while stack:
                curr = stack.pop()
                if curr not in component_nodes:
                    component_nodes.add(curr)
                    visited.add(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in component_nodes:
                            stack.append(neighbor)

            sub_nodes = [node_by_id[nid] for nid in component_nodes]
            sub_edges = [
                edge
                for edge in graph.edges
                if edge.from_id in component_nodes and edge.to_id in component_nodes
            ]
            components.append(
                FlowGraph(
                    nodes=sub_nodes,
                    edges=sub_edges,
                    summary=f"Component size: {len(sub_nodes)}",
                )
            )

    return components


def graph_to_mermaid_multi(
    graph: FlowGraph,
    root_sys_ids: list[str],
    all_metadata: dict[str, dict[str, Any]] = None,
) -> str:
    lines = ["flowchart TD"]

    for root_id in root_sys_ids:
        root_prefix = f"root_{root_id[:8]}_"

        has_nodes = any(
            node.id.startswith(root_prefix)
            or node.id == f"root_{root_id[:8]}_trigger_{root_id[:8]}"
            for node in graph.nodes
        )
        if not has_nodes:
            continue

        meta = (all_metadata or {}).get(root_id, {})
        flow_name = meta.get("name", root_id)
        lines.append(f'    subgraph "{flow_name} ({root_id})"')
        for node in graph.nodes:
            if (
                node.id.startswith(root_prefix)
                or node.id == f"root_{root_id[:8]}_trigger_{root_id[:8]}"
            ):
                label = sanitize_mermaid_label(node.label)
                shape_map = {
                    "trigger": f"(({label}))",
                    "decision": f"{{{{{label}}}}}",
                    "loop": f"[/{label}/]",
                    "subflow_call": f"[[{label}]]",
                }
                shape = shape_map.get(node.type, f"[{label}]")
                lines.append(f"        {node.id}{shape}")
        lines.append("    end")

    for node in graph.nodes:
        if not any(node.id.startswith(f"root_{rid[:8]}_") for rid in root_sys_ids):
            label = sanitize_mermaid_label(node.label)
            shape_map = {
                "trigger": f"(({label}))",
                "decision": f"{{{{{label}}}}}",
                "loop": f"[/{label}/]",
                "subflow_call": f"[[{label}]]",
            }
            shape = shape_map.get(node.type, f"[{label}]")
            lines.append(f"    {node.id}{shape}")

    for edge in graph.edges:
        label = f" |{edge.label}|" if edge.label else ""
        lines.append(f"    {edge.from_id} -->{label} {edge.to_id}")

    return "\n".join(lines)


def build_polished_markdown(
    graph: FlowGraph,
    metadata: dict[str, dict[str, Any]],
    root_sys_ids: list[str],
    mermaid_code: str,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = f"""# ServiceNow Flow Relationship Report
**Generated:** {now}
**Root Flows Analyzed:** {len(root_sys_ids)}

## Executive Summary
Unified diagram showing {len(root_sys_ids)} root flows + all recursive subflows and cross-relationships.

## Root Flows Overview
| Name | Sys ID | Domain | Scope / Application | Active | Flow Type | Last Updated |
|------|--------|--------|---------------------|--------|-----------|--------------|
"""
    for rid in root_sys_ids:
        m = metadata.get(rid, {})
        md += f"| {m.get('name')} | `{rid}` | {m.get('domain')} | {m.get('scope')} / {m.get('application')} | {m.get('active')} | {m.get('flow_type')} | {m.get('updated_on')} |\n"

    md += """
## All Flows & Subflows (including nested)
| Name | Sys ID | Domain | Scope | Active | Description |
|------|--------|--------|-------|--------|-------------|
"""
    for sid, m in metadata.items():
        md += f"| {m.get('name')} | `{sid}` | {m.get('domain')} | {m.get('scope')} | {m.get('active')} | {m.get('description', '')[:80]}... |\n"

    mermaid_blocks = (
        mermaid_code.split("|||BLOCK_SEP|||")
        if "|||BLOCK_SEP|||" in mermaid_code
        else [mermaid_code]
    )

    md += f"""
## Unified Flow Diagrams ({len(mermaid_blocks)} distinct groups)
"""

    for i, block in enumerate(mermaid_blocks):
        md += f"""
### Group {i + 1}
```mermaid
{block.strip()}
```
"""

    md += """
*Tip: Copy the code block above into [mermaid.live](https://mermaid.live) or any Markdown viewer that supports Mermaid.*

## Generation Notes
- Subflows are expanded and deduplicated (appear only once).
- Cross-flow "calls" relationships are shown.
- Branching/conditions approximated from action names.
- Max recursion depth: 5 (prevents infinite loops).

---
*Report generated via ServiceNow MCP Agent — {now}*
"""
    return md


from servicenow_api.api.api_client_base import ServiceNowApiBase


class ServiceNowApiSystem(ServiceNowApiBase):
    def refresh_auth_token(self) -> Response:
        """
        Refresh the authentication token
        :return:
        Response with new refreshed token.
        """
        refresh_data = {
            "grant_type": "refresh_token",
            "client_id": self.auth_data["client_id"],
            "client_secret": self.auth_data["client_secret"],
            "refresh_token": self.token,
        }
        encoded_data_str = urlencode(refresh_data)
        try:
            response = requests.post(
                url=self.auth_url,
                data=encoded_data_str,
                headers=self.auth_headers,
                timeout=30,
            )
            response.raise_for_status()
            json_response = response.json()
            self.token = json_response["access_token"]
            parsed_data = Authentication.model_validate(json_response)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid response data: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during token refresh: {e}", file=sys.stderr)
            raise

    def delete_table_record(self, **kwargs) -> Response:
        """
        Delete a record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be deleted.
        :type table_record_sys_id: str

        :return: Response containing parsed Pydantic model with information about the deletion.
        :rtype: Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.table_record_sys_id is None:
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_table(self, **kwargs) -> Response:
        """
        Get records from the specified table based on provided parameters.

        :param table: The name of the table.
        :type table: str
        :param name_value_pairs: Dictionary of name-value pairs for filtering records.
        :type name_value_pairs: str
        :param sysparm_display_value: Display values for reference fields ('True', 'False', or 'all').
        :type sysparm_display_value: str
        :param sysparm_exclude_reference_link: Exclude reference links in the response.
        :type sysparm_exclude_reference_link: bool
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_no_count: Do not include the total number of records in the response.
        :type sysparm_no_count: bool
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param sysparm_query_no_domain: Exclude records based on domain separation.
        :type sysparm_query_no_domain: bool
        :param sysparm_suppress_pagination_header: Suppress pagination headers in the response.
        :type sysparm_suppress_pagination_header: bool
        :param sysparm_view: Display style ('desktop', 'mobile', or 'both').
        :type sysparm_view: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/{table_model.table}",
                params=table_model.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Table.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_table_record(self, **kwargs) -> Response:
        """
        Get a specific record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be retrieved.
        :type table_record_sys_id: str

        :return: Response containing parsed Pydantic model with information about the retrieved record.
        :rtype: Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.table_record_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def patch_table_record(self, **kwargs) -> Response:
        """
        Partially update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the updated record.
        :rtype: Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if (
                table_model.table is None
                or table_model.table_record_sys_id is None
                or table_model.data is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def update_table_record(self, **kwargs) -> Response:
        """
        Fully update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the updated record.
        :rtype: Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if (
                table_model.table is None
                or table_model.table_record_sys_id is None
                or table_model.data is None
            ):
                raise MissingParameterError
            response = self._session.put(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def add_table_record(self, **kwargs) -> Response:
        """
        Add a new record to the specified table.

        :param table: The name of the table.
        :type table: str
        :param data: Dictionary containing the field values for the new record.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the added record.
        :rtype: Response

        :raises MissingParameterError: If table or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.data is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/now/table/{table_model.table}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def send_email(self, **kwargs) -> Response:
        try:
            email = EmailModel(**kwargs)
            response = self._session.post(
                url=f"{self.url}/now/email",
                headers=self.headers,
                json=email.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_stats(self, **kwargs) -> Response:
        try:
            agg = AggregateModel(**kwargs)
            params: dict[str, Any] = {}
            if agg.query:
                params["sysparm_query"] = agg.query
            if agg.groupby:
                params["sysparm_group_by"] = agg.groupby
            if agg.stats:
                params["sysparm_count"] = "true"

            response = self._session.get(
                url=f"{self.url}/now/stats/{agg.table_name}",
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def api_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Response:
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method.upper()}")
        try:
            request_func = getattr(self._session, method.lower())
            response = request_func(
                url=f"{self.url}/{endpoint}",
                headers=self.headers,
                data=data,
                json=json,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            parsed_data = (
                response.json()
                if response.content
                and "application/json" in response.headers.get("Content-Type", "")
                else None
            )
            return Response(response=response, result=parsed_data)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        except Exception as e:
            print(f"Request Error: {str(e)}", file=sys.stderr)
            raise

    def get_flow_metadata(self, flow_sys_id: str) -> dict[str, Any]:
        """Fetch rich metadata for any flow/subflow."""
        logger.debug(f"Fetching metadata for flow {flow_sys_id}")
        try:
            resp = self.get_table(
                table="sys_hub_flow",
                sysparm_query=f"sys_id={flow_sys_id}",
                sysparm_fields="sys_id,name,active,flow_type,description,sys_scope,application,sys_domain,sys_updated_on,sys_created_on",
                sysparm_display_value="true",
                sysparm_limit="1",
            )
            if not resp.response.ok:
                logger.error(
                    f"Failed fetching metadata for flow {flow_sys_id}: {resp.response.status_code} - {resp.response.text}"
                )
                return {}

            results = resp.response.json().get("result", [])
            if not results:
                logger.warning(f"No metadata found for flow {flow_sys_id}")
                return {}

            flow = results[0] if isinstance(results, list) else results

            def get_val(item, key, default=""):
                v = item.get(key)
                if isinstance(v, dict):
                    return v.get("display_value", v.get("value", default))
                return v if v is not None else default

            return {
                "sys_id": flow.get("sys_id"),
                "name": get_val(flow, "name", "Unnamed Flow"),
                "domain": get_val(flow, "sys_domain"),
                "scope": get_val(flow, "sys_scope"),
                "application": get_val(flow, "application", "Global"),
                "active": str(flow.get("active", False)).lower() == "true",
                "flow_type": flow.get("flow_type", "flow"),
                "description": flow.get("description", ""),
                "updated_on": flow.get("sys_updated_on"),
                "created_on": flow.get("sys_created_on"),
            }
        except Exception as e:
            logger.error(f"Error fetching metadata for flow {flow_sys_id}: {e}")
            return {}

    def workflow_to_mermaid(
        self,
        flow_identifiers: list[str] | None = None,
        max_depth: int = 5,
        save_to_file: bool = True,
        output_dir: str | None = None,
        mermaid_name: str = "servicenow_workflow",
        segment_by_root: bool = True,
        destination_file: str | None = None,
    ) -> FlowReportResult:
        """
        Generates a Mermaid diagram representing the relationships between ServiceNow flows and subflows.

        :param flow_identifiers: List of flow names or sys_ids to use as roots. If None, fetches all active flows.
        :param max_depth: Maximum recursion depth for subflow discovery.
        :param save_to_file: Whether to save the result to a markdown file.
        :param output_dir: Directory to save the report. Defaults to project/servicenow_flow_reports.
        :param mermaid_name: Base name for the generated file (used if destination_file is not provided).
        :param segment_by_root: If True, generates a separate diagram for each root flow.
        :param destination_file: Explicit full path to save the markdown report.
        """
        from servicenow_api import api_client as _api_client

        if flow_identifiers is None:
            flow_identifiers = []

        if not destination_file and output_dir is None:
            ws = _api_client.get_agent_workspace()
            output_dir = str(ws / "servicenow_flow_reports")
            logger.info(f"Using default output directory: {output_dir}")

        logger.info(
            f"workflow_to_mermaid called with flow_identifiers: {flow_identifiers}"
        )
        try:
            root_sys_ids: list[str] = []
            initial_metadata: dict[str, dict[str, Any]] = {}

            if not flow_identifiers:
                logger.info("No flow_identifiers provided. Fetching all active flows.")
                resp = self.get_table(
                    table="sys_hub_flow",
                    sysparm_query="active=true^flow_type=flow",
                    sysparm_limit="1000",
                    sysparm_fields="sys_id,name,active,flow_type,description,sys_scope,application,sys_domain,sys_updated_on,sys_created_on",
                    sysparm_display_value="true",
                )
                if resp.response.ok:
                    results = resp.response.json().get("result", [])
                    if results:
                        results = results if isinstance(results, list) else [results]
                        for r in results:
                            sid = r.get("sys_id")
                            if sid:
                                root_sys_ids.append(sid)

                                def get_val(item, key, default=""):
                                    v = item.get(key)
                                    if isinstance(v, dict):
                                        return v.get(
                                            "display_value", v.get("value", default)
                                        )
                                    return v if v is not None else default

                                initial_metadata[sid] = {
                                    "sys_id": sid,
                                    "name": get_val(r, "name", "Unnamed Flow"),
                                    "domain": get_val(r, "sys_domain"),
                                    "scope": get_val(r, "sys_scope"),
                                    "application": get_val(r, "application", "Global"),
                                    "active": str(r.get("active", False)).lower()
                                    == "true",
                                    "flow_type": r.get("flow_type", "flow"),
                                    "description": r.get("description", ""),
                                    "updated_on": r.get("sys_updated_on"),
                                    "created_on": r.get("sys_created_on"),
                                }
                        logger.info(f"Retrieved {len(root_sys_ids)} active root flows.")
                else:
                    logger.error(
                        f"Failed fetching all flows: {resp.response.status_code} - {resp.response.text}"
                    )
            else:
                for ident in flow_identifiers:
                    logger.debug(f"Looking up sys_id for flow identifier: {ident}")
                    resp = self.get_table(
                        table="sys_hub_flow",
                        sysparm_query=f"name={ident}^ORsys_id={ident}",
                        sysparm_limit="1",
                        sysparm_fields="sys_id,name,active,flow_type,description,sys_scope,application,sys_domain,sys_updated_on,sys_created_on",
                        sysparm_display_value="true",
                    )
                    if resp.response.ok:
                        results = resp.response.json().get("result", [])
                        if results:
                            raw = results[0] if isinstance(results, list) else results
                            sid = raw.get("sys_id")
                            if sid:
                                logger.info(
                                    f"Found sys_id {sid} for identifier {ident}"
                                )
                                root_sys_ids.append(sid)

                                def get_val(item, key, default=""):
                                    v = item.get(key)
                                    if isinstance(v, dict):
                                        return v.get(
                                            "display_value", v.get("value", default)
                                        )
                                    return v if v is not None else default

                                initial_metadata[sid] = {
                                    "sys_id": sid,
                                    "name": get_val(raw, "name", "Unnamed Flow"),
                                    "domain": get_val(raw, "sys_domain"),
                                    "scope": get_val(raw, "sys_scope"),
                                    "application": get_val(
                                        raw, "application", "Global"
                                    ),
                                    "active": str(raw.get("active", False)).lower()
                                    == "true",
                                    "flow_type": raw.get("flow_type", "flow"),
                                    "description": raw.get("description", ""),
                                    "updated_on": raw.get("sys_updated_on"),
                                    "created_on": raw.get("sys_created_on"),
                                }
                            else:
                                logger.warning(
                                    f"Result for {ident} had no sys_id: {results}"
                                )
                        else:
                            logger.warning(f"No results found for {ident}")
                    else:
                        logger.error(
                            f"Failed finding sys_id for {ident}: {resp.response.status_code} - {resp.response.text}"
                        )

            if not root_sys_ids:
                logger.warning(
                    "No flows found matching your identifiers. Exiting tool."
                )
                return FlowReportResult(
                    markdown_content="No flows found matching your identifiers.",
                    file_path=None,
                    summary="0 flows found.",
                    root_flow_sys_ids=[],
                )

            logger.info(f"Collecting graph for {len(root_sys_ids)} root sys_ids")
            graph, all_metadata = self.collect_graph_for_roots(
                root_sys_ids, max_depth=max_depth, initial_metadata=initial_metadata
            )

            mermaid_blocks = []
            if segment_by_root:
                logger.info(f"Segmenting report by root ({len(root_sys_ids)} roots)")
                for rid in root_sys_ids:
                    logger.debug(f"Extracting subgraph for root: {rid}")
                    sub_graph = _api_client.get_reachable_subgraph(graph, rid)
                    if sub_graph.nodes:
                        comp_mermaid = _api_client.graph_to_mermaid_multi(
                            sub_graph, [rid], all_metadata
                        )
                        mermaid_blocks.append(comp_mermaid)
            else:
                logger.info("Splitting global graph into disjoint components")
                components = _api_client.find_connected_components(graph)
                logger.info(
                    f"Found {len(components)} standalone graph component groups"
                )
                for idx, comp in enumerate(components):
                    logger.debug(f"Generating syntax for component {idx}")
                    comp_mermaid = _api_client.graph_to_mermaid_multi(
                        comp, root_sys_ids, all_metadata
                    )
                    mermaid_blocks.append(comp_mermaid)

            combined_mermaid = "|||BLOCK_SEP|||".join(mermaid_blocks)

            logger.info("Building polished markdown")
            markdown_content = _api_client.build_polished_markdown(
                graph, all_metadata, root_sys_ids, combined_mermaid
            )

            file_path = None
            if save_to_file:
                if destination_file:
                    file_path = str(Path(destination_file).resolve())
                else:
                    dir_path = Path(output_dir)
                    dir_path.mkdir(parents=True, exist_ok=True)
                    filename = (
                        f"{mermaid_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    )
                    file_path = str((dir_path / filename).resolve())

                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                logger.info(f"Saved report to: {file_path}")
                summary = f"✅ Report saved to: {file_path} ({len(all_metadata)} flows documented)"
            else:
                summary = f"✅ Markdown generated ({len(all_metadata)} flows) — copy the content below"

            return FlowReportResult(
                markdown_content=markdown_content,
                file_path=file_path,
                summary=summary,
                root_flow_sys_ids=root_sys_ids,
            )
        except Exception as e:
            logger.error(
                f"An error occurred during workflow_to_mermaid processing: {e}",
                exc_info=True,
            )
            return FlowReportResult(
                markdown_content=f"An error occurred generating the report: {e}",
                file_path=None,
                summary=f"Failed with error: {e}",
                root_flow_sys_ids=[],
            )
