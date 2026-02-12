#!/usr/bin/env python
# coding: utf-8

import importlib
import inspect
from typing import List

__all__: List[str] = []

CORE_MODULES = [
    "servicenow_api.servicenow_api",
    "servicenow_api.servicenow_models",
    "servicenow_api.decorators",
    "servicenow_api.exceptions",
]

OPTIONAL_MODULES = {
    "servicenow_api.servicenow_agent": "a2a",
    "servicenow_api.servicenow_mcp": "mcp",
}


def _import_module_safely(module_name: str):
    """Try to import a module and return it, or None if not available."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def _expose_members(module):
    """Expose public classes and functions from a module into globals and __all__."""
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            __all__.append(name)


for module_name in CORE_MODULES:
    module = importlib.import_module(module_name)
    _expose_members(module)

for module_name, extra_name in OPTIONAL_MODULES.items():
    module = _import_module_safely(module_name)
    if module is not None:
        _expose_members(module)
        globals()[f"_{extra_name.upper()}_AVAILABLE"] = True
    else:
        globals()[f"_{extra_name.upper()}_AVAILABLE"] = False

_MCP_AVAILABLE = OPTIONAL_MODULES.get("servicenow_api.servicenow_mcp") in [
    m.__name__ for m in globals().values() if hasattr(m, "__name__")
]
_A2A_AVAILABLE = "servicenow_api.servicenow_agent" in globals()

__all__.extend(["_MCP_AVAILABLE", "_A2A_AVAILABLE"])


"""
ServiceNow API

A Python Wrapper for ServiceNow API
"""
