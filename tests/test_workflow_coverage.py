import pytest
import requests
from unittest.mock import MagicMock, patch
from servicenow_api.api_client import Api
from servicenow_api.servicenow_models import FlowGraph, FlowNode, FlowEdge


@pytest.fixture
def client():
    with (
        patch("requests.Session") as mock_sess,
        patch("requests.post") as mock_post,
        patch("requests.get") as mock_get,
    ):

        # Mock responses for auth/subscribers
        res = MagicMock(spec=requests.Response)
        res.status_code = 200
        res.json.return_value = {"result": []}
        res.ok = True

        mock_post.return_value = res
        mock_get.return_value = res
        mock_sess.return_value.get.return_value = res

        return Api(url="http://test.com", username="user", password="pass")


@pytest.mark.asyncio
async def test_workflow_to_mermaid_coverage(client):
    # Mock get_flow_metadata
    with (
        patch.object(client, "get_flow_metadata") as mock_meta,
        patch.object(client, "get_table") as mock_table,
        patch("servicenow_api.api_client.decode_values", return_value={}),
        patch("servicenow_api.api_client.determine_node_type", return_value="action"),
    ):

        mock_meta.return_value = {
            "name": "Test Flow",
            "description": "Desc",
            "application": "Global",
            "scope": "Global",
        }

        # Mock get_table for actions
        action_resp = MagicMock()
        action_resp.response.ok = True
        action_resp.response.json.return_value = {
            "result": [
                {
                    "sys_id": "act1",
                    "name": "Action 1",
                    "order": 1,
                    "action_type": {"value": "type1"},
                }
            ]
        }
        mock_table.return_value = action_resp

        # Call workflow_to_mermaid
        # Note: this might call itself recursively if there are subflows
        # For coverage, we just want to hit the main loop
        result = client.workflow_to_mermaid(
            flow_identifiers=["flow123"], save_to_file=False
        )
        assert result is not None
        assert "Test Flow" in result.markdown_content


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
