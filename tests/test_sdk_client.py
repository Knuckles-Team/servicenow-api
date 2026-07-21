import subprocess
from unittest.mock import MagicMock, patch

import pytest

from servicenow_api.sdk_client import ServiceNowSdkClient, get_sdk_client


@pytest.fixture
def mock_subprocess(tmp_path):
    """Patch shutil.which (now-sdk 'installed') and subprocess.run."""
    with (
        patch(
            "servicenow_api.sdk_client.shutil.which", return_value="/usr/bin/now-sdk"
        ),
        patch("servicenow_api.sdk_client.subprocess.run") as mock_run,
    ):
        proc = MagicMock()
        proc.returncode = 0
        proc.stdout = "ok"
        proc.stderr = ""
        mock_run.return_value = proc
        yield mock_run


def test_get_sdk_client_returns_client():
    client = get_sdk_client()
    assert isinstance(client, ServiceNowSdkClient)


def test_init_builds_expected_argv(mock_subprocess, tmp_path):
    client = ServiceNowSdkClient()
    result = client.init(
        appName="MyApp",
        packageName="x_my_app",
        scopeName="x_my",
        template="typescript.basic",
        working_dir=str(tmp_path),
    )
    argv = mock_subprocess.call_args.args[0]
    assert argv[0] == "now-sdk"
    assert argv[1] == "init"
    assert "--appName" in argv and "MyApp" in argv
    assert "--packageName" in argv and "x_my_app" in argv
    assert "--scopeName" in argv and "x_my" in argv
    assert "--template" in argv and "typescript.basic" in argv
    assert result.success is True
    assert result.exit_code == 0


def test_auth_password_never_in_argv(mock_subprocess, tmp_path):
    """A password must be piped via stdin with --password-stdin, never in argv."""
    client = ServiceNowSdkClient()
    result = client.auth(
        add="https://dev12345.service-now.com",
        type="basic",
        alias="dev",
        username="admin",
        password="super-secret-value",
        working_dir=str(tmp_path),
    )
    argv = mock_subprocess.call_args.args[0]
    kwargs = mock_subprocess.call_args.kwargs
    assert "super-secret-value" not in argv
    assert "--password-stdin" in argv
    assert kwargs.get("input") == "super-secret-value"
    # The captured command echo must not leak the password either.
    assert "super-secret-value" not in result.command
    assert result.success is True


def test_auth_list_credentials(mock_subprocess, tmp_path):
    client = ServiceNowSdkClient()
    client.auth(list=True, working_dir=str(tmp_path))
    argv = mock_subprocess.call_args.args[0]
    assert argv == ["now-sdk", "auth", "--list"]


def test_build_uses_positional_source(mock_subprocess, tmp_path):
    client = ServiceNowSdkClient()
    client.build(source="/data/my-app", frozenKeys=True, working_dir=str(tmp_path))
    argv = mock_subprocess.call_args.args[0]
    assert argv == ["now-sdk", "build", "/data/my-app", "--frozenKeys"]


def test_deploy_maps_to_install_subcommand(mock_subprocess, tmp_path):
    client = ServiceNowSdkClient()
    result = client.deploy(
        source="/data/my-app", auth="dev", demo_data=False, working_dir=str(tmp_path)
    )
    argv = mock_subprocess.call_args.args[0]
    assert argv[1] == "install"
    assert "--source" in argv and "/data/my-app" in argv
    assert "--auth" in argv and "dev" in argv
    assert "--no-demoData" in argv
    assert result.working_dir == str(tmp_path)


def test_dependencies_passes_sys_ids_positionally(mock_subprocess, tmp_path):
    client = ServiceNowSdkClient()
    client.dependencies(
        sys_ids=["abc123", "def456"], scope="x_my_app", working_dir=str(tmp_path)
    )
    argv = mock_subprocess.call_args.args[0]
    assert "abc123" in argv and "def456" in argv


def test_working_dir_respects_sdk_workdir_override(
    mock_subprocess, monkeypatch, tmp_path
):
    override = tmp_path / "sdk-workspace"
    monkeypatch.setenv("SDK_WORKDIR", str(override))
    client = ServiceNowSdkClient()
    result = client.build()
    assert result.working_dir == str(override)
    assert override.is_dir()  # auto-created
    kwargs = mock_subprocess.call_args.kwargs
    assert kwargs.get("cwd") == str(override)


def test_missing_sdk_binary_raises_clear_error(tmp_path):
    with patch("servicenow_api.sdk_client.shutil.which", return_value=None):
        client = ServiceNowSdkClient()
        with pytest.raises(Exception) as exc:
            client.build(working_dir=str(tmp_path))
        assert "now-sdk" in str(exc.value)


def test_timeout_is_reported_not_raised(tmp_path):
    with (
        patch(
            "servicenow_api.sdk_client.shutil.which", return_value="/usr/bin/now-sdk"
        ),
        patch(
            "servicenow_api.sdk_client.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="now-sdk", timeout=1),
        ),
    ):
        client = ServiceNowSdkClient()
        result = client.build(working_dir=str(tmp_path))
        assert result.success is False
        assert result.exit_code == -1
        assert "timed out" in result.stderr
