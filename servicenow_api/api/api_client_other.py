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
    ParameterError,
)
from pydantic import ValidationError

from servicenow_api.servicenow_models import (
    CICD,
    AccountModel,
    ActivitySubscriptionModel,
    ApplicationServiceModel,
    Attachment,
    AttachmentModel,
    BatchRequest,
    BatchResponse,
    CheckServiceQualificationRequest,
    CICDModel,
    CMDBService,
    CostPlan,
    DataClassificationModel,
    FlowGraph,
    HRProfileModel,
    ImportSet,
    ImportSetModel,
    MetricBaseTimeSeriesModel,
    ProductInventory,
    ProductInventoryQueryParams,
    ProjectTask,
    Response,
    ServiceQualificationItem,
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


class ServiceNowApiOther(ServiceNowApiBase):
    def get_application(self, **kwargs) -> Response:
        """
        Get information about an application.

        :param application_id: The unique identifier of the application.
        :type application_id: str

        :return: Response containing parsed Pydantic model with information about the application.
        :rtype: Response

        :raises MissingParameterError: If the required parameter `application_id` is not provided.
        """
        try:
            application = ApplicationServiceModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/cmdb/app_service/{application.application_id}/getContent",
                params=application.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CMDBService.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def batch_request(self, **kwargs) -> Response:
        """
        Sends multiple REST API requests in a single call.

        :param batch_request_id: ID that identifies the batch of requests.
        :type batch_request_id: str
        :param rest_requests: List of request objects to include in the batch request.
        :type rest_requests: list

        :return: Response containing the batch results.
        :rtype: Response
        """
        try:
            batch = BatchRequest(**kwargs)
            if batch.rest_requests is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/api/now/v1/batch",
                headers=self.headers,
                json=batch.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            return Response(
                response=response, result=BatchResponse.model_validate(json_response)
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def batch_install_result(self, **kwargs) -> Response:
        """
        Get the result of a batch installation based on the provided result ID.

        :param result_id: The ID associated with the batch installation result.
        :type result_id: str

        :return: Response containing parsed Pydantic model with batch installation result.
        :rtype: Response

        :raises MissingParameterError: If result_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.result_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/app/batch/results/{cicd.result_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def instance_scan_progress(self, **kwargs) -> Response:
        """
        Get progress information for an instance scan based on the provided progress ID.

        :param progress_id: The ID associated with the instance scan progress.
        :type progress_id: str

        :return: Response containing parsed Pydantic model with instance scan progress.
        :rtype: Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.progress_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/instance_scan/result/{cicd.progress_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def progress(self, **kwargs) -> Response:
        """
        Get progress information based on the provided progress ID.

        :param progress_id: The ID associated with the progress.
        :type progress_id: str

        :return: Response containing parsed Pydantic model with progress information.
        :rtype: Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.progress_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/progress/{cicd.progress_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def batch_install(self, **kwargs) -> Response:
        """
        Initiate a batch installation with the provided parameters.

        :param name: The name of the batch installation.
        :type name: str
        :param notes: Additional notes for the batch installation.
        :type notes: str
        :param packages: The packages to be installed in the batch.
        :type packages: str

        :return: Response containing parsed Pydantic model with information about the batch installation.
        :rtype: Response

        :raises MissingParameterError: If name or packages are not provided.
        :raises ParameterError: If notes is not a string.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.name is None or cicd.packages is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app/batch/install",
                headers=self.headers,
                verify=self.verify,
                json=cicd.data,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def batch_rollback(self, **kwargs) -> Response:
        """
        Rollback a batch installation based on the provided rollback ID.

        :param rollback_id: The ID associated with the batch rollback.
        :type rollback_id: str

        :return: Response containing parsed Pydantic model with information about the batch rollback.
        :rtype: Response

        :raises MissingParameterError: If rollback_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.rollback_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/app/batch/rollback/{cicd.rollback_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def full_scan(self) -> Response:
        """
        Initiate a full instance scan.

        :return: Response containing parsed Pydantic model with information about the full scan.
        :rtype: Response
        """
        try:
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/full_scan",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid response data: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def point_scan(self, **kwargs) -> Response:
        """
        Initiate a point instance scan based on the provided parameters.

        :param target_sys_id: The sys_id of the target instance.
        :type target_sys_id: str
        :param target_table: The table of the target instance.
        :type target_table: str

        :return: Response containing parsed Pydantic model with information about the point scan.
        :rtype: Response

        :raises MissingParameterError: If target_sys_id or target_table is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.target_sys_id is None or cicd.target_table is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/point_scan",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def combo_suite_scan(self, **kwargs) -> Response:
        """
        Initiate a suite scan for a combo based on the provided combo_sys_id.

        :param combo_sys_id: The sys_id of the combo to be scanned.
        :type combo_sys_id: str

        :return: Response containing parsed Pydantic model with information about the combo suite scan.
        :rtype: Response

        :raises MissingParameterError: If combo_sys_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.combo_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/suite_scan/combo/{cicd.combo_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def suite_scan(self, **kwargs) -> Response:
        """
        Initiate a suite scan based on the provided suite_sys_id and sys_ids.

        :param suite_sys_id: The sys_id of the suite to be scanned.
        :type suite_sys_id: str
        :param sys_ids: List of sys_ids representing app_scope_sys_ids for the suite scan.
        :type sys_ids: list
        :param scan_type: Type of scan to be performed (default is "scoped_apps").
        :type scan_type: str

        :return: Response containing parsed Pydantic model with information about the suite scan.
        :rtype: Response

        :raises MissingParameterError: If suite_sys_id or sys_ids is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.suite_sys_id is None or cicd.app_scope_sys_ids is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/suite_scan/{cicd.suite_sys_id}/{cicd.scan_type}",
                headers=self.headers,
                json=cicd.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def apply_remote_source_control_changes(self, **kwargs) -> Response:
        """
        Apply remote source control changes based on the provided parameters.

        :param app_sys_id: The sys_id of the application for which changes should be applied.
        :type app_sys_id: str
        :param scope: The scope of the changes.
        :type scope: str
        :param branch_name: The name of the branch containing the changes.
        :type branch_name: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool

        :return: Response containing parsed Pydantic model with information about the applied changes.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.app_sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/sc/apply_changes",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def run_test_suite(self, **kwargs) -> Response:
        """
        Run a test suite based on the provided parameters.

        :param test_suite_sys_id: The sys_id of the test suite to be run.
        :type test_suite_sys_id: str
        :param test_suite_name: The name of the test suite to be run.
        :type test_suite_name: str
        :param browser_name: The name of the browser for the test run.
        :type browser_name: str
        :param browser_version: The version of the browser for the test run.
        :type browser_version: str
        :param os_name: The name of the operating system for the test run.
        :type os_name: str
        :param os_version: The version of the operating system for the test run.
        :type os_version: str

        :return: Response containing parsed Pydantic model with information about the test run.
        :rtype: Response

        :raises MissingParameterError: If test_suite_sys_id or test_suite_name is not provided.
        :raises ParameterError: If browser_name is not a valid string.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.test_suite_sys_id is None and cicd.test_suite_name is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/testsuite/run",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_import_set(self, **kwargs) -> Response:
        """
        Get details of a specific import set record.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param import_set_sys_id: The sys_id of the import set record.
        :type import_set_sys_id: str

        :return: Response containing parsed Pydantic model with information about the import set record.
        :rtype: Response

        :raises ParameterError: If import_set_sys_id or table is not provided.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.import_set_sys_id is None or import_set.table is None:
                raise ParameterError
            response = self._session.get(
                url=f"{self.url}/now/import/{import_set.table}/{import_set.import_set_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ImportSet.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def insert_import_set(self, **kwargs) -> Response:
        """
        Insert a new record into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for the new import set record.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the inserted import set record.
        :rtype: Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.data is None or import_set.table is None:
                raise ParameterError
            response = self._session.post(
                url=f"{self.url}/now/import/{import_set.table}",
                headers=self.headers,
                json=import_set.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ImportSet.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def insert_multiple_import_sets(self, **kwargs) -> Response:
        """
        Insert multiple records into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for multiple new import set records.
        :type data: dict

        :return: Response containing list of parsed Pydantic models with information about the inserted import set records.
        :rtype: Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.data is None or import_set.table is None:
                raise ParameterError
            response = self._session.post(
                url=f"{self.url}/now/import/{import_set.table}/insertMultiple",
                headers=self.headers,
                json=import_set.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [ImportSet.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_data_classification(self, **kwargs) -> Response:
        try:
            dc = DataClassificationModel(**kwargs)
            url = f"{self.url}/now/data_classification/classification"
            if dc.sys_id:
                url = f"{url}/{dc.sys_id}"

            response = self._session.get(
                url=url,
                headers=self.headers,
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

    def get_attachment(self, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/attachment/{att.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=Attachment.model_validate(response.json().get("result")),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def upload_attachment(self, file_path: str, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.table_name or not att.table_sys_id or not att.file_name:
                raise MissingParameterError

            with open(file_path, "rb") as f:
                headers = self.headers.copy()
                headers.pop("Content-Type", None)

                params = {
                    "table_name": att.table_name,
                    "table_sys_id": att.table_sys_id,
                    "file_name": att.file_name,
                }

                response = self._session.post(
                    url=f"{self.url}/now/attachment/file",
                    headers=headers,
                    params=params,
                    data=f,
                    verify=self.verify,
                    proxies=self.proxies,
                )
            response.raise_for_status()
            return Response(
                response=response,
                result=Attachment.model_validate(response.json().get("result")),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_attachment(self, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.sys_id:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/now/attachment/{att.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result={"status": "deleted"})
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_activity_subscriptions(self, **kwargs) -> Response:
        try:
            sub = ActivitySubscriptionModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/now/ui/activity_subscription",
                headers=self.headers,
                params=sub.api_parameters,
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

    def get_account(self, **kwargs) -> Response:
        try:
            acc = AccountModel(**kwargs)
            url = f"{self.url}/now/csm/account"
            if acc.sys_id:
                url = f"{url}/{acc.sys_id}"
            response = self._session.get(
                url=url,
                headers=self.headers,
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

    def get_hr_profile(self, **kwargs) -> Response:
        try:
            hr = HRProfileModel(**kwargs)
            url = f"{self.url}/now/hr/profile"
            if hr.sys_id:
                url = f"{url}/{hr.sys_id}"

            response = self._session.get(
                url=url,
                headers=self.headers,
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

    def metricbase_insert(self, **kwargs) -> Response:
        try:
            mb = MetricBaseTimeSeriesModel(**kwargs)
            response = self._session.post(
                url=f"{self.url}/now/metricbase/insert",
                headers=self.headers,
                json=mb.model_dump(exclude_none=True),
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

    def check_service_qualification(self, **kwargs) -> Response:
        """
        Creates a technical service qualification request.
        """
        try:
            req = CheckServiceQualificationRequest(**kwargs)
            payload = req.model_dump(exclude_none=True, by_alias=True)

            response = self._session.post(
                url=f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification",
                headers=self.headers,
                json=payload,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            return Response(
                response=response,
                result=CheckServiceQualificationRequest.model_validate(response.json()),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_service_qualification(self, **kwargs) -> Response:
        """
        Retrieves a technical qualification request by ID or list all.
        """
        try:
            sys_id = kwargs.get("id") or kwargs.get("sys_id")

            if sys_id:
                url = f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification/{sys_id}"
                params: dict[str, Any] = {}
            else:
                url = f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification"
                params = {
                    k: v
                    for k, v in kwargs.items()
                    if k
                    in [
                        "state",
                        "description",
                        "qualificationResult",
                        "limit",
                        "offset",
                    ]
                }

            response = self._session.get(
                url=url,
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list):
                result = [
                    CheckServiceQualificationRequest.model_validate(item)
                    for item in data
                ]
            else:
                result = CheckServiceQualificationRequest.model_validate(data)

            return Response(response=response, result=result)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def process_service_qualification_result(self, **kwargs) -> Response:
        """
        Processes a technical service qualification result.
        """
        try:
            items = kwargs.get("serviceQualificationItem")
            if not items:
                raise MissingParameterError("serviceQualificationItem is required")

            valid_items = [
                ServiceQualificationItem(**item) if isinstance(item, dict) else item
                for item in items
            ]

            payload = {
                "serviceQualificationItem": [
                    item.model_dump(exclude_none=True, by_alias=True)
                    for item in valid_items
                ],
                "description": kwargs.get("description"),
                "@type": "CheckServiceQualification",
            }

            response = self._session.post(
                url=f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification/processResult",
                headers=self.headers,
                json=payload,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CheckServiceQualificationRequest.model_validate(response.json()),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def insert_cost_plans(self, plans: list[dict[str, Any]], **kwargs) -> Response:
        """
        Creates cost plans.
        """
        try:
            valid_plans = [CostPlan(**p) for p in plans]
            payload = [p.model_dump() for p in valid_plans]

            response = self._session.post(
                url=f"{self.url}/api/now/ppm/insert_cost_plans",
                headers=self.headers,
                json=payload,
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

    def insert_project_tasks(self, **kwargs) -> Response:
        """
        Creates a project and associated project tasks.
        """
        try:
            project = ProjectTask(**kwargs)

            response = self._session.post(
                url=f"{self.url}/api/now/ppm/insert_project_tasks",
                headers=self.headers,
                json=project.model_dump(exclude_none=True),
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

    def get_product_inventory(self, **kwargs) -> Response:
        """
        Retrieves a list of all product inventories.
        """
        try:
            qp = ProductInventoryQueryParams(**kwargs)
            params = qp.model_dump(exclude_none=True)

            if qp.place_id:
                params.pop("place_id")
                params["place"] = str({"id": qp.place_id}).replace("'", '"')

            response = self._session.get(
                url=f"{self.url}/api/sn_prd_invt/product",
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list):
                result = [ProductInventory.model_validate(item) for item in data]
            else:
                result = ProductInventory.model_validate(data)

            return Response(response=response, result=result)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def delete_product_inventory(self, **kwargs) -> Response:
        """
        Deletes a specified product inventory record.
        """
        try:
            sys_id = kwargs.get("id") or kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError("product inventory id is required")

            response = self._session.delete(
                url=f"{self.url}/api/sn_prd_invt/order/product/{sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result={"status": "deleted"})
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise
