"""Verify package initialization and version metadata."""

import importlib

import pytest

PKG_NAME = __name__.rsplit(".", 1)[0] if "." in __name__ else None


def _get_pkg_name():
    """Derive package name from project metadata (works in any checkout name).

    Was previously `project_dir.name.replace("-", "_")` — the checkout's
    directory basename. That breaks in every `git worktree`, whose leaf
    directory is named after the branch (e.g. `cx-wD4-wd4-fix-01`), not the
    package (`servicenow_api`), so `importlib.import_module()` below raised
    `ModuleNotFoundError` for every lane working out of a worktree. Read the
    canonical `[project].name` from `pyproject.toml` instead, matching the
    fix already applied in the sibling atlassian-agent/github-agent/
    portainer-agent repos.
    """
    import pathlib

    import tomllib

    test_dir = pathlib.Path(__file__).resolve().parent
    project_dir = test_dir.parent
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        with pyproject.open("rb") as f:
            name = tomllib.load(f)["project"]["name"]
        return name.replace("-", "_")
    return project_dir.name.replace("-", "_")


@pytest.fixture
def pkg_name():
    return _get_pkg_name()


def test_package_importable(pkg_name):
    """Package should be importable."""
    mod = importlib.import_module(pkg_name)
    assert mod is not None


def test_version_exists(pkg_name):
    """Package should expose __version__."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    # Version may come from importlib.metadata instead
    if version is None:
        from importlib.metadata import version as get_version

        version = get_version(pkg_name.replace("_", "-"))
    assert version is not None, f"{pkg_name} has no __version__"


def test_version_format(pkg_name):
    """Version should follow semver-like format."""
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    if version is None:
        from importlib.metadata import version as get_version

        version = get_version(pkg_name.replace("_", "-"))
    parts = version.split(".")
    assert len(parts) >= 2, f"Version {version} should have at least major.minor"
