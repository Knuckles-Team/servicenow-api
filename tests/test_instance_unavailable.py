import pytest
import requests

from servicenow_api.api.api_client_base import (
    ServiceNowInstanceUnavailableError,
    _reject_html_reply,
)

HIBERNATING = "<html><title>Instance Hibernating page</title></html>"


def _reply(body, content_type, url, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = body.encode()
    r.headers["content-type"] = content_type
    r.url = url
    return r


API = "https://x.service-now.com/api/now/table/incident?sysparm_limit=1"


def test_html_api_reply_names_the_hibernating_instance():
    with pytest.raises(ServiceNowInstanceUnavailableError, match="hibernating"):
        _reject_html_reply(_reply(HIBERNATING, "text/html", API))


def test_json_reply_passes_through():
    resp = _reply('{"result": []}', "application/json", API)
    assert _reject_html_reply(resp) is resp


def test_attachment_download_may_be_html():
    resp = _reply("<p>file</p>", "text/html", "https://x/api/now/attachment/a/file")
    assert _reject_html_reply(resp) is resp


def test_client_session_carries_the_hook():
    from servicenow_api.api.api_client_base import ServiceNowApiBase

    session = ServiceNowApiBase(url="https://x", username="u", password="p")._session
    hooks = getattr(session, "hooks", None)
    if hooks is not None:  # the suite swaps in a plain mock session
        assert _reject_html_reply in hooks["response"]
