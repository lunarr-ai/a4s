from typing import TYPE_CHECKING, Annotated
from uuid import uuid4

import httpx
from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from app.models import Agent, AgentMode, Channel

if TYPE_CHECKING:
    from app.broker.channel_registry import ChannelRegistry
    from app.broker.registry import AgentRegistry
    from app.runtime.agent_scheduler import AgentScheduler

PROXY_TIMEOUT = httpx.Timeout(timeout=300.0, connect=30.0)

router = APIRouter(prefix="/channels", tags=["channels"])


class CreateChannelRequest(BaseModel):
    """Request body for creating a channel."""

    name: str = Field(description="Name of the channel.")
    description: str = Field(description="Description of the channel's purpose.")
    agent_ids: list[str] = Field(default_factory=list, description="Initial list of agent IDs.")
    owner_id: str = Field(description="ID of the channel's owner.")


class UpdateChannelRequest(BaseModel):
    """Request body for updating a channel."""

    name: str | None = Field(default=None, description="New name for the channel.")
    description: str | None = Field(default=None, description="New description for the channel.")


class ChannelListResponse(BaseModel):
    """Response for listing channels."""

    channels: list[Channel]
    total: int


class AddAgentsRequest(BaseModel):
    """Request body for adding agents to a channel."""

    agent_ids: list[str] = Field(description="List of agent IDs to add.")


class RemoveAgentsRequest(BaseModel):
    """Request body for removing agents from a channel."""

    agent_ids: list[str] = Field(description="List of agent IDs to remove.")


class ChannelAgentSearchResponse(BaseModel):
    """Response for searching relevant agents in a channel."""

    agents: list[Agent]


class ChannelChatRequest(BaseModel):
    """Request body for sending a message to channel agents."""

    message: str = Field(description="The message to send to agents.")
    agent_ids: list[str] = Field(description="List of agent IDs to send the message to.")


class AgentChatResult(BaseModel):
    """Result of sending a message to a single agent."""

    agent_id: str
    agent_name: str
    response: str | None = None
    error: str | None = None


class ChannelChatResponse(BaseModel):
    """Response for channel chat."""

    results: list[AgentChatResult]


@router.post("", status_code=201)
async def create_channel(request: Request, body: CreateChannelRequest) -> Channel:
    """Create a new channel.

    Args:
        request: FastAPI request object.
        body: Channel creation details.

    Returns:
        The created channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    channel_id = str(uuid4())
    channel = Channel(
        id=channel_id,
        name=body.name,
        description=body.description,
        agent_ids=body.agent_ids,
        owner_id=body.owner_id,
    )
    await channel_registry.create_channel(channel)
    return channel


@router.get("")
async def list_channels(
    request: Request,
    offset: Annotated[int, Query(ge=0, description="Number of channels to skip.")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of channels to return.")] = 50,
) -> ChannelListResponse:
    """List channels with pagination.

    Args:
        request: FastAPI request object.
        offset: Number of channels to skip.
        limit: Maximum number of channels to return.

    Returns:
        Paginated list of channels.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    channels = await channel_registry.list_channels(offset=offset, limit=limit)
    return ChannelListResponse(channels=channels, total=len(channels))


@router.get("/{channel_id}")
async def get_channel(request: Request, channel_id: str) -> Channel:
    """Get a channel by ID.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel to retrieve.

    Returns:
        The channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    return await channel_registry.get_channel(channel_id)


@router.put("/{channel_id}")
async def update_channel(request: Request, channel_id: str, body: UpdateChannelRequest) -> Channel:
    """Update a channel.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel to update.
        body: Update details.

    Returns:
        The updated channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    return await channel_registry.update_channel(channel_id, updates)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(request: Request, channel_id: str) -> None:
    """Delete a channel.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel to delete.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    await channel_registry.delete_channel(channel_id)


@router.post("/{channel_id}/agents")
async def add_agents_to_channel(request: Request, channel_id: str, body: AddAgentsRequest) -> Channel:
    """Add agents to a channel.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel.
        body: Agent IDs to add.

    Returns:
        The updated channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    return await channel_registry.update_channel(channel_id, {"add_agent_ids": body.agent_ids})


@router.delete("/{channel_id}/agents")
async def remove_agents_from_channel(request: Request, channel_id: str, body: RemoveAgentsRequest) -> Channel:
    """Remove agents from a channel.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel.
        body: Agent IDs to remove.

    Returns:
        The updated channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    return await channel_registry.update_channel(channel_id, {"remove_agent_ids": body.agent_ids})


@router.get("/{channel_id}/agents/search")
async def search_relevant_agents(
    request: Request,
    channel_id: str,
    query: Annotated[str, Query(description="Search query.")],
    limit: Annotated[int, Query(ge=1, le=50, description="Maximum number of results.")] = 5,
) -> ChannelAgentSearchResponse:
    """Search for relevant agents in a channel by query.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel.
        query: Search query string.
        limit: Maximum number of results.

    Returns:
        Matching agents from the channel.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    agent_registry: AgentRegistry = request.app.state.registry

    channel = await channel_registry.get_channel(channel_id)
    if not channel.agent_ids:
        return ChannelAgentSearchResponse(agents=[])

    all_relevant = await agent_registry.search_agents(query, limit=50)
    channel_agent_ids = set(channel.agent_ids)
    filtered = [a for a in all_relevant if a.id in channel_agent_ids][:limit]

    return ChannelAgentSearchResponse(agents=filtered)


@router.post("/{channel_id}/chat")
async def channel_chat(request: Request, channel_id: str, body: ChannelChatRequest) -> ChannelChatResponse:
    """Send a message to selected agents in a channel.

    Args:
        request: FastAPI request object.
        channel_id: ID of the channel.
        body: Chat request with message and selected agent IDs.

    Returns:
        Aggregated responses from agents.
    """
    channel_registry: ChannelRegistry = request.app.state.channel_registry
    agent_registry: AgentRegistry = request.app.state.registry
    scheduler: AgentScheduler = request.app.state.agent_scheduler

    channel = await channel_registry.get_channel(channel_id)
    channel_agent_ids = set(channel.agent_ids)
    invalid_agents = [aid for aid in body.agent_ids if aid not in channel_agent_ids]
    if invalid_agents:
        return ChannelChatResponse(
            results=[
                AgentChatResult(agent_id=aid, agent_name="", error="Agent not in channel") for aid in invalid_agents
            ]
        )

    results: list[AgentChatResult] = []
    request_id = str(uuid4())

    for agent_id in body.agent_ids:
        try:
            agent = await agent_registry.get_agent(agent_id)

            if agent.mode == AgentMode.SERVERLESS:
                await scheduler.ensure_running(agent_id)
                scheduler.record_activity(agent_id)

            a2a_request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "message/send",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": body.message}],
                        "messageId": str(uuid4()),
                    },
                },
            }

            async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as client:
                resp = await client.post(f"{agent.url}/", json=a2a_request)

            if resp.status_code == 200:
                data = resp.json()
                response_text = _extract_text_from_a2a_response(data)
                results.append(AgentChatResult(agent_id=agent_id, agent_name=agent.name, response=response_text))
            else:
                results.append(
                    AgentChatResult(agent_id=agent_id, agent_name=agent.name, error=f"HTTP {resp.status_code}")
                )
        except httpx.TimeoutException:
            results.append(AgentChatResult(agent_id=agent_id, agent_name=agent.name, error="Request timed out"))
        except httpx.ConnectError:
            results.append(
                AgentChatResult(agent_id=agent_id, agent_name=agent.name, error="Failed to connect to agent")
            )
        except Exception as e:
            results.append(
                AgentChatResult(agent_id=agent_id, agent_name=agent.name if "agent" in dir() else "", error=str(e))
            )

    return ChannelChatResponse(results=results)


def _extract_parts_text(parts: list | None) -> list[str]:
    if not parts:
        return []
    return [p.get("text") for p in parts if p.get("text")]


def _extract_text_from_a2a_response(data: dict) -> str | None:
    result = data.get("result")
    if not result:
        return None

    text_parts: list[str] = []

    for artifact in result.get("artifacts") or []:
        text_parts.extend(_extract_parts_text(artifact.get("parts")))

    text_parts.extend(_extract_parts_text(result.get("parts")))

    status = result.get("status")
    if status and status.get("message"):
        text_parts.extend(_extract_parts_text(status["message"].get("parts")))

    return "\n".join(text_parts) if text_parts else None
