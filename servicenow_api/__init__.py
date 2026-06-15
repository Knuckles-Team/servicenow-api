#!/usr/bin/env python

import importlib
import inspect
from typing import Any

__all__: list[str] = []

CORE_MODULES: list[str] = [
    "servicenow_api.api_client",
    "servicenow_api.servicenow_models",
]

OPTIONAL_MODULES = {
    "servicenow_api.agent_server": "agent_server",
    "servicenow_api.mcp_server": "mcp_server",
}


def _expose_members(module):
    """Expose public classes and functions from a module into globals and __all__."""
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            if name not in __all__:
                __all__.append(name)


# Eagerly import core modules (keeps API wrappers fast & light)
for module_name in CORE_MODULES:
    if module_name:
        module = importlib.import_module(module_name)
        _expose_members(module)

# Dynamic/lazy loading of optional modules (agent_server, mcp_server)
_loaded_optional_modules: dict[str, Any] = {}


def _import_module_safely(module_name: str):
    """Try to import a module and return it, or None if not available."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def __getattr__(name: str) -> Any:
    # Handle availability flags dynamically without eager imports
    if name == "_MCP_AVAILABLE":
        mcp_key = next((k for k in OPTIONAL_MODULES if "mcp_server" in k), None)
        if mcp_key:
            return _import_module_safely(mcp_key) is not None
        return False
    if name == "_AGENT_AVAILABLE":
        agent_key = next((k for k in OPTIONAL_MODULES if "agent_server" in k), None)
        if agent_key:
            return _import_module_safely(agent_key) is not None
        return False

    # Check optional modules
    for module_name in OPTIONAL_MODULES:
        if module_name not in _loaded_optional_modules:
            module = _import_module_safely(module_name)
            if module is not None:
                _loaded_optional_modules[module_name] = module
                _expose_members(module)

        module = _loaded_optional_modules.get(module_name)
        if module is not None and hasattr(module, name):
            return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(k for k in globals().keys() if not k.startswith("_")) + __all__)
