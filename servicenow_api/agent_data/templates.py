import asyncio
from typing import Dict
from servicenow_api.models import PeriodicTask

CORE_FILES = {
    "IDENTITY": "IDENTITY.md",
    "USER": "USER.md",
    "CRON": "CRON.md",
    "CRON_LOG": "CRON_LOG.md",
    "AGENTS": "AGENTS.md",
    "MEMORY": "MEMORY.md",
    "MCP_CONFIG": "mcp_config.json",
}


tasks: list[PeriodicTask] = []
lock = asyncio.Lock()


TEMPLATES: Dict[str, str] = {
    "IDENTITY": """# IDENTITY.md - Who I Am, Core Personality, & Boundaries

 * **Name:** Servicenow Api Agent
 * **Role:** A research specialist agent for web search and information gathering using Servicenow Api.
 * **Emoji:** 🔍
 * **Vibe:** Precise, objective, concise

 ## System Prompt
 You are a Research Specialist Agent for Servicenow Api.
 You have access to a powerful metasearch engine to find information on the web.
 Your responsibilities:
 1. Analyze the user's research topic or query.
 2. Use the 'web_search' tool (or related skills) to find relevant information.
 3. Synthesize the search results into a clear, concise, and well-cited answer.
 4. Be objective and provide multiple perspectives if the topic is complex.
 5. If initial results are insufficient, refine your search queries and try again.
 6. Always include the URLs of the sources you used.
 7. MEMORY: You have long-term memory in MEMORY.md. If the user says 'remember', 'recall', or mentions past interactions, read MEMORY.md to retrieve context. Save important decisions, outcomes, and user preferences to MEMORY.md using append_note_to_file.
 """,
    "USER": """# USER.md - About the Human

* **Name:** User
* **Preferred name:** User
* **Timezone:** America/Chicago
* **Location:** Chicago, Illinois
* **Style:** Technical, concise, no fluff
""",
    "CRON": """# CRON.md - Persistent Scheduled Tasks
Last updated: {now}

## Active Tasks

| ID          | Name              | Interval (min) | Prompt                              | Last run          | Next approx |
|-------------|-------------------|----------------|-------------------------------------|-------------------|-------------|
| heartbeat   | Heartbeat         | 30             | @HEARTBEAT.md                       | —                 | —           |
| log-cleanup | Log Cleanup       | 720            | __internal:cleanup_cron_log         | —                 | —           |

*Edit this table to add/remove tasks. The agent reloads it periodically.*
*Use `@filename.md` in the Prompt column to load a multi-line prompt from a workspace file.*
""",
    "AGENTS": """# AGENTS.md - Known A2A Peer Agents
Last updated: {now}

This file is the local registry of other A2A agents this agent can discover and call.

## Registered A2A Peers

| Name            | Endpoint URL                    | Description                          | Capabilities                     | Auth      | Notes / Last Connected |
|-----------------|---------------------------------|--------------------------------------|----------------------------------|-----------|------------------------|
| SearchMaster    | http://search-agent:9000/a2a    | Advanced web researcher              | web_search, summarize, browse    | none      | 2026-02-20             |

*Add new rows manually or let the agent call `register_a2a_peer(...)`.*
""",
    "MEMORY": """# MEMORY.md - Long-term Memory
Last updated: {now}

This file stores important decisions, user preferences, and historical outcomes.
The agent should read this if the user asks "remember when" or similar.

## Log of Important Events
- [2026-02-21] Workspace initialized with advanced agent features.
""",
    "mcp_config": """{
  "mcpServers": {}
}
""",
    "CRON_LOG": """# CRON_LOG.md - Periodic Task Output Log
Last updated: {now}

This file stores the output of periodic/cron tasks.
The agent can read this to review what background tasks have done.
Old entries are automatically pruned to keep only the most recent results.

---
""",
}

NEW_SKILL_TEMPLATE = """---
name: {name}
description: {description}
version: 0.1.0
tags: [{tags}]
input_modes: [text]
output_modes: [text]
---

# {name} Skill

## When to use
{when_to_use}

## How to use
{how_to_use}

## Examples
- Example 1: ...
"""
