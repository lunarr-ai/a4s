import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.broker.exceptions import (
    AgentNotRegisteredError,
    AgentRegistryConnectionError,
    AgentRegistryError,
    ChannelNotFoundError,
    ChannelRegistryConnectionError,
    ChannelRegistryError,
)
from app.broker.qdrant_registry import QdrantAgentRegistry
from app.broker.sqlite_channel_registry import SqliteChannelRegistry
from app.config import config
from app.memory.factory import create_memory_manager
from app.models import Agent, AgentMode, AgentModel, AgentStatus, SpawnConfig
from app.routers import health_router, v1_router
from app.runtime.agent_scheduler import AgentScheduler
from app.runtime.docker_manager import DockerRuntimeManager
from app.runtime.exceptions import AgentNotFoundError, AgentSpawnError, ImageNotFoundError
from app.skills import exceptions as skills_exc
from app.skills.sqlite_registry import SqliteSkillsRegistry

logger = logging.getLogger(__name__)

fastapi_app = FastAPI(title="A4S API")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(health_router)
fastapi_app.include_router(v1_router)


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


@fastapi_app.exception_handler(ChannelNotFoundError)
async def channel_not_found_handler(_request: Request, exc: ChannelNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@fastapi_app.exception_handler(ChannelRegistryConnectionError)
async def channel_registry_connection_error_handler(
    _request: Request, exc: ChannelRegistryConnectionError
) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@fastapi_app.exception_handler(ChannelRegistryError)
async def channel_registry_error_handler(_request: Request, exc: ChannelRegistryError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


async def _ensure_backbone_agent(registry: QdrantAgentRegistry) -> None:
    agent_id = config.backbone_agent_id
    try:
        await registry.get_agent(agent_id)
        logger.info("Backbone agent %s already registered", agent_id)
        return
    except AgentNotRegisteredError:
        pass

    container_name = f"a4s-agent-{agent_id}"
    agent = Agent(
        id=agent_id,
        name="backbone-router",
        description="Routes user messages to the most relevant agents in a channel",
        version="1.0.0",
        url=f"http://{container_name}:8000",
        port=8000,
        status=AgentStatus.PENDING,
        mode=AgentMode.PERMANENT,
        spawn_config=SpawnConfig(
            image=config.backbone_agent_image,
            model=AgentModel(
                provider=config.backbone_agent_model_provider,
                model_id=config.backbone_agent_model_id,
            ),
            instruction="Instruction managed via container environment",
            tools=[],
            mcp_tool_filter="search_agents,send_a2a_message",
        ),
    )
    await registry.register_agent(agent)
    logger.info("Registered backbone agent %s", agent_id)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    registry = QdrantAgentRegistry(
        url=config.qdrant_url,
        collection_name=config.registry_qdrant_collection,
    )
    runtime_manager = DockerRuntimeManager(
        api_base_url=config.api_base_url,
        agent_gateway_url=config.agent_gateway_url,
        network_name=config.agent_network,
    )
    skills_registry = await SqliteSkillsRegistry.create(config.skills_db_path)
    channel_registry = await SqliteChannelRegistry.create(config.channel_db_path)
    memory_manager = await create_memory_manager(config)
    agent_scheduler = AgentScheduler(
        runtime_manager=runtime_manager,
        registry=registry,
        idle_timeout=config.agent_idle_timeout,
        reaper_interval=config.agent_reaper_interval,
    )
    await agent_scheduler.start()

    app.state.registry = registry
    app.state.runtime_manager = runtime_manager
    app.state.skills_registry = skills_registry
    app.state.channel_registry = channel_registry
    app.state.memory_manager = memory_manager
    app.state.agent_scheduler = agent_scheduler

    await _ensure_backbone_agent(registry)

    try:
        yield
    finally:
        await agent_scheduler.stop()
        await registry.close()
        runtime_manager.close()
        await skills_registry.close()
        await channel_registry.close()
        await memory_manager.close()


app = fastapi_app
app.router.lifespan_context = lifespan
