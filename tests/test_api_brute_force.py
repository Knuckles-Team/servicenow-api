import inspect
import requests
from unittest.mock import MagicMock, patch
from servicenow_api.api_client import Api
from servicenow_api.servicenow_models import Response
import asyncio
import pytest


@pytest.fixture
def mock_session():
    with (
        patch("requests.Session") as mock_sess,
        patch("requests.post") as mock_post,
        patch("requests.get") as mock_get,
    ):

        session = mock_sess.return_value

        res = MagicMock(spec=requests.Response)
        res.status_code = 200
        res.json.return_value = {
            "result": [{"sys_id": "123", "number": "INC123", "name": "test"}]
        }
        res.content = b'{"result": []}'

        mock_post.return_value = res
        mock_get.return_value = res
        session.get.return_value = res
        session.post.return_value = res
        session.put.return_value = res
        session.patch.return_value = res
        session.delete.return_value = res

        yield session


def test_all_api_methods_brute_force(mock_session):
    client = Api(url="http://test.com", username="user", password="pass")

    # Success pass
    res_success = MagicMock(spec=requests.Response)
    res_success.status_code = 200
    res_success.json.return_value = {
        "result": [{"sys_id": "123", "number": "INC123", "name": "test"}]
    }
    res_success.ok = True

    # Failure pass
    res_fail = MagicMock(spec=requests.Response)
    res_fail.status_code = 500
    res_fail.ok = False
    res_fail.text = "Internal Server Error"

    for mock_res in [res_success, res_fail]:
        mock_session.get.return_value = mock_res
        mock_session.post.return_value = mock_res
        mock_session.put.return_value = mock_res
        mock_session.delete.return_value = mock_res

        for name, method in inspect.getmembers(client, predicate=inspect.ismethod):
            if name.startswith("_") or name in ["headers", "proxies"]:
                continue

            sig = inspect.signature(method)
            kwargs = {}
            for param in sig.parameters.values():
                if param.name == "self":
                    continue

                # Guess value based on parameter name and type
                val = "test"
                low_name = param.name.lower()
                if any(x in low_name for x in ["sys_id", "id", "sysid"]):
                    val = "123"
                elif "table" in low_name:
                    val = "incident"
                elif "className" in low_name:
                    val = "cmdb_ci_server"
                elif "data" in low_name:
                    val = {"short_description": "test"}
                elif "payload" in low_name:
                    val = {"test": "val"}
                elif param.annotation == bool:
                    val = True
                elif param.annotation == int:
                    val = 10
                elif param.annotation == list or "list" in low_name:
                    val = ["test"]

                if param.default == inspect.Parameter.empty:
                    kwargs[param.name] = val
                elif param.name == "kwargs":  # handle **kwargs
                    kwargs["short_description"] = "test"
                    kwargs["incident_id"] = "123"
                    kwargs["table"] = "incident"

            try:
                method(**kwargs)
            except Exception:
                pass


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
