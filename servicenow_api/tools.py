import logging
import os
from datetime import datetime, timedelta
from typing import Any

from pydantic_ai import Agent, RunContext
from servicenow_api.models import PeriodicTask
from servicenow_api.utils import (
    read_md_file,
    append_to_md_file,
    update_cron_task_in_cron_md,
    load_a2a_peers,
    register_a2a_peer as register_a2a_peer_util,
    build_system_prompt_from_workspace,
    tasks,
    lock,
    create_new_skill,
    load_mcp_config,
    save_mcp_config,
    delete_skill_from_disk,
    read_skill_md,
    write_skill_md,
    to_boolean,
)

DEFAULT_WORKSPACE_TOOLS = to_boolean(string=os.environ.get("WORKSPACE_TOOLS", "True"))
DEFAULT_A2A_TOOLS = to_boolean(string=os.environ.get("A2A_TOOLS", "True"))
DEFAULT_SCHEDULER_TOOLS = to_boolean(string=os.environ.get("SCHEDULER_TOOLS", "True"))
DEFAULT_DYNAMIC_TOOLS = to_boolean(string=os.environ.get("DYNAMIC_TOOLS", "True"))

logger = logging.getLogger(__name__)


def register_agent_tools(agent: Agent):
    """Register universal workspace, A2A, and scheduler tools to the agent."""

    @agent.system_prompt
    def build_dynamic_prompt(ctx: RunContext[Any]) -> str:
        """Inject workspace files (IDENTITY, MEMORY, etc.) into the system prompt."""
        return build_system_prompt_from_workspace()

    # --- Workspace Tools ---
    if DEFAULT_WORKSPACE_TOOLS:

        @agent.tool
        async def read_workspace_file(ctx: RunContext[Any], filename: str) -> str:
            """Read content of any .md file in workspace (IDENTITY.md, CRON.md, etc.)."""
            return read_md_file(filename)

        @agent.tool
        async def append_note_to_file(
            ctx: RunContext[Any], filename: str, text: str
        ) -> str:
            """Append a short note or section to a workspace .md file."""
            append_to_md_file(filename, text)
            return f"Appended to {filename}"

        @agent.tool
        async def save_to_memory(ctx: RunContext[Any], text: str) -> str:
            """
            Save important decisions, outcomes, user preferences, or critical
            information to long-term memory (MEMORY.md).
            """
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            note = f"- [{timestamp}] {text}"
            append_to_md_file("MEMORY.md", note)
            return "Saved to memory."

        @agent.tool
        async def update_cron_task(
            ctx: RunContext[Any],
            task_id: str,
            name: str,
            interval_minutes: int,
            prompt: str,
        ) -> str:
            """Add or update a scheduled task in CRON.md"""
            task = {
                "id": task_id,
                "name": name,
                "interval_min": interval_minutes,
                "prompt": prompt,
            }
            update_cron_task_in_cron_md(task)
            return f"Updated/added task {task_id} in CRON.md"

    # --- A2A Peer Tools ---
    if DEFAULT_A2A_TOOLS:

        @agent.tool
        async def list_a2a_peers(ctx: RunContext[Any]) -> str:
            """List all known A2A peer agents."""
            peers = load_a2a_peers()
            if not peers:
                return "No A2A peers registered yet."
            lines = ["## Known A2A Peers"]
            for p in peers:
                lines.append(f"- **{p['name']}** → {p['url']}  ({p['capabilities']})")
            return "\n".join(lines)

        @agent.tool
        async def register_a2a_peer(
            ctx: RunContext[Any],
            name: str,
            url: str,
            description: str = "",
            capabilities: str = "",
            auth: str = "none",
        ) -> str:
            """Register or update another A2A agent this agent can call."""
            return register_a2a_peer_util(name, url, description, capabilities, auth)

    # --- Scheduler Tools ---
    if DEFAULT_SCHEDULER_TOOLS:

        @agent.tool
        async def schedule_periodic_task(
            ctx: RunContext[Any],
            task_id: str,
            name: str,
            interval_minutes: int,
            prompt: str,
        ) -> str:
            """Let the AI schedule itself to run any prompt (and therefore any tool) periodically."""
            if interval_minutes < 1:
                return "Interval must be ≥ 1 minute"
            async with lock:
                if any(t.id == task_id for t in tasks):
                    return f"Task ID '{task_id}' already exists"
                tasks.append(
                    PeriodicTask(
                        id=task_id,
                        name=name,
                        interval_minutes=interval_minutes,
                        prompt=prompt,
                        last_run=datetime.now()
                        - timedelta(minutes=interval_minutes + 5),  # run soon
                    )
                )
            return f"✅ Scheduled '{name}' (ID: {task_id}) every {interval_minutes} min"

        @agent.tool
        async def list_periodic_tasks(ctx: RunContext[Any]) -> str:
            """List all active periodic tasks."""
            async with lock:
                if not tasks:
                    return "No periodic tasks scheduled."
                lines = ["Active periodic tasks:"]
                now = datetime.now()
                for t in tasks:
                    if t.active:
                        mins_since = (now - t.last_run).total_seconds() / 60
                        next_in = max(0, int(t.interval_minutes - mins_since))
                        lines.append(
                            f"• {t.id}: {t.name} (every {t.interval_minutes} min, next ≈ {next_in} min)"
                        )
                return "\n".join(lines)

        @agent.tool
        async def cancel_periodic_task(ctx: RunContext[Any], task_id: str) -> str:
            """Cancel a periodic task by ID."""
            async with lock:
                for t in tasks:
                    if t.id == task_id:
                        t.active = False
                        return f"Cancelled task {task_id}"
            return f"Task {task_id} not found"

    # --- Dynamic Extension Tools ---
    if DEFAULT_DYNAMIC_TOOLS:

        @agent.tool
        async def update_mcp_config(
            ctx: RunContext[Any],
            server_name: str,
            server_url: str,
            transport: str = "sse",
        ) -> str:
            """Add or update an MCP server entry in mcp_config.json (auto-loaded on next run)."""
            config = load_mcp_config()
            config.setdefault("mcpServers", {})[server_name] = {
                "url": server_url,
                "transport": transport,
            }
            save_mcp_config(config)
            return f"✅ MCP server '{server_name}' added/updated. It will be available on next run."

        @agent.tool
        async def create_skill(
            ctx: RunContext[Any],
            name: str,
            description: str,
            when_to_use: str = "",
            how_to_use: str = "",
        ) -> str:
            """Create a brand-new skill folder + SKILL.md that will be auto-loaded on next run."""
            return create_new_skill(name, description, when_to_use, how_to_use)

        @agent.tool
        async def delete_skill(ctx: RunContext[Any], name: str) -> str:
            """Delete a skill folder from the workspace. Only works for workspace skills."""
            return delete_skill_from_disk(name)

        @agent.tool
        async def edit_skill(ctx: RunContext[Any], name: str, new_content: str) -> str:
            """
            Overwrite the SKILL.md of an existing workspace skill.
            Use this to refine a skill's logic, description, or examples.
            """
            return write_skill_md(name, new_content)

        @agent.tool
        async def get_skill_content(ctx: RunContext[Any], name: str) -> str:
            """Read the current SKILL.md of a workspace skill to prepare for editing."""
            return read_skill_md(name)
