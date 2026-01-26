from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from app.broker.exceptions import (
    AgentNotRegisteredError,
    AgentRegistryConnectionError,
    AgentRegistryError,
)
from app.broker.qdrant_registry import QdrantAgentRegistry
from app.broker.registry import AgentRegistry
from app.config import config
from app.runtime.docker_manager import DockerRuntimeManager
from app.runtime.exceptions import AgentNotFoundError, AgentSpawnError, ImageNotFoundError
from app.runtime.manager import RuntimeManager
from app.skills import exceptions as skills_exc
from app.skills.registry import SkillsRegistry
from app.skills.sqlite_registry import SqliteSkillsRegistry


@dataclass
class AppContext:
    """Application context shared across MCP tools."""

    registry: AgentRegistry
    runtime_manager: RuntimeManager
    skills_registry: SkillsRegistry


fastapi_app = FastAPI(title="A4S API")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@fastapi_app.exception_handler(AgentNotFoundError)
async def agent_not_found_handler(_request: Request, exc: AgentNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@fastapi_app.exception_handler(AgentSpawnError)
async def agent_spawn_error_handler(_request: Request, exc: AgentSpawnError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@fastapi_app.exception_handler(ImageNotFoundError)
async def image_not_found_handler(_request: Request, exc: ImageNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@fastapi_app.exception_handler(AgentNotRegisteredError)
async def agent_not_registered_handler(_request: Request, exc: AgentNotRegisteredError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@fastapi_app.exception_handler(AgentRegistryConnectionError)
async def agent_registry_connection_error_handler(_request: Request, exc: AgentRegistryConnectionError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@fastapi_app.exception_handler(AgentRegistryError)
async def agent_registry_error_handler(_request: Request, exc: AgentRegistryError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@fastapi_app.exception_handler(skills_exc.SkillNotFoundError)
async def skill_not_found_handler(_request: Request, exc: skills_exc.SkillNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@fastapi_app.exception_handler(skills_exc.SkillValidationError)
async def skill_validation_error_handler(_request: Request, exc: skills_exc.SkillValidationError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@fastapi_app.exception_handler(skills_exc.SkillRegistryConnectionError)
async def skill_registry_connection_error_handler(
    _request: Request, exc: skills_exc.SkillRegistryConnectionError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@fastapi_app.exception_handler(skills_exc.SkillRegistryError)
async def skill_registry_error_handler(_request: Request, exc: skills_exc.SkillRegistryError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@asynccontextmanager
async def mcp_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    registry = QdrantAgentRegistry(
        url=config.qdrant_url,
        collection_name=config.qdrant_collection_name,
    )
    runtime_manager = DockerRuntimeManager()
    skills_registry = await SqliteSkillsRegistry.create(config.skills_db_path)

    try:
        yield AppContext(registry=registry, runtime_manager=runtime_manager, skills_registry=skills_registry)
    finally:
        await registry.close()
        runtime_manager.close()
        await skills_registry.close()


mcp = FastMCP("A4S MCP Server", lifespan=mcp_lifespan)


@mcp.tool()
async def search_agents(
    query: str,
    ctx: Context[ServerSession, AppContext],
    limit: int = 10,
) -> list[dict]:
    """Search for agents using semantic search.

    Args:
        query: The search query text to find relevant agents.
        limit: Maximum number of results to return.

    Returns:
        List of agents matching the query.
    """
    registry = ctx.request_context.lifespan_context.registry
    agents = await registry.search_agents(query, limit)
    return [
        {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "url": agent.url,
            "port": agent.port,
            "status": agent.status.value,
        }
        for agent in agents
    ]


# Get the MCP ASGI app and mount it into FastAPI
mcp_starlette_app = mcp.streamable_http_app()
mcp_asgi_app = mcp_starlette_app.routes[0].app
fastapi_app.mount("/mcp", mcp_asgi_app)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with mcp.session_manager.run():
        yield


app = fastapi_app
app.router.lifespan_context = lifespan
