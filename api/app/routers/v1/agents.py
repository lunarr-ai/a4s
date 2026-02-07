from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import config as app_config
from app.models import Agent, AgentMode, AgentStatus, SpawnConfig
from app.runtime.models import SpawnAgentRequest
from app.utils import generate_agent_id

if TYPE_CHECKING:
    from app.broker.registry import AgentRegistry
    from app.runtime.agent_scheduler import AgentScheduler
    from app.runtime.manager import RuntimeManager

router = APIRouter(prefix="/agents", tags=["agents"])


class RegisterAgentRequest(BaseModel):
    """Request body for registering an agent."""

    name: str = Field(description="Name of the agent.")
    description: str = Field(description="Description of the agent capabilities.")
    version: str = Field(description="Version of the agent.", default="1.0.0")
    url: str | None = Field(
        default=None,
        description="URL where the agent is accessible. Auto-generated for managed agents. Provide only for external agents not managed by A4S.",
    )
    port: int = Field(description="Port the agent listens on.", default=8000)
    mode: AgentMode = Field(default=AgentMode.SERVERLESS, description="Runtime mode of the agent.")
    spawn_config: SpawnConfig = Field(description="Configuration for spawning agent containers.")


class AgentListResponse(BaseModel):
    """Response for listing agents."""

    agents: list[Agent]
    offset: int
    limit: int
    total: int


class AgentSearchResponse(BaseModel):
    """Response for searching agents."""

    agents: list[Agent]
    query: str
    limit: int


class AgentStatusResponse(BaseModel):
    """Response for agent status."""

    agent_id: str
    status: AgentStatus


@router.post("", status_code=201)
async def register_agent(request: Request, body: RegisterAgentRequest) -> Agent:
    """Register an agent in the registry.

    Args:
        request: FastAPI request object.
        body: Agent registration details.

    Returns:
        The registered agent.
    """
    registry: AgentRegistry = request.app.state.registry

    agent_id = generate_agent_id(body.name)
    # Auto-generate URL for managed agents; external agents provide their own
    url = body.url if body.url else f"http://a4s-agent-{agent_id}:{body.port}"
    agent = Agent(
        id=agent_id,
        name=body.name,
        description=body.description,
        version=body.version,
        url=url,
        port=body.port,
        status=AgentStatus.PENDING,
        mode=body.mode,
        spawn_config=body.spawn_config,
    )
    await registry.register_agent(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def unregister_agent(request: Request, agent_id: str) -> None:
    """Unregister an agent from the registry.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to unregister.
    """
    registry: AgentRegistry = request.app.state.registry
    await registry.unregister_agent(agent_id)


@router.get("")
async def list_agents(
    request: Request,
    offset: Annotated[int, Query(ge=0, description="Number of agents to skip.")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of agents to return.")] = 50,
) -> AgentListResponse:
    """List agents with pagination.

    Args:
        request: FastAPI request object.
        offset: Number of agents to skip.
        limit: Maximum number of agents to return.

    Returns:
        Paginated list of agents.
    """
    registry: AgentRegistry = request.app.state.registry
    agents = await registry.list_agents(offset=offset, limit=limit)
    return AgentListResponse(
        agents=agents,
        offset=offset,
        limit=limit,
        total=len(agents),
    )


@router.get("/search")
async def search_agents(
    request: Request,
    query: Annotated[str, Query(description="Search query.")],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of results.")] = 10,
) -> AgentSearchResponse:
    """Search agents by query.

    Args:
        request: FastAPI request object.
        query: Search query string.
        limit: Maximum number of results.

    Returns:
        Matching agents.
    """
    registry: AgentRegistry = request.app.state.registry
    agents = await registry.search_agents(query, limit=limit)
    backbone_id = app_config.backbone_agent_id
    if backbone_id:
        agents = [a for a in agents if a.id != backbone_id]
    return AgentSearchResponse(agents=agents, query=query, limit=limit)


@router.get("/{agent_id}")
async def get_agent(request: Request, agent_id: str) -> Agent:
    """Get an agent by ID.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to retrieve.

    Returns:
        The agent.
    """
    registry: AgentRegistry = request.app.state.registry
    return await registry.get_agent(agent_id)


@router.post("/{agent_id}/start")
async def start_agent(request: Request, agent_id: str) -> AgentStatusResponse:
    """Start an agent container using spawn_config from registry.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to start.

    Returns:
        Status of the started agent.
    """
    registry: AgentRegistry = request.app.state.registry
    runtime_manager: RuntimeManager = request.app.state.runtime_manager

    agent = await registry.get_agent(agent_id)

    spawn_request = SpawnAgentRequest(
        agent_id=agent.id,
        name=agent.name,
        image=agent.spawn_config.image,
        version=agent.version,
        port=agent.port,
        model=agent.spawn_config.model,
        description=agent.description,
        instruction=agent.spawn_config.instruction,
        tools=agent.spawn_config.tools,
        mcp_tool_filter=agent.spawn_config.mcp_tool_filter,
    )

    runtime_manager.spawn_agent(spawn_request)
    container_name = f"a4s-agent-{agent.id}"
    status = runtime_manager.get_agent_status(container_name)

    return AgentStatusResponse(agent_id=agent.id, status=status)


@router.post("/{agent_id}/stop")
async def stop_agent(request: Request, agent_id: str) -> AgentStatusResponse:
    """Stop an agent container.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to stop.

    Returns:
        Status of the stopped agent.
    """
    registry: AgentRegistry = request.app.state.registry
    runtime_manager: RuntimeManager = request.app.state.runtime_manager

    agent = await registry.get_agent(agent_id)
    container_name = f"a4s-agent-{agent.id}"

    runtime_manager.stop_agent(container_name)

    return AgentStatusResponse(agent_id=agent_id, status=AgentStatus.STOPPED)


@router.get("/{agent_id}/status")
async def get_agent_status(request: Request, agent_id: str) -> AgentStatusResponse:
    """Get the runtime status of an agent.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent.

    Returns:
        Current runtime status of the agent.
    """
    registry: AgentRegistry = request.app.state.registry
    runtime_manager: RuntimeManager = request.app.state.runtime_manager

    agent = await registry.get_agent(agent_id)
    container_name = f"a4s-agent-{agent.id}"
    status = runtime_manager.get_agent_status(container_name)

    return AgentStatusResponse(agent_id=agent_id, status=status)


@router.api_route("/{agent_id}/ensure-running", methods=["GET", "POST"])
async def ensure_running(request: Request, agent_id: str) -> Response:
    """Ensure agent is running (for nginx auth_request).

    Triggers cold start if needed, records activity.
    Accepts both GET (for nginx auth_request) and POST.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to ensure is running.

    Returns:
        Empty 200 response on success.
    """
    scheduler: AgentScheduler = request.app.state.agent_scheduler
    registry: AgentRegistry = request.app.state.registry

    agent = await registry.get_agent(agent_id)

    if agent.mode == AgentMode.SERVERLESS:
        await scheduler.ensure_running(agent_id)
        scheduler.record_activity(agent_id)

    return Response(status_code=200)
