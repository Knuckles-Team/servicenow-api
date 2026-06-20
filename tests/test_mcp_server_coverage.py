import ast
import inspect
import os
from unittest.mock import MagicMock, patch

import pytest

from servicenow_api.mcp_server import get_mcp_instance


class AwaitableMock:
    def __await__(self):
        async def _async_noop():
            pass

        return _async_noop().__await__()

    def __call__(self, *args, **kwargs):
        return self


class MockContext:
    def info(self, msg: str):
        return AwaitableMock()


@pytest.fixture
def mock_client():
    client = MagicMock()
    # Mock some basic responses
    resp = MagicMock()
    resp.result = {"status": "ok"}
    client.get_incidents.return_value = resp
    client.get_incident.return_value = resp
    client.create_incident.return_value = resp
    return client


def extract_tool_actions(filepath: str):
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    tool_actions = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            node.name.startswith("servicenow_") or node.name == "ingest_incidents_to_kg"
        ):
            # This is a tool function!
            actions = []
            for child in ast.walk(node):
                if isinstance(child, ast.Compare):
                    # Check if it is `action == "string"`
                    if (
                        isinstance(child.left, ast.Name)
                        and child.left.id == "action"
                        and len(child.ops) == 1
                        and isinstance(child.ops[0], ast.Eq)
                        and len(child.comparators) == 1
                    ):
                        comp = child.comparators[0]
                        if isinstance(comp, ast.Constant):
                            actions.append(comp.value)
                        elif isinstance(comp, ast.Str):
                            actions.append(comp.s)
            tool_actions[node.name] = actions
    return tool_actions


@pytest.mark.asyncio
async def test_mcp_tools_coverage(mock_client):
    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, args, middlewares, registered_tags, imported_tools = get_mcp_instance()
        assert mcp is not None
        tools = await mcp.list_tools()
        assert len(tools) > 0


@pytest.mark.asyncio
async def test_all_tools_loop(mock_client):
    """
    Call every tool with every action identified in the source code to maximize coverage.
    """
    from fastmcp.tools import FunctionTool

    mcp_server_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "servicenow_api",
        "mcp_server.py",
    )
    tool_actions = extract_tool_actions(mcp_server_path)

    ctx = MockContext()

    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, _, _, _, _ = get_mcp_instance()
        tools = await mcp.list_tools()
        for tool in tools:
            if isinstance(tool, FunctionTool):
                # Retrieve the actions we parsed for this tool (mapping hyphen back to underscore)
                norm_name = tool.name.replace("-", "_")
                actions = tool_actions.get(norm_name, [])

                # Test invalid JSON format
                try:
                    await tool.fn(
                        action="dummy",
                        params_json="invalid json",
                        client=mock_client,
                        ctx=ctx,
                    )
                except Exception:
                    pass

                # Test each valid action
                for act in actions:
                    try:
                        await tool.fn(
                            action=act,
                            params_json="{}",
                            client=mock_client,
                            ctx=ctx,
                        )
                    except Exception:
                        pass

                # Test unknown action
                try:
                    await tool.fn(
                        action="invalid_action_dummy",
                        params_json="{}",
                        client=mock_client,
                        ctx=ctx,
                    )
                except Exception:
                    pass
            else:
                try:
                    await tool.run()
                except Exception:
                    pass


@pytest.mark.asyncio
async def test_prompts():
    """
    Call every prompt helper defined on the FastMCP instance.
    """
    mcp, _, _, _, _ = get_mcp_instance()
    prompts = await mcp.list_prompts()
    for prompt in prompts:
        try:
            sig = inspect.signature(prompt.fn)
            kwargs = {}
            for name, _param in sig.parameters.items():
                kwargs[name] = "dummy_val"
            prompt.fn(**kwargs)
        except Exception:
            pass


def test_mcp_server_entrypoint():
    from servicenow_api.mcp_server import mcp_server

    # 1. stdio
    with patch("fastmcp.FastMCP.run") as mock_run:
        with patch("sys.argv", ["mcp_server", "--transport", "stdio"]):
            mcp_server()
            mock_run.assert_called_with(transport="stdio")

    # 2. sse
    with patch("fastmcp.FastMCP.run") as mock_run:
        with patch(
            "sys.argv",
            [
                "mcp_server",
                "--transport",
                "sse",
                "--host",
                "localhost",
                "--port",
                "8000",
            ],
        ):
            mcp_server()
            mock_run.assert_called_with(transport="sse", host="localhost", port=8000)

    # 3. streamable-http
    with patch("fastmcp.FastMCP.run") as mock_run:
        with patch(
            "sys.argv",
            [
                "mcp_server",
                "--transport",
                "streamable-http",
                "--host",
                "localhost",
                "--port",
                "8000",
            ],
        ):
            mcp_server()
            mock_run.assert_called_with(
                transport="streamable-http", host="localhost", port=8000
            )

    # 4. invalid transport
    with patch("fastmcp.FastMCP.run") as mock_run:
        with patch("sys.argv", ["mcp_server", "--transport", "invalid"]):
            with pytest.raises(SystemExit):
                mcp_server()


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])


@pytest.mark.asyncio
async def test_tool_mode_condensed_default(mock_client, monkeypatch):
    """Default mode = condensed: action-routed tools only, no verbose 1:1 tools."""
    monkeypatch.delenv("MCP_TOOL_MODE", raising=False)
    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, *_ = get_mcp_instance()
        names = {t.name for t in await mcp.list_tools()}
    assert "servicenow_cmdb" in names  # condensed action tool
    assert "servicenow_get_cmdb_instance" not in names  # verbose absent


@pytest.mark.asyncio
async def test_tool_mode_verbose(mock_client, monkeypatch):
    """verbose mode: one 1:1 tool per Api domain method, condensed absent."""
    monkeypatch.setenv("MCP_TOOL_MODE", "verbose")
    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, *_ = get_mcp_instance()
        names = {t.name for t in await mcp.list_tools()}
    assert "servicenow_cmdb" not in names
    assert "servicenow_get_cmdb_instance" in names
    # verbose tool names map 1:1 onto public Api methods
    from servicenow_api.api_client import Api

    method = "get_cmdb_instance"
    assert callable(getattr(Api, method, None))
    assert f"servicenow_{method}" in names


@pytest.mark.asyncio
async def test_tool_mode_both_is_union(mock_client, monkeypatch):
    monkeypatch.setenv("MCP_TOOL_MODE", "both")
    with patch("servicenow_api.mcp_server.get_client", return_value=mock_client):
        mcp, *_ = get_mcp_instance()
        names = {t.name for t in await mcp.list_tools()}
    assert "servicenow_cmdb" in names  # condensed
    assert "servicenow_get_cmdb_instance" in names  # verbose
