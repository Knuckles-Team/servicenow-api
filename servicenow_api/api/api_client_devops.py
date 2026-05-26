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
    CICD,
    CICDModel,
    DevOpsArtifactRegistrationRequest,
    DevOpsChangeControlResponse,
    DevOpsOnboardingStatusResponse,
    DevOpsSchemaRequest,
    FlowGraph,
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


class ServiceNowApiDevops(ServiceNowApiBase):
    def app_repo_install(self, **kwargs) -> Response:
        """
        Install an application from the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be installed.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool
        :param base_app_version: The version of the base app.
        :type base_app_version: str
        :param version: The version of the application to be installed.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the installation.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/install",
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

    def app_repo_publish(self, **kwargs) -> Response:
        """
        Publish an application to the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be published.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param dev_notes: Development notes for the published version.
        :type dev_notes: str
        :param version: The version of the application to be published.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the publication.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/publish",
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

    def app_repo_rollback(self, **kwargs) -> Response:
        """
        Rollback an application in the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be rolled back.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param version: The version of the application to be rolled back.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the rollback.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id, scope, or version is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None or cicd.version is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/rollback",
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

    def activate_plugin(self, **kwargs) -> Response:
        """
        Activate a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be activated.
        :type plugin_id: str

        :return: Response containing parsed Pydantic model with information about the activation.
        :rtype: Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.plugin_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/plugin/{cicd.plugin_id}/activate",
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

    def rollback_plugin(self, **kwargs) -> Response:
        """
        Rollback a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be rolled back.
        :type plugin_id: str

        :return: Response containing parsed Pydantic model with information about the rollback.
        :rtype: Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.plugin_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/plugin/{cicd.plugin_id}/rollback",
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

    def import_repository(self, **kwargs) -> Response:
        """
        Import a repository based on the provided parameters.

        :param credential_sys_id: The sys_id of the credential to be used for the import.
        :type credential_sys_id: str
        :param mid_server_sys_id: The sys_id of the MID Server to be used for the import.
        :type mid_server_sys_id: str
        :param repo_url: The URL of the repository to be imported.
        :type repo_url: str
        :param branch_name: The name of the branch to be imported.
        :type branch_name: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool

        :return: Response containing parsed Pydantic model with information about the repository import.
        :rtype: Response

        :raises MissingParameterError: If repo_url is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.repo_url is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/sc/import",
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

    def update_set_create(self, **kwargs) -> Response:
        """
        Creates a new update set and inserts the new record in the Update Sets [sys_update_set] table.

        :param update_set_name: Name to give the update set.
        :type update_set_name: str
        :param description: Description of the update set.
        :type description: str
        :param scope: The scope name of the application in which to create the new update set.
        :type scope: str
        :param sys_id: Sys_id of the application in which to create the new update set.
        :type sys_id: str

        :return: Response containing parsed Pydantic model with information about the created update set.
        :rtype: Response

        :raises MissingParameterError: If update_set_name is not provided or both sys_id and scope are not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_name is None or (
                cicd.sys_id is None and cicd.scope is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/create",
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

    def update_set_retrieve(self, **kwargs) -> Response:
        """
        Retrieves an update set with a given sys_id and allows you to remove the existing retrieved update set from the instance.

        :param update_set_id: Sys_id of the update set on the source instance from where the update set was retrieved.
        :type update_set_id: str
        :param update_source_id: Sys_id of the remote instance record.
        :type update_source_id: str
        :param update_source_instance_id: Instance ID of the remote instance.
        :type update_source_instance_id: str
        :param auto_preview: Flag that indicates whether to automatically preview the update set after retrieval.
        :type auto_preview: bool
        :param cleanup_retrieved: Flag that indicates whether to remove the existing retrieved update set from the instance.
        :type cleanup_retrieved: bool

        :return: Response containing parsed Pydantic model with progress information about the retrieval.
        :rtype: Response

        :raises MissingParameterError: If update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/retrieve",
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

    def update_set_preview(self, **kwargs) -> Response:
        """
        Previews an update set to check for any conflicts and retrieve progress information about the update set operation.

        :param remote_update_set_id: Sys_id of the update set to preview.
        :type remote_update_set_id: str

        :return: Response containing parsed Pydantic model with progress information about the preview.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/preview/{cicd.remote_update_set_id}",
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

    def update_set_commit(self, **kwargs) -> Response:
        """
        Commits an update set with a given sys_id.

        :param remote_update_set_id: Sys_id of the update set to commit.
        :type remote_update_set_id: str
        :param force_commit: Flag that indicates whether to force commit the update set.
        :type force_commit: str

        :return: Response containing parsed Pydantic model with progress information about the commit.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/commit/{cicd.remote_update_set_id}",
                json=cicd.data,
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

    def update_set_commit_multiple(self, **kwargs) -> Response:
        """
        Commits multiple update sets in a single request according to the order that they're provided.

        :param remote_update_set_ids: List of sys_ids associated with any update sets to commit. Sys_ids are committed in the order given in the request.
        :type remote_update_set_ids: str
        :param force_commit: Flag that indicates whether to force commit the update set.
        :type force_commit: str

        :return: Response containing parsed Pydantic model with progress information about the multiple commits.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_ids is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_ids is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/commitMultiple",
                params=cicd.api_parameters,
                json=cicd.data,
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

    def update_set_back_out(self, **kwargs) -> Response:
        """
        Backs out an installation operation that was performed on an update set with a given sys_id.

        :param update_set_id: Sys_id of the update set.
        :type update_set_id: str
        :param rollback_installs: Flag that indicates whether to rollback the batch installation performed during the update set commit.
        :type rollback_installs: bool

        :return: Response containing parsed Pydantic model with progress information about the back out.
        :rtype: Response

        :raises MissingParameterError: If update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/back_out",
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

    def get_devops_code_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specified code resource.
        """
        try:
            req = DevOpsSchemaRequest(**kwargs)
            if not req.resource:
                raise MissingParameterError

            params = {"resource": req.resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/code/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_devops_onboarding_status(self, **kwargs) -> Response:
        """
        Returns the current status of the specified onboarding event.
        """
        try:
            id_ = kwargs.get("id")
            if not id_:
                raise MissingParameterError

            params = {"id": id_}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/onboarding/status",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=DevOpsOnboardingStatusResponse.model_validate(
                    response.json().get("result", {})
                ),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_devops_change_control(self, **kwargs) -> Response:
        """
        Checks if the orchestration task is under change control.
        """
        try:
            toolId = kwargs.get("toolId")
            orchestrationTaskName = kwargs.get("orchestrationTaskName")
            if not toolId:
                raise MissingParameterError

            params = {
                "toolId": toolId,
                "toolType": kwargs.get("toolType", "jenkins"),
            }
            if orchestrationTaskName:
                params["orchestrationTaskName"] = orchestrationTaskName
            if "testConnection" in kwargs:
                params["testConnection"] = str(kwargs.get("testConnection")).lower()
            if "orchestrationTaskURL" in kwargs:
                params["orchestrationTaskURL"] = kwargs.get("orchestrationTaskURL")

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/changeControl",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=DevOpsChangeControlResponse.model_validate(
                    response.json().get("result", {})
                ),
            )
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_devops_change_info(self, **kwargs) -> Response:
        """
        Retrieves change request details for a specified orchestration pipeline execution.
        """
        try:
            toolId = kwargs.get("toolId")
            buildNumber = kwargs.get("buildNumber")
            if not toolId or not buildNumber:
                raise MissingParameterError

            params = {"toolId": toolId, "buildNumber": buildNumber}
            if "stageName" in kwargs:
                params["stageName"] = kwargs.get("stageName")
            if "pipelineName" in kwargs:
                params["pipelineName"] = kwargs.get("pipelineName")
            if "projectName" in kwargs:
                params["projectName"] = kwargs.get("projectName")
            if "branchName" in kwargs:
                params["branchName"] = kwargs.get("branchName")

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/changeInfo",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_devops_orchestration_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specified orchestration resource.
        """
        try:
            resource = kwargs.get("resource")
            if not resource:
                raw_req = DevOpsSchemaRequest(**kwargs)
                resource = raw_req.resource

            if not resource:
                raise MissingParameterError

            params = {"resource": resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def check_devops_step_mapping(self, **kwargs) -> Response:
        """
        Verifies that the information being passed is valid for the creation of an orchestration task.
        """
        try:
            toolId = kwargs.get("toolId")
            orchestrationTaskName = kwargs.get("orchestrationTaskName")
            orchestrationTaskURL = kwargs.get("orchestrationTaskURL")
            toolType = kwargs.get("toolType", "jenkins")

            if not toolId or not orchestrationTaskName or not orchestrationTaskURL:
                raise MissingParameterError

            params = {
                "toolId": toolId,
                "orchestrationTaskName": orchestrationTaskName,
                "orchestrationTaskURL": orchestrationTaskURL,
                "toolType": toolType,
            }
            for k in [
                "branchName",
                "isMultiBranch",
                "parentStageName",
                "parentStageURL",
                "testConnection",
            ]:
                if k in kwargs:
                    params[k] = kwargs[k]

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/stepMapping",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def get_devops_plan_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specific plan.
        """
        try:
            resource = kwargs.get("resource")
            if not resource:
                raise MissingParameterError

            params = {"resource": resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/plan/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise

    def register_devops_artifact(self, **kwargs) -> Response:
        """
        Enables orchestration tools to register artifacts into a ServiceNow instance.
        """
        try:
            req = DevOpsArtifactRegistrationRequest(**kwargs)
            if not req.artifacts:
                raise MissingParameterError

            params: dict[str, Any] = {}
            if req.orchestrationToolId:
                params["orchestrationToolId"] = req.orchestrationToolId
            if req.toolId:
                params["toolId"] = req.toolId

            response = self._session.post(
                url=f"{self.url}/api/sn_devops/devops/artifact/registration",
                params=params,
                headers=self.headers,
                json=req.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}", file=sys.stderr)
            raise
