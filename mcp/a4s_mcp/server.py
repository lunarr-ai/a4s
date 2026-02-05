from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from uuid import uuid4

import httpx
from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    JSONRPCErrorResponse,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    SendMessageRequest,
    Task,
    TextPart,
)
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.session import ServerSession

from a4s_mcp.config import config


@dataclass
class AppContext:
    """Application context shared across MCP tools."""

    client: httpx.AsyncClient


@asynccontextmanager
async def mcp_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    # TODO: Get requester identity from auth token instead of config
    headers = {}
    if config.requester_id:
        headers["X-Requester-Id"] = config.requester_id
    async with httpx.AsyncClient(base_url=config.api_base_url, headers=headers) as client:
        yield AppContext(client=client)


SERVER_INSTRUCTIONS = """A4S enables agent orchestration, skills, and memory.

<agent-collaboration>
To delegate work to other agents:
1. Search for agents matching the task (use specific terms like "addition" not generic "math")
2. Select agent(s) whose description directly matches the task
3. Send the task to selected agent(s) and return their response(s)
</agent-collaboration>

<skills>
To use a skill:
1. Search for skills by capability
2. Read the skill's instructions resource
3. Activate the skill for detailed guidance
</skills>

<memory>
Store context for semantic retrieval to enable better reasoning in future interactions.

When to add memory:
- User preference is shared (e.g., "I prefer dark mode", "Call me Alex")
- Decision or suggestion is made that should persist
- Goal or task is completed
- New entity is introduced (person, project, concept)
- User gives feedback or clarification

All memories are public. Only the owner can write/delete memories.

NEVER store sensitive info (credentials, API keys, passwords, PII) in memory.
</memory>
"""

mcp = FastMCP("A4S MCP Server", instructions=SERVER_INSTRUCTIONS, lifespan=mcp_lifespan)


@mcp.tool()
async def search_agents(
    ctx: Context[ServerSession, AppContext],
    query: str,
    limit: int = 10,
) -> dict:
    """Search for agents by name, description, or capability.

    Args:
        query: Search query (e.g., "code review").
        limit: Max results (default 10).
    """
    client = ctx.request_context.lifespan_context.client
    resp = await client.get("/api/v1/agents/search", params={"query": query, "limit": limit})
    resp.raise_for_status()
    data = resp.json()
    return {
        "agents": [{"id": a["id"], "name": a["name"], "description": a["description"]} for a in data["agents"]],
        "query": query,
    }


@mcp.tool()
async def send_a2a_message(  # noqa: C901
    ctx: Context[ServerSession, AppContext],
    agent_id: str,
    message: str,
) -> dict:
    """Send a message to an agent via A2A protocol.

    Args:
        agent_id: Agent ID from search_agents.
        message: Text message to send.
    """
    api_client = ctx.request_context.lifespan_context.client
    resp = await api_client.get(f"/api/v1/agents/{agent_id}")
    if resp.status_code == 404:
        raise ToolError(f"Agent '{agent_id}' not found. Use search_agents to find agents.")
    resp.raise_for_status()
    agent = resp.json()
    agent_url = agent["url"]

    timeout = httpx.Timeout(120.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as http_client:
        card_resp = await http_client.get(f"{agent_url}/.well-known/agent.json")
        card_resp.raise_for_status()
        agent_card = AgentCard.model_validate(card_resp.json())
        a2a_client = A2AClient(http_client, agent_card=agent_card)

        msg = Message(
            role="user",
            parts=[TextPart(text=message)],
            message_id=str(uuid4()),
        )
        payload = MessageSendParams(
            message=msg,
            configuration=MessageSendConfiguration(accepted_output_modes=["text"]),
        )
        request = SendMessageRequest(id=str(uuid4()), params=payload)

        response = await a2a_client.send_message(request)

    text_parts: list[str] = []
    state = "unknown"

    if isinstance(response.root, JSONRPCErrorResponse):
        raise ToolError(f"A2A error: {response.root.error.message}")

    def extract_text(parts: list) -> list[str]:
        texts = []
        for part in parts:
            inner = part.root if hasattr(part, "root") else part
            if isinstance(inner, TextPart):
                texts.append(inner.text)
        return texts

    result = response.root.result
    if isinstance(result, Task):
        state = result.status.state.value if result.status else "unknown"
        if result.artifacts:
            for artifact in result.artifacts:
                text_parts.extend(extract_text(artifact.parts))
        if result.status and result.status.message:
            text_parts.extend(extract_text(result.status.message.parts))
    elif isinstance(result, Message):
        state = "completed"
        text_parts.extend(extract_text(result.parts))

    return {"state": state, "text": "\n".join(text_parts) if text_parts else None}


@mcp.tool()
async def search_skills(
    ctx: Context[ServerSession, AppContext],
    query: str,
    limit: int = 10,
) -> dict:
    """Search for skills by name or description.

    Args:
        query: Search query (e.g., "create PDF").
        limit: Max results (default 10).
    """
    client = ctx.request_context.lifespan_context.client
    resp = await client.get("/api/v1/skills/search", params={"query": query, "limit": limit})
    resp.raise_for_status()
    data = resp.json()
    return {
        "skills": [{"name": s["name"], "description": s["description"]} for s in data["skills"]],
        "query": query,
        "limit": limit,
    }


@mcp.tool()
async def add_memory(
    ctx: Context[ServerSession, AppContext],
    messages: str | list[dict[str, str]],
    agent_id: str,
) -> dict:
    """Store a memory.

    Args:
        messages: Conversation [{"role": "user", "content": "..."}] or plain text.
        agent_id: Agent identifier for scoping (required).
    """
    client = ctx.request_context.lifespan_context.client
    payload: dict = {"messages": messages, "agent_id": agent_id}
    resp = await client.post("/api/v1/memories", json=payload)
    resp.raise_for_status()
    data = resp.json()
    return {"message": data.get("message", "Memory queued"), "group_id": data.get("group_id", "")}


@mcp.tool()
async def search_memories(
    ctx: Context[ServerSession, AppContext],
    query: str,
    agent_id: str,
    limit: int = 10,
) -> dict:
    """Search memories for an agent.

    Args:
        query: Natural language search (e.g., "color preferences").
        agent_id: Agent identifier for scoping (required).
        limit: Max results (default 10).
    """
    client = ctx.request_context.lifespan_context.client
    payload = {"query": query, "agent_id": agent_id, "limit": limit}
    resp = await client.post("/api/v1/memories/search", json=payload)
    resp.raise_for_status()
    data = resp.json()
    memories = [{"id": m["id"], "content": m["content"], "score": m.get("score")} for m in data]
    return {"memories": memories, "query": query, "count": len(memories)}


@mcp.tool()
async def update_memory(
    ctx: Context[ServerSession, AppContext],
    memory_id: str,
    content: str,
) -> dict:
    """Update an existing memory's content.

    Args:
        memory_id: ID from search_memories.
        content: New content text.
    """
    client = ctx.request_context.lifespan_context.client
    resp = await client.put(f"/api/v1/memories/{memory_id}", json={"content": content})
    resp.raise_for_status()
    data = resp.json()
    return {"id": data["id"], "content": data["content"]}


@mcp.tool()
async def delete_memory(
    ctx: Context[ServerSession, AppContext],
    memory_id: str,
    agent_id: str,
) -> dict:
    """Delete a memory. Only owner can delete.

    Args:
        memory_id: ID from search_memories.
        agent_id: Agent identifier owning the memory (required).
    """
    client = ctx.request_context.lifespan_context.client
    resp = await client.delete(f"/api/v1/memories/{memory_id}", params={"agent_id": agent_id})
    resp.raise_for_status()
    return {"deleted": True, "memory_id": memory_id}


@mcp.resource("skill://{skill_name}/instructions")
async def get_skill_instructions(skill_name: str) -> str:
    """Get the SKILL.md instructions for a skill.

    Returns the full body content of the skill's SKILL.md file,
    which contains detailed instructions for using the skill.
    """
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.get(f"/api/v1/skills/by-name/{skill_name}")
        resp.raise_for_status()
        skill = resp.json()
        return skill["body"]


@mcp.resource("skill://{skill_name}/file/{path}")
async def get_skill_file(skill_name: str, path: str) -> bytes:
    """Get a specific file associated with a skill.

    Returns the content of the specified file from the skill's
    associated files (scripts, references, assets, etc.).
    """
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.get(f"/api/v1/skills/by-name/{skill_name}")
        resp.raise_for_status()
        skill = resp.json()
        skill_id = skill["id"]

        resp = await client.get(f"/api/v1/skills/{skill_id}/files/{path}")
        resp.raise_for_status()
        return resp.content


@mcp.prompt()
async def activate_skill(skill_name: str) -> str:
    """Generate instructions for activating and using a specific skill.

    Args:
        skill_name: Name of the skill to activate.

    Returns:
        Formatted prompt with skill instructions.
    """
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.get(f"/api/v1/skills/by-name/{skill_name}")
        if resp.status_code != 200:
            return f"Error: Skill '{skill_name}' not found. Use search_skills to find available skills."

        skill = resp.json()

    parts = [f"# Skill: {skill['name']}", "", "## Description", skill["description"], ""]

    if skill.get("compatibility"):
        parts.extend(["## Compatibility", skill["compatibility"], ""])

    if skill.get("allowed_tools"):
        parts.extend(["## Allowed Tools", ", ".join(skill["allowed_tools"]), ""])

    if skill.get("body"):
        parts.extend(["## Instructions", skill["body"], ""])

    parts.extend(["---", "You are now operating with this skill activated. Follow the instructions above."])

    return "\n".join(parts)
