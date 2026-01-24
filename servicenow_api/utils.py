#!/usr/bin/python
# coding: utf-8

import os
import pickle
import yaml
from pathlib import Path
from typing import Any, Union, List, Optional
from importlib.resources import files, as_file
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from fasta2a import Skill


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
