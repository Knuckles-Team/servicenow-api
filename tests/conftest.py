"""Fleet-wide test-harness self-healing: `.uv-workspace-siblings/agent-utilities`.

`pyproject.toml`'s `[tool.uv.sources]` resolves the `agent-utilities`
dependency through the gitignored `.uv-workspace-siblings/agent-utilities`
symlink (it must be gitignored — it's a machine-local absolute path). Only
the canonical checkout has it hand-created; a freshly created `git worktree`
never gets one, so the FIRST `uv sync` in a new worktree fails outright:

    error: Distribution not found at:
    file://.../.uv-workspace-siblings/agent-utilities

Three lanes hit this independently on 2026-08-27/28 and each fixed it by
hand. This mirrors the self-healing pattern agent-webui's `pnpm-build`
pre-commit hook already uses for its own missing `node_modules`
(`test -d node_modules || pnpm install`): provision the missing, gitignored,
worktree-local artifact idempotently instead of requiring every lane to
remember to hand-create it.

LIMITATION: this only self-heals a venv that has ALREADY been synced at
least once (e.g. the symlink was later deleted by `git clean`) — once
synced, uv's editable-install finder points at the resolved absolute path,
not the symlink, so pytest runs fine without it from then on. It CANNOT fix
the very first `uv sync` in a brand-new worktree, because pytest itself is
not installed until that sync succeeds. For that case, run this file
directly, once, before your first sync:

    python tests/conftest.py && uv sync --extra test --extra mcp
"""

import pathlib
import subprocess
import sys

import pytest


def _ensure_agent_utilities_sibling() -> "pathlib.Path | None":
    here = pathlib.Path(__file__).resolve().parent  # .../tests
    repo_root = here.parent
    link = repo_root / ".uv-workspace-siblings" / "agent-utilities"
    if link.is_symlink() or link.exists():
        return link

    # Derive the canonical (non-worktree) checkout root from git's common
    # dir — a worktree's own directory name/location tells us nothing about
    # where its sibling `agent-utilities` repo lives (this program's other
    # fleet-wide defect: deriving anything from the worktree basename).
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except Exception:
        return None
    common_dir = pathlib.Path(result.stdout.strip())
    canonical_root = common_dir.parent  # .../agent-packages/agents/<this-repo>
    packages_root = canonical_root.parent.parent  # .../agent-packages
    target = packages_root / "agent-utilities"
    if not (target / "pyproject.toml").exists():
        return None

    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(target)
    except FileExistsError:
        pass
    return link


_ensure_agent_utilities_sibling()

if __name__ == "__main__":
    # Allows `python tests/conftest.py` to bootstrap a fresh worktree BEFORE
    # `uv sync`, without importing anything from this repo's own package or
    # its third-party deps — none of which exist yet in a pre-sync venv.
    raise SystemExit(0)


@pytest.fixture(autouse=True)
def _clean_argv(monkeypatch):
    """Fleet-wide test-harness defect: reset sys.argv to a single clean
    element before every test.

    Several tests in this suite exercise this package's own argparse-based
    CLI entrypoint — directly via `get_mcp_instance()`/`agent_server()`, or
    indirectly via `runpy.run_module(..., run_name="__main__")` — and that
    argparse call reads the LIVE `sys.argv`. Left alone, pytest's own
    invocation flags (`-p no:randomly`, `-n auto`, `--randomly-seed=...`, ...)
    end up in that argv and are rejected by the module's CLI parser:

        error: argument -p/--port: invalid int value: 'no:randomly'

    which makes `pytest tests/ -q -p no:randomly` disagree with a plain
    `pytest tests/ -q` run -- not a real regression, just this trap. A
    handful of call sites already pin their own argv locally (e.g. via
    `patch("sys.argv", [...])` around a `runpy.run_module` call); those
    still work unchanged, since that local patch simply overrides this
    fixture's baseline for the duration of its own `with` block, and
    monkeypatch restores this baseline afterward. This fixture is the
    fleet-wide backstop for every OTHER call site (most of them direct
    `get_mcp_instance()` calls with no local patch at all) that the
    per-call-site fix in WD4-FIX-01 could not enumerate exhaustively. See
    plans/complex/waves/wD4/WD4-FIX-01.md defect (a).
    """
    monkeypatch.setattr(sys, "argv", ["pytest"])


import json
import os
import re
from unittest.mock import patch
from urllib.parse import urlparse

from dotenv import load_dotenv

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
        self.proxies = {}

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

        if "problem" in path:
            sysparm_query = (params or {}).get("sysparm_query", "")
            match = re.search(r"sys_id=([^&]+)", sysparm_query)
            sys_id = match.group(1) if match else "prb_123"
            record = {
                "sys_id": sys_id,
                "short_description": "Mocked Problem",
                "description": "Mocked",
            }
            # .../table/problem -> list (get_problems); .../table/problem/<id> -> single
            # record (get_problem), matching the real Table API response shape.
            if path.rstrip("/").endswith("/problem"):
                return MockResponse({"result": [record]}, 200)
            return MockResponse({"result": record}, 200)

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

        if "problem" in path:
            payload = json or {}
            short_desc = payload.get("short_description", "Mocked Short Description")
            desc = payload.get("description", "Mocked Description")
            return MockResponse(
                {
                    "result": {
                        "sys_id": "mock_problem_sys_id_123",
                        "short_description": short_desc,
                        "description": desc,
                    }
                },
                201,
            )

        return MockResponse({"result": {}}, 200)

    def put(self, url, data=None, json=None, **kwargs):
        return MockResponse({"result": {}}, 200)

    def patch(self, url, data=None, json=None, **kwargs):
        url_parsed = urlparse(url)
        path = url_parsed.path

        if "problem" in path or "incident" in path:
            payload = json or {}
            return MockResponse(
                {
                    "result": {
                        "sys_id": path.rstrip("/").rsplit("/", 1)[-1],
                        **payload,
                    }
                },
                200,
            )

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
