#!/usr/bin/python
"""ServiceNow SDK CLI wrapper (`now-sdk`, the `@servicenow/sdk` npm package).

Subprocess wrapper around the official ServiceNow SDK CLI — the Fluent-based tool
to scaffold, build, and deploy a Studio scoped application as source-controlled
code. This client is architecturally distinct from :class:`servicenow_api.api_client.Api`
(an HTTP REST client): it shells out to a local CLI binary rather than calling the
ServiceNow REST API directly, so it does not inherit ``ServiceNowApiBase`` and needs
no HTTP session/auth handshake to construct.

Each method runs one ``now-sdk <subcommand>`` invocation, capturing stdout/stderr/
exit-code into a :class:`~servicenow_api.servicenow_models.SdkCommandResult`. A
``password`` given to :meth:`ServiceNowSdkClient.auth` is piped via stdin
(``--password-stdin``) and never appears in argv, the captured ``command`` echo, or
any log/exception — matching the CLI's own documented non-interactive pattern.

See ``docker/Dockerfile`` (the ``builder-node`` stage) for how ``now-sdk`` ships in
the container image, and ``servicenow_api/mcp_server.py``'s ``register_sdk_tools``
for the MCP tool surface over this client.
"""

import shutil
import subprocess
import sys
from pathlib import Path

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting
from agent_utilities.core.exceptions import MissingParameterError

from servicenow_api.servicenow_models import (
    SdkAuthModel,
    SdkBuildModel,
    SdkCommandResult,
    SdkDependenciesModel,
    SdkInitModel,
    SdkInstallModel,
    SdkTransformModel,
)

logger = get_logger(__name__)

#: Console command the `@servicenow/sdk` npm package installs (see docker/Dockerfile).
SDK_BINARY = "now-sdk"
#: now-sdk build/install/transform can take minutes on a real scoped app.
_DEFAULT_TIMEOUT_SECONDS = 900


def _default_workdir() -> str:
    """Resolve the default now-sdk working directory, auto-created.

    Override with ``SDK_WORKDIR`` (deployment-varying — e.g. a mounted persistent
    volume); otherwise defaults to a fixed subdirectory of ``$HOME`` (``/tmp`` in the
    shipped container image, per docker/Dockerfile's ``HOME=/tmp``).
    """
    configured = setting("SDK_WORKDIR", "")
    workdir = (
        Path(configured) if configured else Path.home() / "servicenow-sdk-workspace"
    )
    workdir.mkdir(parents=True, exist_ok=True)
    return str(workdir)


def _run(
    subcommand: str,
    args: list[str],
    *,
    working_dir: str | None,
    stdin_data: str | None = None,
    timeout: int = _DEFAULT_TIMEOUT_SECONDS,
) -> SdkCommandResult:
    """Run ``now-sdk <subcommand> <args>``, capturing output.

    Never raises on a non-zero now-sdk exit — the exit code/stderr are the result
    callers inspect (``success=False``). Raises :class:`MissingParameterError` if
    the CLI itself is not installed, and re-raises unexpected subprocess errors
    (e.g. permission denied) after logging.
    """
    if shutil.which(SDK_BINARY) is None:
        raise MissingParameterError(
            f"{SDK_BINARY!r} is not on PATH — the ServiceNow SDK CLI is not "
            "installed in this environment (see docker/Dockerfile's builder-node "
            "stage, or `npm install -g @servicenow/sdk`)."
        )
    resolved_dir = working_dir or _default_workdir()
    Path(resolved_dir).mkdir(parents=True, exist_ok=True)
    argv = [SDK_BINARY, subcommand, *args]
    try:
        proc = subprocess.run(  # nosec B603 - argv built from validated fields, shell=False
            argv,
            cwd=resolved_dir,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return SdkCommandResult(
            command=argv,
            exit_code=-1,
            stdout=e.stdout or "",
            stderr=(e.stderr or "") + f"\nnow-sdk timed out after {timeout}s",
            working_dir=resolved_dir,
            success=False,
        )
    except Exception as e:
        print(f"now-sdk invocation failed: {type(e).__name__}", file=sys.stderr)
        raise
    return SdkCommandResult(
        command=argv,
        exit_code=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        working_dir=resolved_dir,
        success=proc.returncode == 0,
    )


class ServiceNowSdkClient:
    """Subprocess wrapper around the ServiceNow SDK CLI (``now-sdk``).

    Every method accepts ``**kwargs`` validated into the matching
    ``Sdk*Model`` (see ``servicenow_models.py``) and returns a
    :class:`SdkCommandResult`. Mirrors the ``**kwargs``-in, ``Response``-out shape
    of the HTTP ``api_client_*.py`` classes so it registers with the same MCP
    condensed-tool pattern, even though it drives a local CLI rather than REST.
    """

    def init(self, **kwargs) -> SdkCommandResult:
        """Scaffold a new scoped app / Fluent project (``now-sdk init``, alias ``create``)."""
        model = SdkInitModel(**kwargs)
        args: list[str] = []
        if model.from_source:
            args += ["--from", model.from_source]
        if model.app_name:
            args += ["--appName", model.app_name]
        if model.package_name:
            args += ["--packageName", model.package_name]
        if model.scope_name:
            args += ["--scopeName", model.scope_name]
        if model.template:
            args += ["--template", model.template]
        if model.auth:
            args += ["--auth", model.auth]
        if model.debug:
            args.append("--debug")
        return _run("init", args, working_dir=model.working_dir)

    def auth(self, **kwargs) -> SdkCommandResult:
        """Configure instance authentication (``now-sdk auth``).

        A ``password`` is piped via stdin with ``--password-stdin`` and is never
        placed in argv or in the returned command echo.
        """
        model = SdkAuthModel(**kwargs)
        args: list[str] = []
        stdin_data = None
        if model.list_credentials:
            args.append("--list")
        if model.delete:
            args += ["--delete", model.delete]
        if model.use:
            args += ["--use", model.use]
        if model.add:
            args += ["--add", model.add]
            if model.auth_type:
                args += ["--type", model.auth_type]
            if model.alias:
                args += ["--alias", model.alias]
            if model.username:
                args += ["--username", model.username]
            if model.password:
                args.append("--password-stdin")
                stdin_data = model.password
        if model.debug:
            args.append("--debug")
        return _run("auth", args, working_dir=model.working_dir, stdin_data=stdin_data)

    def build(self, **kwargs) -> SdkCommandResult:
        """Compile Fluent sources into an installable package (``now-sdk build``)."""
        model = SdkBuildModel(**kwargs)
        args: list[str] = []
        if model.source:
            args.append(model.source)
        if model.frozen_keys:
            args.append("--frozenKeys")
        if model.error_on_conflict:
            args.append("--errorOnConflict")
        if model.skip_clean:
            args.append("--skipClean")
        if model.legacy_choices:
            args.append("--legacyChoices")
        if model.debug:
            args.append("--debug")
        return _run("build", args, working_dir=model.working_dir)

    def deploy(self, **kwargs) -> SdkCommandResult:
        """Install/update the app on the target instance (``now-sdk install``, alias ``deploy``)."""
        model = SdkInstallModel(**kwargs)
        args: list[str] = []
        if model.source:
            args += ["--source", model.source]
        if model.auth:
            args += ["--auth", model.auth]
        if model.reinstall:
            args.append("--reinstall")
        if model.open_browser:
            args.append("--open-browser")
        if model.info:
            args.append("--info")
        if model.demo_data is False:
            args.append("--no-demoData")
        elif model.demo_data is True:
            args.append("--demoData")
        if model.skip_flow_activation:
            args.append("--skip-flow-activation")
        if model.debug:
            args.append("--debug")
        return _run("install", args, working_dir=model.working_dir)

    def transform(self, **kwargs) -> SdkCommandResult:
        """Download + convert XML records into Fluent source (``now-sdk transform``)."""
        model = SdkTransformModel(**kwargs)
        args: list[str] = []
        if model.table:
            args += ["--table", model.table]
        if model.force:
            args.append("--force")
        if model.from_path:
            args += ["--from", model.from_path]
        if model.directory:
            args += ["--directory", model.directory]
        if model.auth:
            args += ["--auth", model.auth]
        if model.format_source is False:
            args.append("--no-format")
        elif model.format_source is True:
            args.append("--format")
        if model.debug:
            args.append("--debug")
        return _run("transform", args, working_dir=model.working_dir)

    def dependencies(self, **kwargs) -> SdkCommandResult:
        """Download configured dependencies + type defs (``now-sdk dependencies``)."""
        model = SdkDependenciesModel(**kwargs)
        args: list[str] = []
        if model.sys_ids:
            args.extend(model.sys_ids)
        if model.directory:
            args += ["--directory", model.directory]
        if model.auth:
            args += ["--auth", model.auth]
        if model.type_defs_only:
            args.append("--type-defs-only")
        if model.fluent_only:
            args.append("--fluent-only")
        if model.add:
            args += ["--add", model.add]
        if model.scope:
            args += ["--scope", model.scope]
        if model.debug:
            args.append("--debug")
        return _run("dependencies", args, working_dir=model.working_dir)


def get_sdk_client() -> ServiceNowSdkClient:
    """FastMCP dependency: return a ``ServiceNowSdkClient``.

    Unlike :func:`servicenow_api.auth.get_client`, this needs no ServiceNow HTTP
    auth handshake — ``now-sdk`` manages its own credential store (see
    :meth:`ServiceNowSdkClient.auth`) — so construction is always trivial.
    """
    return ServiceNowSdkClient()
