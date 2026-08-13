"""Run an Agent Utilities gate against this checkout in an isolated worktree."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _is_agent_utilities_root(path: Path) -> bool:
    """Return whether *path* contains the framework and its gate scripts."""

    return (
        (path / "pyproject.toml").is_file()
        and (path / "agent_utilities").is_dir()
        and (path / "scripts").is_dir()
    )


def _agent_utilities_root(repository_root: Path) -> Path:
    """Resolve the framework checkout without assuming this worktree's location."""

    configured = os.environ.get("AGENT_UTILITIES_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
        if _is_agent_utilities_root(root):
            return root
        raise RuntimeError("AGENT_UTILITIES_ROOT is not an agent-utilities checkout")

    result = subprocess.run(
        ["git", "-C", str(repository_root), "worktree", "list", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    worktrees = [
        Path(line.removeprefix("worktree ")).resolve()
        for line in result.stdout.splitlines()
        if line.startswith("worktree ")
    ]
    # A repo checkout -- canonical or a linked worktree -- sits some number of
    # directory levels below the workspace root that also holds agent-utilities
    # as a sibling (one level for a top-level repo like agent-webui, two for an
    # agents/<name> package). Walk upward from each known worktree instead of
    # assuming a fixed depth, so one script works at every nesting level.
    for worktree in worktrees:
        for ancestor in (worktree, *worktree.parents):
            candidate = ancestor.parent / "agent-utilities"
            if _is_agent_utilities_root(candidate):
                return candidate

    raise RuntimeError(
        "Cannot locate an agent-utilities checkout. Set AGENT_UTILITIES_ROOT to the "
        "framework checkout before running pre-commit."
    )


def main() -> int:
    """Execute an Agent Utilities module or script in its locked environment."""

    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--module")
    target.add_argument("--script", type=Path)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    options = parser.parse_args()

    repository_root = Path(__file__).resolve().parents[1]
    try:
        framework_root = _agent_utilities_root(repository_root)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))

    uv = shutil.which("uv")
    if uv is None:
        parser.error("uv is required to run Agent Utilities pre-commit gates")

    command = [uv, "run", "--project", str(framework_root), "--locked", "python"]
    if options.module:
        command.extend(["-m", options.module])
    else:
        assert options.script is not None
        script = framework_root / options.script
        if not script.is_file():
            parser.error(f"Agent Utilities script was not found: {options.script}")
        command.append(str(script))
    arguments = options.arguments
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    command.extend(arguments)

    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        f"{repository_root}{os.pathsep}{existing}" if existing else str(repository_root)
    )
    return subprocess.run(command, cwd=repository_root, env=environment).returncode


if __name__ == "__main__":
    sys.exit(main())
