#!/usr/bin/python
# coding: utf-8

import os
import pickle
import yaml
import logging
from pathlib import Path
from typing import Union, List, Any, Optional
from importlib.resources import files, as_file
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from fasta2a import Skill

logger = logging.getLogger(__name__)


def to_integer(string: Union[str, int] = None) -> int:
    if isinstance(string, int):
        return string
    if not string:
        return 0
    try:
        return int(string.strip())
    except ValueError:
        raise ValueError(f"Cannot convert '{string}' to integer")


def to_boolean(string: Union[str, bool] = None) -> bool:
    if isinstance(string, bool):
        return string
    if not string:
        return False
    normalized = str(string).strip().lower()
    true_values = {"t", "true", "y", "yes", "1"}
    false_values = {"f", "false", "n", "no", "0"}
    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert '{string}' to boolean")


def save_model(model: Any, file_name: str = "model", file_path: str = ".") -> str:
    pickle_file = os.path.join(file_path, f"{file_name}.pkl")
    with open(pickle_file, "wb") as file:
        pickle.dump(model, file)
    return pickle_file


def load_model(file: str) -> Any:
    with open(file, "rb") as model_file:
        model = pickle.load(model_file)
    return model


def retrieve_package_name() -> str:
    """
    Returns the top-level package name of the module that imported this utils.py.

    Works reliably when utils.py is inside a proper package (with __init__.py or
    implicit namespace package) and the caller does normal imports.
    """
    # Most common case: utils.py is imported as  package.utils
    # __package__ is then 'package' or 'package.subpackage'
    if __package__:
        # Take only the top-level part
        top = __package__.partition(".")[0]
        if top and top != "__main__":
            return top

    # Fallback for scripts run directly or unusual import patterns
    try:
        file_path = Path(__file__).resolve()
        # Walk up until we find a plausible top-level package folder
        # (one that contains files like pyproject.toml, setup.py, README, or just assume 1–2 levels)
        for parent in file_path.parents:
            if (
                (parent / "pyproject.toml").is_file()
                or (parent / "setup.py").is_file()
                or (parent / "__init__.py").is_file()
            ):  # stop at namespace root
                return parent.name
    except Exception:
        pass

    # Last resort — usually wrong in packaged context, but better than crashing
    return "unknown_package"


def get_skills_path() -> str:
    skills_dir = files(retrieve_package_name()) / "skills"
    with as_file(skills_dir) as path:
        skills_path = str(path)
    return skills_path


def get_mcp_config_path() -> str:
    mcp_config_file = files(retrieve_package_name()) / "mcp_config.json"
    with as_file(mcp_config_file) as path:
        mcp_config_path = str(path)
    return mcp_config_path


def load_skills_from_directory(directory: str) -> List[Skill]:
    skills = []
    base_path = Path(directory)

    if not base_path.exists():
        print(f"Skills directory not found: {directory}")
        return skills

    for item in base_path.iterdir():
        if item.is_dir():
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                try:
                    with open(skill_file, "r") as f:
                        # Extract frontmatter
                        content = f.read()
                        if content.startswith("---"):
                            _, frontmatter, _ = content.split("---", 2)
                            data = yaml.safe_load(frontmatter)

                            skill_id = item.name
                            skill_name = data.get("name", skill_id)
                            skill_desc = data.get(
                                "description", f"Access to {skill_name} tools"
                            )
                            skills.append(
                                Skill(
                                    id=skill_id,
                                    name=skill_name,
                                    description=skill_desc,
                                    tags=[skill_id],
                                    input_modes=["text"],
                                    output_modes=["text"],
                                )
                            )
                except Exception as e:
                    print(f"Error loading skill from {skill_file}: {e}")

    return skills


def create_model(
    provider: str,
    model_id: str,
    base_url: Optional[str],
    api_key: Optional[str],
):
    if provider == "openai":
        target_base_url = base_url
        target_api_key = api_key
        if target_base_url:
            os.environ["OPENAI_BASE_URL"] = target_base_url
        if target_api_key:
            os.environ["OPENAI_API_KEY"] = target_api_key
        return OpenAIChatModel(model_name=model_id, provider="openai")

    elif provider == "anthropic":
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        return AnthropicModel(model_name=model_id)

    elif provider == "google":
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        return GoogleModel(model_name=model_id)

    elif provider == "huggingface":
        if api_key:
            os.environ["HF_TOKEN"] = api_key
        return HuggingFaceModel(model_name=model_id)
    return OpenAIChatModel(model_name=model_id, provider="openai")


def extract_tool_tags(tool_def: Any) -> List[str]:
    """
    Extracts tags from a tool definition object.

    Found structure in debug:
    tool_def.name (str)
    tool_def.meta (dict) -> {'fastmcp': {'tags': ['tag']}}

    This function checks multiple paths to be robust:
    1. tool_def.meta['fastmcp']['tags']
    2. tool_def.meta['tags']
    3. tool_def.metadata['tags'] (legacy/alternative wrapper)
    4. tool_def.metadata.get('meta')... (nested path)
    """
    tags_list = []

    # 1. Direct 'meta' attribute (seen in pydantic-ai / mcp.types.Tool)
    meta = getattr(tool_def, "meta", None)
    if isinstance(meta, dict):
        # Check fastmcp dict
        fastmcp = meta.get("fastmcp") or meta.get("_fastmcp") or {}
        tags_list = fastmcp.get("tags", [])
        if tags_list:
            return tags_list

        # Check direct tags in meta
        tags_list = meta.get("tags", [])
        if tags_list:
            return tags_list

    # 2. 'metadata' attribute (common in some wrappers)
    metadata = getattr(tool_def, "metadata", None)
    if isinstance(metadata, dict):
        # Path: metadata.tags
        tags_list = metadata.get("tags", [])
        if tags_list:
            return tags_list

        # Path: metadata.meta...
        meta_nested = metadata.get("meta") or {}
        fastmcp = meta_nested.get("fastmcp") or meta_nested.get("_fastmcp") or {}
        tags_list = fastmcp.get("tags", [])
        if tags_list:
            return tags_list

        tags_list = meta_nested.get("tags", [])
        if tags_list:
            return tags_list

    # 3. Direct 'tags' attribute
    tags_list = getattr(tool_def, "tags", [])
    if isinstance(tags_list, list) and tags_list:
        return tags_list

    return []


def tool_in_tag(tool_def: Any, tag: str) -> bool:
    """
    Checks if a tool belongs to a specific tag.
    """
    tool_tags = extract_tool_tags(tool_def)
    if tag in tool_tags:
        return True
    else:
        return False


def filter_tools_by_tag(tools: List[Any], tag: str) -> List[Any]:
    """
    Filters a list of tools for a given tag.
    """
    return [t for t in tools if tool_in_tag(t, tag)]
