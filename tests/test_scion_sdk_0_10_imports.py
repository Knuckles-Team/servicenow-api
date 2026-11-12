"""Every scion_sdk import in this repository resolves on the pinned SDK release."""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "node_modules", "build", "dist", ".tox", "__pycache__"}


def _python_files() -> list[Path]:
    return [
        p
        for p in ROOT.rglob("*.py")
        if not (set(p.relative_to(ROOT).parts) & SKIP)
        and not any(part.startswith(".") for part in p.relative_to(ROOT).parts)
    ]


def _is_sdk(name: str | None) -> bool:
    return bool(name) and (name == "scion_sdk" or name.startswith("scion_sdk."))


def test_every_scion_sdk_import_resolves_on_the_pinned_release() -> None:
    missing: list[str] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if (
                        _is_sdk(alias.name)
                        and importlib.util.find_spec(alias.name) is None
                    ):
                        missing.append(f"{rel}:{node.lineno} {alias.name}")
            elif (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and _is_sdk(node.module)
            ):
                if importlib.util.find_spec(node.module) is None:
                    missing.append(f"{rel}:{node.lineno} {node.module}")
                    continue
                module = importlib.import_module(node.module)
                for alias in node.names:
                    if alias.name == "*" or hasattr(module, alias.name):
                        continue
                    if importlib.util.find_spec(f"{node.module}.{alias.name}") is None:
                        missing.append(
                            f"{rel}:{node.lineno} {node.module}.{alias.name}"
                        )
    assert not missing, (
        "scion_sdk names that do not exist on the pinned release:\n"
        + "\n".join(missing)
    )
