#!/usr/bin/python

import base64
import gzip
import json
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.exceptions import (
    MissingParameterError,
)
from pydantic import ValidationError

from servicenow_api.servicenow_models import (
    ChangeManagementModel,
    ChangeRequest,
    FlowGraph,
    Response,
    Task,
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


class ServiceNowApiChange(ServiceNowApiBase):
    def get_change_requests(self, **kwargs) -> Response:
        """
        Retrieve change requests based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: str or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: Response containing list of parsed Pydantic models with information about change requests.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        :raises ParameterError: If unexpected response format is encountered.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            change_requests_data = []

            if change_request.change_type:
                change_type = f"/{change_request.change_type}"
            else:
                change_type = ""

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_requests_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change{change_type}",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    change_requests_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_requests_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(response=first_response, result=change_requests_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_nextstate(self, **kwargs) -> Response:
        """
        Retrieve the next state of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the next state.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/nextstate",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_schedule(self, **kwargs) -> Response:
        """
        Retrieve the schedule of a change request based on CI sys ID.

        :param cmdb_ci_sys_id: Sys ID of the CI (Configuration Item).
        :type cmdb_ci_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the change request schedule.
        :rtype: Response

        :raises MissingParameterError: If cmdb_ci_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.cmdb_ci_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/ci/{change_request.cmdb_ci_sys_id}/schedule",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_tasks(self, **kwargs) -> Response:
        """
        Retrieve tasks associated with a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: str or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about change request tasks.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            tasks_data = []

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                tasks_data.extend([Task.model_validate(item) for item in result_data])

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    tasks_data.extend(
                        [Task.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                tasks_data.extend([Task.model_validate(item) for item in result_data])

            return Response(response=first_response, result=tasks_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request(self, **kwargs) -> Response:
        """
        Retrieve details of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            if change_request.change_type in ["emergency", "normal", "standard"]:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_type}/{change_request.change_request_sys_id}"
            else:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}"
            response = self._session.get(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_ci(self, **kwargs) -> Response:
        """
        Retrieve the configuration item (CI) associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the associated CI.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/ci",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_conflict(self, **kwargs) -> Response:
        """
        Retrieve conflict information associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the conflicts.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_standard_change_request_templates(self, **kwargs) -> Response:
        """
        Retrieve standard change request templates based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: str or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about standard change request templates.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            standard_change_templates_data = []

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/standard/template",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                standard_change_templates_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/standard/template",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    standard_change_templates_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/standard/template",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                standard_change_templates_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(
                response=first_response, result=standard_change_templates_data
            )
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_models(self, **kwargs) -> Response:
        """
        Retrieve change request models based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: str or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about change request models.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            change_models_data = []
            if change_request.change_type:
                change_type = f"/{change_request.change_type}"
            else:
                change_type = ""

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_models_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    change_models_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_models_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(response=first_response, result=change_models_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_standard_change_request_model(self, **kwargs) -> Response:
        """
        Retrieve details of a standard change request model.

        :param model_sys_id: Sys ID of the standard change request model.
        :type model_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the standard change request model.
        :rtype: Response

        :raises MissingParameterError: If model_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.model_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/model/{change_request.model_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_standard_change_request_template(self, **kwargs) -> Response:
        """
        Retrieve details of a standard change request template.

        :param template_sys_id: Sys ID of the standard change request template.
        :type template_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the standard change request template.
        :rtype: Response

        :raises MissingParameterError: If template_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.template_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/standard/template/{change_request.template_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_change_request_worker(self, **kwargs) -> Response:
        """
        Retrieve details of a change request worker.

        :param worker_sys_id: Sys ID of the change request worker.
        :type worker_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the change request worker.
        :rtype: Response

        :raises MissingParameterError: If worker_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.worker_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/worker/{change_request.worker_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def create_change_request(self, **kwargs) -> Response:
        """
        Create a new change request.

        :param name_value_pairs: Name-value pairs providing details for the new change request.
        :type name_value_pairs: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None
        :param standard_change_template_id: Sys ID of the standard change request template (if applicable).
        :type standard_change_template_id: str or None

        :return: Response containing parsed Pydantic model with information about the created change request.
        :rtype: Response

        :raises MissingParameterError: If name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.data is None:
                raise MissingParameterError
            standard_change_template_id = (
                f"/{change_request.standard_change_template_id}"
                if change_request.standard_change_template_id
                else ""
            )
            change_type = (
                f"/{change_request.change_type}" if change_request.change_type else ""
            )
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def create_change_request_task(self, **kwargs) -> Response:
        """
        Create a new task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param data: Name-value pairs providing details for the new task.
        :type data: dict or None

        :return: Response containing parsed Pydantic model with information about the created task.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/task",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def create_change_request_ci_association(self, **kwargs) -> Response:
        """
        Create associations between a change request and configuration items (CIs).

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param cmdb_ci_sys_ids: List of Sys IDs of CIs to associate with the change request.
        :type cmdb_ci_sys_ids: list or None
        :param association_type: Type of association (affected, impacted, offering).
        :type association_type: str or None
        :param refresh_impacted_services: Flag to refresh impacted services (applicable for 'affected' association).
        :type refresh_impacted_services: bool or None

        :return: Response containing parsed Pydantic model with information about the created associations.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id, cmdb_ci_sys_ids, or association_type is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If association_type is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.cmdb_ci_sys_ids is None
                or change_request.association_type is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/ci",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def calculate_standard_change_request_risk(self, **kwargs) -> Response:
        """
        Calculate and update the risk of a standard change request.

        :param change_request_sys_id: Sys ID of the standard change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the calculated risk.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/standard/{change_request.change_request_sys_id}/risk",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_change_request_conflict(self, **kwargs) -> Response:
        """
        Check for conflicts in a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about conflicts.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def refresh_change_request_impacted_services(self, **kwargs) -> Response:
        """
        Refresh impacted services for a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the refreshed impacted services.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/refresh_impacted_services",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def approve_change_request(self, **kwargs) -> Response:
        """
        Approve or reject a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param state: State to set the change request to (approved or rejected).
        :type state: str or None

        :return: Response containing parsed Pydantic model with information about the approval/rejection.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or state is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If state is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.state is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/approvals",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def update_change_request(self, **kwargs) -> Response:
        """
        Update details of a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the change request.
        :type name_value_pairs: str or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the updated change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            change_type = (
                f"/{change_request.change_type}" if change_request.change_type else ""
            )
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change{change_type}/{change_request.change_request_sys_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def update_change_request_first_available(self, **kwargs) -> Response:
        """
        Update the schedule of a change request to the first available slot.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the updated schedule.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/schedule/first_available",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def update_change_request_task(self, **kwargs) -> Response:
        """
        Update details of a task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_request_task_sys_id: Sys ID of the change request task.
        :type change_request_task_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the task.
        :type name_value_pairs: str or None

        :return: Response containing parsed Pydantic model with information about the updated task.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id, change_request_task_sys_id, or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.change_request_task_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task/{change_request.change_request_task_sys_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_change_request(self, **kwargs) -> Response:
        """
        Delete a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the deleted change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            if change_request.change_type in ["emergency", "normal", "standard"]:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_type}/{change_request.change_request_sys_id}"
            else:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}"
            response = self._session.delete(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_change_request_task(self, **kwargs) -> Response:
        """
        Delete a task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param task_sys_id: Sys ID of the task associated with the change request.
        :type task_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the deleted task.
        :rtype: Response

        :raises MissingParameterError: If either change_request_sys_id or task_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.task_sys_id is None
            ):
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task/{change_request.task_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_change_request_conflict_scan(self, **kwargs) -> Response:
        """
        Delete conflict scan information associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param task_sys_id: Sys ID of the task associated with the change request.
        :type task_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the deleted conflict scan.
        :rtype: Response

        :raises MissingParameterError: If either change_request_sys_id or task_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.task_sys_id is None
            ):
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise
