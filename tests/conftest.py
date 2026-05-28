import os
import pytest
from dotenv import load_dotenv
from unittest.mock import patch
import json
import re
from urllib.parse import urlparse

load_dotenv()

import requests


# Define mock response and session helper classes
class MockResponse(requests.Response):
    def __init__(self, json_data, status_code):
        super().__init__()
        self._json_data = json_data
        self.status_code = status_code

    def json(self, **kwargs):
        return self._json_data

    @property
    def text(self):
        return json.dumps(self._json_data)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class MockSession:
    def __init__(self, *args, **kwargs):
        self.headers = {}
        self.verify = True
        self.proxies = None

    def get(self, url, params=None, **kwargs):
        url_parsed = urlparse(url)
        path = url_parsed.path

        if "subscribers" in path:
            return MockResponse({"result": []}, 200)

        if "change/model" in path or "change_request" in path:
            return MockResponse(
                {"result": [{"sys_id": "model_1", "name": "Model 1"}]}, 200
            )

        if "incident" in path:
            sysparm_query = (params or {}).get("sysparm_query", "")
            match = re.search(r"sys_id=([^&]+)", sysparm_query)
            sys_id = match.group(1) if match else "inc_123"
            return MockResponse(
                {
                    "result": [
                        {
                            "sys_id": sys_id,
                            "short_description": "Mocked Incident",
                            "description": "Mocked",
                        }
                    ]
                },
                200,
            )

        return MockResponse({"result": []}, 200)

    def post(self, url, data=None, json=None, **kwargs):
        url_parsed = urlparse(url)
        path = url_parsed.path

        if "incident" in path:
            payload = json or {}
            short_desc = payload.get("short_description", "Mocked Short Description")
            desc = payload.get("description", "Mocked Description")
            return MockResponse(
                {
                    "result": {
                        "sys_id": "mock_sys_id_123",
                        "short_description": short_desc,
                        "description": desc,
                    }
                },
                201,
            )

        return MockResponse({"result": {}}, 200)

    def put(self, url, data=None, json=None, **kwargs):
        return MockResponse({"result": {}}, 200)

    def delete(self, url, **kwargs):
        return MockResponse({"result": {}}, 200)


def mock_post(url, *args, **kwargs):
    if "oauth" in url:
        return MockResponse({"access_token": "mocked_oauth_token"}, 200)
    return MockResponse({"result": {}}, 200)


# Apply patches session-wide
@pytest.fixture(scope="session", autouse=True)
def mock_requests_session():
    with patch("requests.Session", MockSession), patch("requests.post", mock_post):
        yield


@pytest.fixture(scope="session")
def servicenow_config():
    """Fixture to provide ServiceNow configuration from environment variables or mock defaults."""
    config = {
        "instance": os.getenv("SERVICENOW_INSTANCE") or "http://servicenow.com/api/",
        "username": os.getenv("SERVICENOW_USERNAME") or "mock_user",
        "password": os.getenv("SERVICENOW_PASSWORD") or "mock_pass",
    }
    return config


@pytest.fixture(scope="session")
def api_client(servicenow_config):
    """Fixture to provide an authenticated Service Now Api client."""
    from servicenow_api.api_client import Api

    client = Api(
        url=servicenow_config["instance"],
        username=servicenow_config["username"],
        password=servicenow_config["password"],
    )
    return client
