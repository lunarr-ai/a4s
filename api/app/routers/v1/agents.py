from typing import TYPE_CHECKING, Annotated

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.models import Agent, AgentMode, AgentStatus, SpawnConfig
from app.runtime.models import SpawnAgentRequest
from app.utils import generate_agent_id

if TYPE_CHECKING:
    from app.broker.registry import AgentRegistry
    from app.runtime.agent_scheduler import AgentScheduler
    from app.runtime.manager import RuntimeManager

PROXY_TIMEOUT = httpx.Timeout(timeout=300.0, connect=30.0)
EXCLUDED_HEADERS = frozenset({"host", "content-length", "transfer-encoding", "content-encoding"})

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
    owner_id: str = Field(description="ID of the agent's owner.")
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
        owner_id=body.owner_id,
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
        owner_id=agent.owner_id,
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


@router.api_route("/{agent_id}/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_agent(request: Request, agent_id: str, path: str = "") -> Response:
    """Proxy request to agent container with cold start.

    Args:
        request: FastAPI request object.
        agent_id: ID of the agent to proxy to.
        path: Path to forward to the agent.

    Returns:
        Proxied response from the agent.
    """
    if request.method == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Max-Age": "1728000",
            },
        )

    scheduler: AgentScheduler = request.app.state.agent_scheduler
    registry: AgentRegistry = request.app.state.registry

    agent = await registry.get_agent(agent_id)
    if agent.mode == AgentMode.SERVERLESS:
        await scheduler.ensure_running(agent_id)
        scheduler.record_activity(agent_id)

    target_url = f"{agent.url}/{path}"
    if request.query_params:
        target_url = f"{target_url}?{request.query_params}"

    headers = {k: v for k, v in request.headers.items() if k.lower() not in EXCLUDED_HEADERS}
    body = await request.body()

    async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as client:
        try:
            resp = await client.request(method=request.method, url=target_url, headers=headers, content=body)
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=504, detail="Agent request timed out") from e
        except httpx.ConnectError as e:
            raise HTTPException(status_code=502, detail="Failed to connect to agent") from e

    resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in EXCLUDED_HEADERS}
    resp_headers["Access-Control-Allow-Origin"] = "*"

    return Response(content=resp.content, status_code=resp.status_code, headers=resp_headers)
