"""Exercise real client construction and Requests preparation with fake credentials."""

import base64
import json
import traceback
from unittest.mock import MagicMock
from urllib.parse import parse_qs

import pytest
import requests
from requests.sessions import Session

from servicenow_api.api_client import Api
from servicenow_api.auth import get_client

SECRET = "fake-secret+&=review"
TOKEN = "fake-review-token"
URL = "https://review.invalid"


@pytest.fixture
def transport(monkeypatch):
    session = Session()
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"access_token": TOKEN}).encode()
    response.url = URL + "/oauth_token.do"
    send = MagicMock(return_value=response)
    monkeypatch.setattr(session, "send", send)
    monkeypatch.setattr(requests, "Session", lambda: session)
    return response, send


def client(**kwargs):
    return Api(
        url=URL,
        client_id="fake-client",
        client_secret=SECRET,
        grant_type="client_credentials",
        tls_profile=MagicMock(),
        **kwargs,
    )


def test_exchange_success(transport, capsys, caplog):
    _, send = transport
    api = client(username="ignored-user", password="ignored-password")
    prepared = send.call_args.args[0]
    assert prepared.method == "POST"
    assert prepared.url == URL + "/oauth_token.do"
    assert prepared.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert parse_qs(prepared.body) == {
        "grant_type": ["client_credentials"],
        "client_id": ["fake-client"],
        "client_secret": [SECRET],
    }
    assert send.call_args.kwargs["timeout"] == 30
    api.tls_profile.configure_requests_session.assert_called_once_with(api._session)
    captured = capsys.readouterr()
    assert SECRET not in captured.err + captured.out + caplog.text
    assert TOKEN not in captured.err + captured.out + caplog.text
    assert api.headers["Authorization"] == f"Bearer {TOKEN}"


@pytest.mark.parametrize("status", [400, 401, 403, 500])
def test_http_failure_rejected_even_with_token(transport, status):
    response, _ = transport
    response.status_code = status
    with pytest.raises(requests.HTTPError):
        client()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"access_token": None},
        {"access_token": ""},
        {"access_token": " "},
        {"access_token": 42},
        {"access_token": []},
        [],
        None,
    ],
)
def test_invalid_token_response(transport, payload):
    response, _ = transport
    response._content = json.dumps(payload).encode()
    with pytest.raises(ValueError, match="OAuth"):
        client()


def test_malformed_json(transport):
    response, _ = transport
    response._content = b"not JSON"
    with pytest.raises(ValueError):
        client()


@pytest.mark.parametrize("failure", [requests.Timeout, requests.ConnectionError])
def test_transport_errors_do_not_leak(transport, failure, capsys, caplog):
    _, send = transport
    send.side_effect = failure(SECRET)
    with pytest.raises(failure) as caught:
        client()
    output = capsys.readouterr()
    rendered = "".join(traceback.format_exception(caught.value))
    assert SECRET not in rendered + output.err + output.out + caplog.text


def test_response_error_does_not_leak(transport, capsys, caplog):
    response, _ = transport
    response._content = json.dumps(
        {"error": "invalid_client", "client_secret": SECRET, "refresh_token": TOKEN}
    ).encode()
    with pytest.raises(Exception):
        client()
    output = capsys.readouterr()
    for value in (SECRET, TOKEN):
        assert value not in output.err + output.out + caplog.text


def test_redirects_disabled(transport):
    _, send = transport
    client()
    assert send.call_args.kwargs["allow_redirects"] is False


def test_explicit_token_wins(transport):
    _, send = transport
    api = client(token="explicit-fake-token")
    assert api.headers["Authorization"] == "Bearer explicit-fake-token"
    send.assert_not_called()


def test_password_grant_unchanged(transport):
    _, send = transport
    api = Api(
        url=URL,
        username="fake-user",
        password="fake-password",
        client_id="fake-client",
        client_secret=SECRET,
        tls_profile=MagicMock(),
    )
    data = parse_qs(send.call_args.args[0].body)
    assert data["grant_type"] == ["password"]
    assert data["username"] == ["fake-user"]
    assert data["password"] == ["fake-password"]
    assert api.headers["Authorization"] == f"Bearer {TOKEN}"


def test_basic_unchanged(transport):
    _, send = transport
    api = Api(
        url=URL, username="fake-user", password="fake-password", tls_profile=MagicMock()
    )
    assert (
        api.headers["Authorization"]
        == "Basic " + base64.b64encode(b"fake-user:fake-password").decode()
    )
    send.assert_not_called()


@pytest.fixture
def config(monkeypatch):
    from agent_utilities.mcp import delegated_auth

    settings = {
        "SERVICENOW_INSTANCE": URL,
        "SERVICENOW_GRANT_TYPE": "client_credentials",
        "SERVICENOW_CLIENT_ID": "fake-client",
        "SERVICENOW_CLIENT_SECRET": SECRET,
        "SERVICENOW_USERNAME": "fake-user",
        "SERVICENOW_PASSWORD": "fake-password",
    }
    monkeypatch.setattr(
        "servicenow_api.auth.setting",
        lambda key, default=None: settings.get(key, default),
    )
    monkeypatch.setattr(delegated_auth, "is_delegation_enabled", lambda: False)
    return settings


def test_config_client_credentials_over_password(transport, config):
    _, send = transport
    get_client(tls_profile=MagicMock())
    assert "username" not in parse_qs(send.call_args.args[0].body)


@pytest.mark.parametrize(
    "missing", ["SERVICENOW_CLIENT_ID", "SERVICENOW_CLIENT_SECRET"]
)
def test_explicit_grant_missing_credentials_fails_closed(transport, config, missing):
    config.pop(missing)
    with pytest.raises(ValueError):
        get_client(tls_profile=MagicMock())
    transport[1].assert_not_called()


def test_delegation_takes_precedence(transport, config, monkeypatch):
    from agent_utilities.mcp import delegated_auth

    monkeypatch.setattr(delegated_auth, "is_delegation_enabled", lambda: True)
    monkeypatch.setattr(
        delegated_auth, "get_delegated_token", lambda **kwargs: "fake-delegated"
    )
    monkeypatch.setattr(delegated_auth, "get_user_identity", lambda: {})
    api = get_client(tls_profile=MagicMock())
    assert api.headers["Authorization"] == "Bearer fake-delegated"
    transport[1].assert_not_called()


def test_delegation_failure_does_not_fallback(transport, config, monkeypatch):
    from agent_utilities.mcp import delegated_auth

    monkeypatch.setattr(delegated_auth, "is_delegation_enabled", lambda: True)

    def failure(**kwargs):
        raise RuntimeError("fake delegation failure")

    monkeypatch.setattr(delegated_auth, "get_delegated_token", failure)
    with pytest.raises(RuntimeError):
        get_client(tls_profile=MagicMock())
    transport[1].assert_not_called()


@pytest.mark.parametrize("status", [301, 302, 307, 308])
def test_redirect_response_rejected(transport, status):
    transport[0].status_code = status
    with pytest.raises(requests.HTTPError):
        client()


@pytest.mark.parametrize("missing", ["client_id", "client_secret"])
def test_direct_incomplete_grant_does_not_fallback(transport, missing):
    kwargs = dict(
        url=URL,
        username="fake-user",
        password="fake-password",
        client_id="fake-client",
        client_secret=SECRET,
        grant_type="client_credentials",
        tls_profile=MagicMock(),
    )
    kwargs[missing] = None
    with pytest.raises(ValueError):
        Api(**kwargs)
    transport[1].assert_not_called()


@pytest.mark.parametrize("oauth", [False, True])
def test_config_default_password_and_basic_unchanged(transport, config, oauth):
    config.pop("SERVICENOW_GRANT_TYPE")
    if not oauth:
        config.pop("SERVICENOW_CLIENT_ID")
        config.pop("SERVICENOW_CLIENT_SECRET")
    api = get_client(tls_profile=MagicMock())
    if oauth:
        assert parse_qs(transport[1].call_args.args[0].body)["grant_type"] == [
            "password"
        ]
    else:
        assert api.headers["Authorization"].startswith("Basic ")
        transport[1].assert_not_called()


def test_http_error_body_is_not_exposed(transport, capsys, caplog):
    response, _ = transport
    response.status_code = 401
    response._content = json.dumps({"error": SECRET, "refresh_token": TOKEN}).encode()
    with pytest.raises(requests.HTTPError) as caught:
        client()
    captured = capsys.readouterr()
    output = (
        "".join(traceback.format_exception(caught.value)) + captured.err + caplog.text
    )
    assert SECRET not in output
    assert TOKEN not in output
