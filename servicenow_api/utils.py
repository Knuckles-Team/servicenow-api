#!/usr/bin/python
# coding: utf-8

import os
import httpx
import pickle
import yaml
import logging
from pathlib import Path
from typing import Union, List, Any, Optional
import json
from importlib.resources import files, as_file
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.huggingface import HuggingFaceModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.mistral import MistralModel
from fasta2a import Skill

try:

    from openai import AsyncOpenAI
    from pydantic_ai.providers.openai import OpenAIProvider
except ImportError:
    AsyncOpenAI = None
    OpenAIProvider = None

try:
    from groq import AsyncGroq
    from pydantic_ai.providers.groq import GroqProvider
except ImportError:
    AsyncGroq = None
    GroqProvider = None

try:
    from mistralai import Mistral
    from pydantic_ai.providers.mistral import MistralProvider
except ImportError:
    Mistral = None
    MistralProvider = None

try:
    from anthropic import AsyncAnthropic
    from pydantic_ai.providers.anthropic import AnthropicProvider
except ImportError:
    AsyncAnthropic = None
    AnthropicProvider = None


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


def to_float(string: Union[str, float] = None) -> float:
    if isinstance(string, float):
        return string
    if not string:
        return 0.0
    try:
        return float(string.strip())
    except ValueError:
        raise ValueError(f"Cannot convert '{string}' to float")


def to_list(string: Union[str, list] = None) -> list:
    if isinstance(string, list):
        return string
    if not string:
        return []
    try:
        return json.loads(string)
    except Exception:
        return string.split(",")


def to_dict(string: Union[str, dict] = None) -> dict:
    if isinstance(string, dict):
        return string
    if not string:
        return {}
    try:
        return json.loads(string)
    except Exception:
        raise ValueError(f"Cannot convert '{string}' to dict")


def prune_large_messages(messages: list[Any], max_length: int = 5000) -> list[Any]:
    """
    Summarize large tool outputs in the message history to save context window.
    Keeps the most recent tool outputs intact if they are the very last message,
    but generally we want to prune history.
    """
    pruned_messages = []
    for i, msg in enumerate(messages):
        content = getattr(msg, "content", None)
        if content is None and isinstance(msg, dict):
            content = msg.get("content")

        if isinstance(content, str) and len(content) > max_length:
            summary = (
                f"{content[:200]} ... "
                f"[Output truncated, original length {len(content)} characters] "
                f"... {content[-200:]}"
            )

            if isinstance(msg, dict):
                msg["content"] = summary
                pruned_messages.append(msg)
            elif hasattr(msg, "content"):
                try:
                    from copy import copy

                    new_msg = copy(msg)
                    new_msg.content = summary
                    pruned_messages.append(new_msg)
                except Exception:
                    pruned_messages.append(msg)
            else:
                pruned_messages.append(msg)
        else:
            pruned_messages.append(msg)

    return pruned_messages


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
    if __package__:
        top = __package__.partition(".")[0]
        if top and top != "__main__":
            return top

    try:
        file_path = Path(__file__).resolve()
        for parent in file_path.parents:
            if (
                (parent / "pyproject.toml").is_file()
                or (parent / "setup.py").is_file()
                or (parent / "__init__.py").is_file()
            ):
                return parent.name
    except Exception:
        pass

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


def get_http_client(
    ssl_verify: bool = True, timeout: float = 300.0
) -> httpx.AsyncClient | None:
    if not ssl_verify:
        return httpx.AsyncClient(verify=False, timeout=timeout)
    return None


def create_model(
    provider: str,
    model_id: str,
    base_url: Optional[str],
    api_key: Optional[str],
    ssl_verify: bool = True,
    timeout: float = 300.0,
):
    """
    Create a Pydantic AI model with the specified provider and configuration.

    Args:
        provider: The model provider (openai, anthropic, google, groq, mistral, huggingface, ollama)
        model_id: The specific model ID to use
        base_url: Optional base URL for the API
        api_key: Optional API key
        ssl_verify: Whether to verify SSL certificates (default: True)

    Returns:
        A Pydantic AI Model instance
    """
    http_client = None
    if not ssl_verify:
        http_client = httpx.AsyncClient(verify=False, timeout=timeout)

    if provider == "openai":
        target_base_url = base_url
        target_api_key = api_key

        if http_client and AsyncOpenAI and OpenAIProvider:
            client = AsyncOpenAI(
                api_key=target_api_key or os.environ.get("OPENAI_API_KEY"),
                base_url=target_base_url or os.environ.get("OPENAI_BASE_URL"),
                http_client=http_client,
            )
            provider_instance = OpenAIProvider(openai_client=client)
            return OpenAIChatModel(model_name=model_id, provider=provider_instance)

        if target_base_url:
            os.environ["OPENAI_BASE_URL"] = target_base_url
        if target_api_key:
            os.environ["OPENAI_API_KEY"] = target_api_key
        return OpenAIChatModel(model_name=model_id, provider="openai")

    elif provider == "ollama":
        target_base_url = base_url or "http://localhost:11434/v1"
        target_api_key = api_key or "ollama"

        if http_client and AsyncOpenAI and OpenAIProvider:
            client = AsyncOpenAI(
                api_key=target_api_key,
                base_url=target_base_url,
                http_client=http_client,
            )
            provider_instance = OpenAIProvider(openai_client=client)
            return OpenAIChatModel(model_name=model_id, provider=provider_instance)

        os.environ["OPENAI_BASE_URL"] = target_base_url
        os.environ["OPENAI_API_KEY"] = target_api_key
        return OpenAIChatModel(model_name=model_id, provider="openai")

    elif provider == "anthropic":
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key

        try:
            if http_client and AsyncAnthropic and AnthropicProvider:
                client = AsyncAnthropic(
                    api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
                    http_client=http_client,
                )
                provider_instance = AnthropicProvider(anthropic_client=client)
                return AnthropicModel(model_name=model_id, provider=provider_instance)
        except ImportError:
            pass

        return AnthropicModel(model_name=model_id)

    elif provider == "google":
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        return GoogleModel(model_name=model_id)

    elif provider == "groq":
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key

        if http_client and AsyncGroq and GroqProvider:
            client = AsyncGroq(
                api_key=api_key or os.environ.get("GROQ_API_KEY"),
                http_client=http_client,
            )
            provider_instance = GroqProvider(groq_client=client)
            return GroqModel(model_name=model_id, provider=provider_instance)

        return GroqModel(model_name=model_id)

    elif provider == "mistral":
        if api_key:
            os.environ["MISTRAL_API_KEY"] = api_key

        if http_client and Mistral and MistralProvider:
            pass

        return MistralModel(model_name=model_id)

    elif provider == "huggingface":
        if api_key:
            os.environ["HUGGING_FACE_API_KEY"] = api_key
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

    meta = getattr(tool_def, "meta", None)
    if isinstance(meta, dict):
        fastmcp = meta.get("fastmcp") or meta.get("_fastmcp") or {}
        tags_list = fastmcp.get("tags", [])
        if tags_list:
            return tags_list

        tags_list = meta.get("tags", [])
        if tags_list:
            return tags_list

    metadata = getattr(tool_def, "metadata", None)
    if isinstance(metadata, dict):
        tags_list = metadata.get("tags", [])
        if tags_list:
            return tags_list

        meta_nested = metadata.get("meta") or {}
        fastmcp = meta_nested.get("fastmcp") or meta_nested.get("_fastmcp") or {}
        tags_list = fastmcp.get("tags", [])
        if tags_list:
            return tags_list

        tags_list = meta_nested.get("tags", [])
        if tags_list:
            return tags_list

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
