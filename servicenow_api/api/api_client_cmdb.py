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
    CMDB,
    CILifecycleActionRequest,
    CILifecycleResult,
    CMDBIngestModel,
    CMDBInstanceModel,
    CMDBModel,
    FlowEdge,
    FlowGraph,
    FlowNode,
    Response,
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


class ServiceNowApiCmdb(ServiceNowApiBase):
    def get_cmdb(self, **kwargs) -> Response:
        """
        Get Configuration Management Database (CMDB) information based on specified parameters.

        :param cmdb_id: The unique identifier of the CMDB record
        :type cmdb_id: str

        :return: Response containing parsed Pydantic model with CMDB information.
        :rtype: Response

        :raises ParameterError: If the provided parameters are invalid.
        """
        try:
            cmdb = CMDBModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/cmdb/meta/{cmdb.cmdb_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CMDB.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_cmdb_relation(self, **kwargs) -> Response:
        """
        Deletes the relation for the specified configuration item (CI).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param rel_sys_id: Sys_id of the relation to remove.
        :type rel_sys_id: str

        :return: Response containing the operation result.
        :rtype: Response

        :raises MissingParameterError: If className, sys_id, or rel_sys_id is not provided.
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.rel_sys_id is None:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}/relation/{cmdb.rel_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            if response.content:
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                return Response(response=response, result=result_data)
            return Response(response=response, result={"status": "deleted"})
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_cmdb_instances(self, **kwargs) -> Response:
        """
        Returns the available configuration items (CI) for a specified CMDB class.

        :param className: CMDB class name.
        :type className: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int or str
        :param sysparm_offset: Starting record index.
        :type sysparm_offset: int or str
        :param sysparm_query: Encoded query used to filter the result set.
        :type sysparm_query: str

        :return: Response containing list of CIs.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}",
                params=cmdb.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_cmdb_instance(self, **kwargs) -> Response:
        """
        Returns attributes and relationship information for a specified CI record.

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI record to retrieve.
        :type sys_id: str

        :return: Response containing parsed Pydantic model with CI information.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def create_cmdb_instance(self, **kwargs) -> Response:
        """
        Creates a single configuration item (CI).

        :param className: CMDB class name.
        :type className: str
        :param attributes: Data attributes to define in the CI record.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str
        :param inbound_relations: List of inbound relations.
        :type inbound_relations: list
        :param outbound_relations: List of outbound relations.
        :type outbound_relations: list

        :return: Response containing created CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def update_cmdb_instance(self, **kwargs) -> Response:
        """
        Updates the specified CI record (PUT).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param attributes: Data attributes to replace.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.put(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def patch_cmdb_instance(self, **kwargs) -> Response:
        """
        Replaces attributes in the specified CI record (PATCH).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param attributes: Data attributes to replace.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.patch(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def create_cmdb_relation(self, **kwargs) -> Response:
        """
        Adds an inbound and/or outbound relation to the specified CI.

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param inbound_relations: List of inbound relations.
        :type inbound_relations: list
        :param outbound_relations: List of outbound relations.
        :type outbound_relations: list
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI relations.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}/relation",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def ingest_cmdb_data(self, **kwargs) -> Response:
        """
        Inserts records into the Import Set table associated with the data source.

        :param data_source_sys_id: Sys_id of the data source record.
        :type data_source_sys_id: str
        :param records: Array of objects to ingest.
        :type records: list

        :return: Response containing ingestion result.
        :rtype: Response
        """
        try:
            ingest = CMDBIngestModel(**kwargs)
            if ingest.data_source_sys_id is None or ingest.records is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/ingest/{ingest.data_source_sys_id}",
                headers=self.headers,
                json=ingest.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            if response.status_code not in [201, 202]:
                response.raise_for_status()

            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_ci_lifecycle_action(self, **kwargs) -> Response:
        """
        Removes a configuration item (CI) action for a list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.actionName or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            response = self._session.delete(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def unregister_ci_lifecycle_operator(self, **kwargs) -> Response:
        """
        Unregisters an operator for non-workflow users.
        """
        try:
            req_id = kwargs.get("req_id")
            if not req_id:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/api/now/cilifecyclemgmt/operators/{req_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_ci_lifecycle_active_actions(self, **kwargs) -> Response:
        """
        Returns a list of active CI actions for the specified CI.
        """
        try:
            sys_id = kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions/{sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_ci_lifecycle_compat_actions(self, **kwargs) -> Response:
        """
        Determines whether two specified CI actions are compatible.
        """
        try:
            actionName = kwargs.get("actionName")
            otherActionName = kwargs.get("otherActionName")
            if not actionName or not otherActionName:
                raise MissingParameterError

            params = {"actionName": actionName, "otherActionName": otherActionName}
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/compatActions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_ci_lifecycle_lease_expired(self, **kwargs) -> Response:
        """
        Determines whether the lease has expired for the requester.
        """
        try:
            sys_id = kwargs.get("sys_id")
            actionName = kwargs.get("actionName")
            requestorId = kwargs.get("requestorId")
            if not sys_id or not actionName or not requestorId:
                raise MissingParameterError

            params = {"actionName": actionName, "requestorId": requestorId}
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/leases/{sys_id}/expired",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_ci_lifecycle_not_allowed_action(self, **kwargs) -> Response:
        """
        Determines whether a specified CI action is not allowed.
        """
        try:
            actionName = kwargs.get("actionName")
            ciClass = kwargs.get("ciClass")
            opsLabel = kwargs.get("opsLabel")
            if not actionName or not ciClass or not opsLabel:
                raise MissingParameterError

            params = {
                "actionName": actionName,
                "ciClass": ciClass,
                "opsLabel": opsLabel,
            }
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/notAllowedAction",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_ci_lifecycle_not_allowed_ops_transition(self, **kwargs) -> Response:
        """
        Determines whether an operational state transition is allowed.
        """
        try:
            ciClass = kwargs.get("ciClass")
            opsLabel = kwargs.get("opsLabel")
            transitionOpsLabel = kwargs.get("transitionOpsLabel")
            if not ciClass or not opsLabel or not transitionOpsLabel:
                raise MissingParameterError

            params = {
                "ciClass": ciClass,
                "opsLabel": opsLabel,
                "transitionOpsLabel": transitionOpsLabel,
            }
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/notAllowedOpsTransition",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_ci_lifecycle_requestor_valid(self, **kwargs) -> Response:
        """
        Determines whether the specified user is a valid requester.
        """
        try:
            req_id = kwargs.get("req_id")
            if not req_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/requestors/{req_id}/valid",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_ci_lifecycle_status(self, **kwargs) -> Response:
        """
        Returns the current operational state for the specified CI.
        """
        try:
            sys_id = kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/statuses/{sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def extend_ci_lifecycle_lease(self, **kwargs) -> Response:
        """
        Extends the specified CI action's lease expiration time.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            sys_id = kwargs.get("sys_id")
            if (
                not sys_id
                or not req.actionName
                or not req.leaseTime
                or not req.requestorId
            ):
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "leaseTime": req.leaseTime,
                "requestorId": req.requestorId,
            }
            response = self._session.patch(
                url=f"{self.url}/api/now/cilifecyclemgmt/leases/{sys_id}",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def add_ci_lifecycle_action(self, **kwargs) -> Response:
        """
        Adds a specified CI action to a specified list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.actionName or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            if req.leaseTime:
                params["leaseTime"] = req.leaseTime
            if req.oldActionNames:
                params["oldActionNames"] = req.oldActionNames

            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def register_ci_lifecycle_operator(self, **kwargs) -> Response:
        """
        Registers an operator for a non-workflow user.
        """
        try:
            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/operators",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def set_ci_lifecycle_status(self, **kwargs) -> Response:
        """
        Sets the operational state for a specified list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.opsLabel or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "opsLabel": req.opsLabel,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            if req.oldOpsLabels:
                params["oldOpsLabels"] = req.oldOpsLabels

            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/statuses",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def collect_graph_for_roots(
        self,
        root_sys_ids: list[str],
        max_depth: int = 5,
        initial_metadata: dict[str, dict[str, Any]] = None,
    ) -> tuple[FlowGraph, dict[str, dict[str, Any]]]:
        all_nodes: list[FlowNode] = []
        all_edges: list[FlowEdge] = []
        visited: dict[str, str] = {}
        root_nodes: dict[str, str] = {}
        all_metadata: dict[str, dict[str, Any]] = {}

        if initial_metadata:
            all_metadata.update(initial_metadata)

        def recurse(
            flow_sys_id: str, prefix: str = "", depth: int = 0, is_root: bool = False
        ) -> str | None:
            if depth > max_depth:
                logger.warning(f"Max depth {max_depth} reached at flow {flow_sys_id}")
                return None
            if flow_sys_id in visited:
                logger.debug(
                    f"Already visited flow {flow_sys_id}, returning its trigger_id"
                )
                return visited[flow_sys_id]

            if flow_sys_id in all_metadata:
                meta = all_metadata[flow_sys_id]
            else:
                meta = self.get_flow_metadata(flow_sys_id)
                if meta:
                    all_metadata[flow_sys_id] = meta

            if not meta:
                logger.warning(f"Could not retrieve metadata for flow {flow_sys_id}")
                return None

            flow_name = meta.get("name", "Unnamed")

            actions = []
            for tbl in ["sys_hub_action_instance_v2", "sys_hub_action_instance"]:
                resp = self.get_table(
                    table=tbl,
                    sysparm_query=f"flow={flow_sys_id}^ORDERBYorder",
                    sysparm_fields="sys_id,name,order,values,action,action_type,comment,display_text",
                    sysparm_limit=500,
                    sysparm_display_value="true",
                )
                if resp.response.ok:
                    results = resp.response.json().get("result", [])
                    if results:
                        actions = results if isinstance(results, list) else [results]
                        logger.debug(
                            f"Found {len(actions)} actions for flow {flow_sys_id} in table {tbl}"
                        )
                        break
                else:
                    logger.warning(
                        f"Failed fetching actions from table {tbl} for flow {flow_sys_id}: {resp.response.status_code} - {resp.response.text}"
                    )

            nodes: list[FlowNode] = []
            edges: list[FlowEdge] = []
            prev_id: str | None = None

            trigger_id = f"{prefix}trigger_{flow_sys_id[:8]}"
            visited[flow_sys_id] = trigger_id

            desc = meta.get("description", "")
            app = meta.get("application", "Global")
            scope = meta.get("scope", "Global")

            trigger_label = f"FLOW: {flow_name}" if is_root else f"SUBFLOW: {flow_name}"
            trigger_label += f"<br/><i>{flow_sys_id}</i>"
            if desc:
                trunc_desc = desc[:100] + "..." if len(desc) > 100 else desc
                trigger_label += f"<br/>{trunc_desc}"
            trigger_label += f"<br/>App: {app} | Scope: {scope}"

            nodes.append(FlowNode(id=trigger_id, label=trigger_label, type="trigger"))
            prev_id = trigger_id
            if is_root:
                root_nodes[flow_sys_id] = trigger_id

            for action in actions:
                act_id = f"{prefix}{action.get('sys_id', '')}"
                decoded = decode_values(action.get("values"))
                node_type = determine_node_type(action, decoded)

                step_name = action.get("name", "")
                if step_name.lower() in ["step", "action"]:
                    step_name = ""

                action_ref = action.get("action_type", {})
                if not action_ref:
                    action_ref = action.get("action", {})

                action_type_label = (
                    action_ref.get("display_value")
                    if isinstance(action_ref, dict)
                    else action_ref
                ) or "Action"

                comment = action.get("comment", "")
                display_text = action.get("display_text", "")

                action_sys_id = action.get("sys_id", "N/A")

                main_title = step_name if step_name else action_type_label
                label = f"<b>{main_title}</b>"

                if display_text and display_text.lower() != main_title.lower():
                    label += f"<br/>{display_text}"
                elif comment and comment.lower() != main_title.lower():
                    label += f"<br/>{comment}"

                extra_details = extract_action_details(decoded, action_type_label)
                for detail in extra_details:
                    if all(
                        d.split(": ")[1].lower() not in label.lower()
                        for d in [detail]
                        if ": " in d
                    ):
                        label += f"<br/>{detail}"

                if step_name and action_type_label.lower() != step_name.lower():
                    label += f"<br/>({action_type_label})"

                label += f"<br/><small>{action_sys_id}</small>"

                sub_id = find_subflow_sys_id(decoded)
                if sub_id:
                    sub_meta = self.get_flow_metadata(sub_id)
                    if sub_meta:
                        sub_name = sub_meta.get("name", "Unnamed Subflow")
                        label = f"{label} -> CALL SUBFLOW: {sub_name}"

                nodes.append(
                    FlowNode(
                        id=act_id,
                        label=label,
                        type=node_type,
                        action_name=step_name,
                    )
                )

                if prev_id:
                    edges.append(FlowEdge(from_id=prev_id, to_id=act_id))

                if sub_id:
                    sub_trigger = recurse(
                        sub_id, f"sub_{sub_id[:8]}_", depth + 1, is_root=False
                    )
                    if sub_trigger:
                        edges.append(
                            FlowEdge(from_id=act_id, to_id=sub_trigger, label="calls")
                        )

                if node_type == "decision" and len(edges) > 0:
                    edges[-1].label = "condition"

                prev_id = act_id

            all_nodes.extend(nodes)
            all_edges.extend(edges)
            return trigger_id

        for root_id in root_sys_ids:
            recurse(root_id, prefix=f"root_{root_id[:8]}_", depth=0, is_root=True)

        return (
            FlowGraph(
                nodes=all_nodes,
                edges=all_edges,
                summary=f"{len(root_sys_ids)} root flows + subflows",
            ),
            all_metadata,
        )
