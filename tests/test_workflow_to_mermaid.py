import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from servicenow_api.api_client import Api


@patch("servicenow_api.api_client.get_agent_workspace")
@patch("servicenow_api.api_client.Api.get_table")
@patch("servicenow_api.api_client.Api.collect_graph_for_roots")
@patch("servicenow_api.api_client.find_connected_components")
@patch("servicenow_api.api_client.graph_to_mermaid_multi")
@patch("servicenow_api.api_client.build_polished_markdown")
@patch("requests.Session.get")
@patch("builtins.open", new_callable=MagicMock)
def test_workflow_to_mermaid_path(
    mock_open,
    mock_session_get,
    mock_build_md,
    mock_graph_to_mermaid,
    mock_find_components,
    mock_collect_graph,
    mock_get_table,
    mock_get_workspace,
):

    mock_session_get.return_value.status_code = 200
    mock_workspace = Path("/tmp/mock_workspace")
    mock_get_workspace.return_value = mock_workspace

    mock_get_table.return_value.response.ok = True
    mock_get_table.return_value.response.json.return_value = {
        "result": [{"sys_id": "123"}]
    }

    mock_collect_graph.return_value = (MagicMock(), {"123": {"name": "Test Flow"}})
    mock_find_components.return_value = [MagicMock()]
    mock_graph_to_mermaid.return_value = "mermaid syntax"
    mock_build_md.return_value = "# Polished Markdown"

    client = Api(url="http://test.com", username="user", password="pass")

    result = client.workflow_to_mermaid(save_to_file=True)

    mock_get_workspace.assert_called_once()

    expected_base = mock_workspace / "servicenow_flow_reports"
    assert "servicenow_flow_reports" in result.file_path
    assert str(expected_base) in result.file_path

    mock_open.assert_called_once()
    args, kwargs = mock_open.call_args
    assert Path(args[0]).is_absolute()
    assert str(expected_base) in args[0]


if __name__ == "__main__":
    pytest.main([__file__])
