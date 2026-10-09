#!/usr/bin/python

import base64
import gzip
import json
import logging
import sys
from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

import requests
from agent_connector_sdk.exceptions import MissingParameterError
from agent_connector_sdk.tls.profile import ResolvedTLSProfile
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from servicenow_api.servicenow_models import (
    FlowGraph,
)

logger = logging.getLogger(__name__)


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
        logger.error("Failed to decode values: error_type=%s", type(e).__name__)
        return []


def _collect_action_params(decoded: list[dict[str, Any]]) -> dict[str, Any]:
    """Flatten decoded action-input rows into a single name->value map."""
    params: dict[str, Any] = {}
    for p in decoded:
        name = p.get("name")
        val = p.get("displayValue") or p.get("value")
        if name and val:
            params[name] = val
    return params


def _approval_action_details(params: dict[str, Any]) -> list[str]:
    details = []
    table = params.get("table_name") or params.get("table")
    rules = params.get("approval_conditions")
    if table:
        details.append(f"Table: {table}")
    if rules:
        details.append(f"Rules: {rules}")
    return details


def _record_action_details(params: dict[str, Any]) -> list[str]:
    """Shared by "create record" and "update record" actions."""
    details = []
    table = params.get("table_name") or params.get("ah_table") or params.get("table")
    fields = params.get("values") or params.get("ah_fields")
    if table:
        details.append(f"Table: {table}")
    if fields and isinstance(fields, str):
        important = [f.split("=")[0] for f in fields.split("^") if "=" in f]
        if important:
            details.append(f"Fields: {', '.join(important[:5])}...")
    return details


def _lookup_action_details(params: dict[str, Any]) -> list[str]:
    details = []
    table = params.get("table")
    conds = params.get("conditions")
    if table:
        details.append(f"Table: {table}")
    if conds:
        details.append(f"Cond: {conds}")
    return details


def _note_action_details(params: dict[str, Any]) -> list[str]:
    """Shared by worknote and comment actions."""
    note = (
        params.get("ah_work_note")
        or params.get("ah_comment")
        or params.get("note")
        or params.get("comment")
    )
    return [f"Note: {note}"] if note else []


# Ordered like the original if/elif chain: the first keyword that appears in
# the (lowercased) action type wins, matching the prior first-match semantics.
_ACTION_DETAIL_EXTRACTORS: list[tuple[str, Any]] = [
    ("approval", _approval_action_details),
    ("create record", _record_action_details),
    ("update record", _record_action_details),
    ("look up record", _lookup_action_details),
    ("worknote", _note_action_details),
    ("comment", _note_action_details),
]


def extract_action_details(
    decoded: list[dict[str, Any]], action_type: str
) -> list[str]:
    """
    Extracts specific metadata from decoded action values based on the action type.
    """
    params = _collect_action_params(decoded)
    at_clean = (action_type or "").lower()

    for keyword, extractor in _ACTION_DETAIL_EXTRACTORS:
        if keyword in at_clean:
            return extractor(params)

    return []


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


def _resolve_start_node(graph: FlowGraph, root_id: str) -> str | None:
    """Find the graph's trigger node for `root_id`, trying both id shapes."""
    node_ids = {node.id for node in graph.nodes}
    start_node = f"root_{root_id[:8]}_trigger_{root_id[:8]}"
    if start_node in node_ids:
        return start_node
    start_node = f"trigger_{root_id[:8]}"
    if start_node in node_ids:
        return start_node
    return None


def _build_adjacency(
    edges: list[Any], *, bidirectional: bool = False
) -> defaultdict[str, list[str]]:
    adj: defaultdict[str, list[str]] = defaultdict(list)
    for edge in edges:
        adj[edge.from_id].append(edge.to_id)
        if bidirectional:
            adj[edge.to_id].append(edge.from_id)
    return adj


def _walk_reachable(
    adj: defaultdict[str, list[str]], start: str, visited: set[str]
) -> set[str]:
    """Iterative DFS from `start`, recording newly-visited ids into `visited`
    (in place, so callers can track visitation across multiple starts) and
    returning just the ids reached from this particular start."""
    reached: set[str] = set()
    stack = [start]
    while stack:
        curr = stack.pop()
        if curr not in reached:
            reached.add(curr)
            visited.add(curr)
            for neighbor in adj[curr]:
                if neighbor not in reached:
                    stack.append(neighbor)
    return reached


def get_reachable_subgraph(graph: FlowGraph, root_id: str) -> FlowGraph:
    """
    Extracts a subgraph containing only the nodes and edges reachable from the given root_id.
    """
    start_node = _resolve_start_node(graph, root_id)
    if start_node is None:
        return FlowGraph(nodes=[], edges=[], summary="Root not found")

    adj = _build_adjacency(graph.edges)
    node_by_id = {node.id: node for node in graph.nodes}
    reachable_nodes = _walk_reachable(adj, start_node, set())

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


def _subgraph_for_ids(graph: FlowGraph, node_ids: set[str], summary: str) -> FlowGraph:
    node_by_id = {node.id: node for node in graph.nodes}
    sub_nodes = [node_by_id[nid] for nid in node_ids]
    sub_edges = [
        edge
        for edge in graph.edges
        if edge.from_id in node_ids and edge.to_id in node_ids
    ]
    return FlowGraph(nodes=sub_nodes, edges=sub_edges, summary=summary)


def find_connected_components(graph: FlowGraph) -> list[FlowGraph]:
    """
    Splits a single large global FlowGraph into a list of smaller FlowGraphs,
    where each sub-graph represents a completely disconnected component of flows/subflows.
    """
    if not graph.nodes:
        return []

    adj = _build_adjacency(graph.edges, bidirectional=True)
    all_node_ids = {node.id for node in graph.nodes}

    visited: set[str] = set()
    components: list[FlowGraph] = []
    for start_node in all_node_ids:
        if start_node in visited:
            continue
        component_nodes = _walk_reachable(adj, start_node, visited)
        components.append(
            _subgraph_for_ids(
                graph, component_nodes, f"Component size: {len(component_nodes)}"
            )
        )

    return components


def _mermaid_node_shape(node: Any, label: str) -> str:
    shape_map = {
        "trigger": f"(({label}))",
        "decision": f"{{{{{label}}}}}",
        "loop": f"[/{label}/]",
        "subflow_call": f"[[{label}]]",
    }
    return shape_map.get(node.type, f"[{label}]")


def _mermaid_root_group_lines(
    graph: FlowGraph, root_id: str, all_metadata: dict[str, dict[str, Any]]
) -> list[str] | None:
    """Lines for one root's subgraph block, or None if the root has no nodes."""
    root_prefix = f"root_{root_id[:8]}_"
    trigger_id = f"root_{root_id[:8]}_trigger_{root_id[:8]}"
    root_nodes = [
        node
        for node in graph.nodes
        if node.id.startswith(root_prefix) or node.id == trigger_id
    ]
    if not root_nodes:
        return None

    meta = all_metadata.get(root_id, {})
    flow_name = meta.get("name", root_id)
    lines = [f'    subgraph "{flow_name} ({root_id})"']
    for node in root_nodes:
        label = sanitize_mermaid_label(node.label)
        lines.append(f"        {node.id}{_mermaid_node_shape(node, label)}")
    lines.append("    end")
    return lines


def _mermaid_ungrouped_node_lines(
    graph: FlowGraph, root_sys_ids: list[str]
) -> list[str]:
    lines = []
    for node in graph.nodes:
        if any(node.id.startswith(f"root_{rid[:8]}_") for rid in root_sys_ids):
            continue
        label = sanitize_mermaid_label(node.label)
        lines.append(f"    {node.id}{_mermaid_node_shape(node, label)}")
    return lines


def _mermaid_edge_lines(graph: FlowGraph) -> list[str]:
    lines = []
    for edge in graph.edges:
        label = f" |{edge.label}|" if edge.label else ""
        lines.append(f"    {edge.from_id} -->{label} {edge.to_id}")
    return lines


def graph_to_mermaid_multi(
    graph: FlowGraph,
    root_sys_ids: list[str],
    all_metadata: dict[str, dict[str, Any]] | None = None,
) -> str:
    lines = ["flowchart TD"]

    for root_id in root_sys_ids:
        group_lines = _mermaid_root_group_lines(graph, root_id, all_metadata or {})
        if group_lines:
            lines.extend(group_lines)

    lines.extend(_mermaid_ungrouped_node_lines(graph, root_sys_ids))
    lines.extend(_mermaid_edge_lines(graph))

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


def _exchange_oauth_token(
    session: requests.Session,
    auth_url: str,
    auth_headers: dict[str, str],
    auth_data: dict[str, Any],
) -> str:
    """POST the password-grant OAuth exchange and return the access token."""
    encoded_data_str = urlencode(auth_data)
    response = None
    try:
        response = session.post(
            url=auth_url,
            data=encoded_data_str,
            headers=auth_headers,
            timeout=30,
        )
        response = response.json()
        return response["access_token"]
    except Exception as e:
        print(
            f"Error Authenticating with OAuth: \n\n{type(e).__name__}\n\nResponse: {response}",
            file=sys.stderr,
        )
        raise e


class ServiceNowApiBase:
    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        token: str | None = None,
        grant_type: str | None = "password",
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.tls_profile = tls_profile or resolve_tls_profile("servicenow")
        self.tls_profile.configure_requests_session(self._session)
        self.base_url = url
        self.auth_url = f"{self.base_url}/oauth_token.do"
        self.url = ""
        self.headers = None
        self.auth_headers = None
        self.auth_data = None
        self.encoded_auth_data = None
        self.token = None
        if token:
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif grant_type == "client_credentials":
            if not client_id or not client_secret:
                raise ValueError(
                    "OAuth client_credentials requires client_id and client_secret"
                )
            self.auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            self.auth_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            }
            try:
                response = self._session.post(
                    url=self.auth_url,
                    data=urlencode(self.auth_data),
                    headers=self.auth_headers,
                    timeout=30,
                    allow_redirects=False,
                )
            except requests.RequestException as exc:
                # Exception text can contain credentials echoed by a transport.
                raise type(exc)("OAuth token request failed") from None
            if not 200 <= response.status_code < 300:
                raise requests.HTTPError(
                    f"OAuth token request failed (HTTP {response.status_code})"
                )
            try:
                payload = response.json()
            except ValueError:
                raise ValueError("OAuth token response is not valid JSON") from None
            access_token = (
                payload.get("access_token") if isinstance(payload, dict) else None
            )
            if not isinstance(access_token, str) or not access_token.strip():
                raise ValueError("OAuth token response has no valid access_token")
            self.token = access_token
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif username and password and client_id and client_secret:
            self.auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            self.auth_data = {
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password,
            }
            self.token = _exchange_oauth_token(
                self._session, self.auth_url, self.auth_headers, self.auth_data
            )
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif username and password:
            user_pass = f"{username}:{password}".encode()
            user_pass_encoded = b64encode(user_pass).decode()
            self.headers = {
                "Authorization": f"Basic {user_pass_encoded}",
                "Content-Type": "application/json",
            }
        else:
            raise MissingParameterError

        self.url = f"{self.base_url}/api"

        # NOTE: no eager connectivity probe here. This used to issue a GET
        # `{url}/api/subscribers` at construction time to fail fast on bad
        # auth/URL — but a client is built per-call via `Depends(get_client)`
        # (see auth.py's `get_client`), so any exception raised here (bad
        # creds, DNS/egress failure, a slow/hibernating instance) was caught
        # by FastMCP's dependency resolver and surfaced only as the generic
        # `RuntimeError: Failed to resolve dependency 'client' for <tool>`,
        # discarding the real cause. Each tool method already issues its own
        # request and calls `response.raise_for_status()`
        # (`requests.HTTPError`) per-call, so removing this probe just means
        # the actual transport/auth failure is what the caller sees, instead
        # of a generic dependency-resolution error. Same fix already applied
        # in archivebox-api's `BaseApiClient.__init__`.
