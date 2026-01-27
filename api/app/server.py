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
    ctx: Context[ServerSession, AppContext],
    query: str,
    limit: int = 10,
) -> dict:
    """Search for agents by name/description.

    When to use:
    - Find agents by capability (query="code review")

    Args:
        query: Search query.
        limit: Max results to return (default 10).

    Returns:
        {agents, query}
    """
    registry = ctx.request_context.lifespan_context.registry

    agents = await registry.search_agents(query, limit)

    return {
        "agents": [
            {
                "id": str(agent.id),
                "name": agent.name,
                "description": agent.description,
                "url": agent.url,
                "port": agent.port,
                "status": agent.status.value,
            }
            for agent in agents
        ],
        "query": query,
        "limit": limit,
    }


@mcp.tool()
async def get_skills(
    names: list[str],
    ctx: Context[ServerSession, AppContext],
) -> dict:
    """Get metadata for specific skills by exact name.

    When to use:
    - Retrieve skills by name after search
    - Verify skills exist before activation

    When NOT to use:
    - Don't know names - use search_skills
    - Need instructions - read skill://{name}/instructions

    Args:
        names: List of exact skill names to retrieve.

    Returns:
        {found: [{name, description}], not_found: [names]}
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry
    found = []
    not_found = []

    for name in names:
        try:
            skill = await skills_registry.get_skill_by_name(name)
            found.append({"name": skill.name, "description": skill.description})
        except skills_exc.SkillNotFoundError:
            not_found.append(name)

    return {"found": found, "not_found": not_found}


@mcp.tool()
async def search_skills(
    ctx: Context[ServerSession, AppContext],
    query: str,
    limit: int = 10,
) -> dict:
    """Search for skills by name/description.

    When to use:
    - Find skills for a task (query="create PDF documents")

    When NOT to use:
    - Know exact skill names - use get_skills
    - Need full instructions - read skill://{name}/instructions

    Args:
        query: Search query.
        limit: Max results to return (default 10).

    Returns:
        {skills, query}
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry
    skills = await skills_registry.search_skills(query, limit)

    return {
        "skills": [{"name": s.name, "description": s.description} for s in skills],
        "query": query,
        "limit": limit,
    }


@mcp.resource("skill://{skill_name}/instructions")
async def get_skill_instructions(
    skill_name: str,
    ctx: Context[ServerSession, AppContext],
) -> str:
    """Get the SKILL.md instructions for a skill.

    Returns the full body content of the skill's SKILL.md file,
    which contains detailed instructions for using the skill.
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry
    skill = await skills_registry.get_skill_by_name(skill_name)
    return skill.body


@mcp.resource("skill://{skill_name}/file/{path}")
async def get_skill_file(
    skill_name: str,
    path: str,
    ctx: Context[ServerSession, AppContext],
) -> bytes:
    """Get a specific file associated with a skill.

    Returns the content of the specified file from the skill's
    associated files (scripts, references, assets, etc.).
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry
    skill = await skills_registry.get_skill_by_name(skill_name)
    skill_file = await skills_registry.get_skill_file_by_path(skill.id, path)
    return skill_file.content


@mcp.prompt()
async def activate_skill(
    skill_name: str,
    ctx: Context[ServerSession, AppContext],
) -> str:
    """Generate instructions for activating and using a specific skill.

    Args:
        skill_name: Name of the skill to activate.

    Returns:
        Formatted prompt with skill instructions.
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry

    try:
        skill = await skills_registry.get_skill_by_name(skill_name)
    except skills_exc.SkillNotFoundError:
        return f"Error: Skill '{skill_name}' not found. Use search_skills to find available skills."

    parts = [f"# Skill: {skill.name}", "", "## Description", skill.description, ""]

    if skill.compatibility:
        parts.extend(["## Compatibility", skill.compatibility, ""])

    if skill.allowed_tools:
        parts.extend(["## Allowed Tools", ", ".join(skill.allowed_tools), ""])

    if skill.body:
        parts.extend(["## Instructions", skill.body, ""])

    parts.extend(["---", "You are now operating with this skill activated. Follow the instructions above."])

    return "\n".join(parts)


@mcp.prompt()
async def discover_skills(
    task_description: str,
    ctx: Context[ServerSession, AppContext],
    limit: int = 5,
) -> str:
    """Find and recommend skills for a given task.

    Args:
        task_description: Description of the task to accomplish.
        limit: Maximum number of skills to recommend.

    Returns:
        Formatted prompt with skill recommendations.
    """
    skills_registry = ctx.request_context.lifespan_context.skills_registry
    skills = await skills_registry.search_skills(task_description, limit)

    if not skills:
        return (
            f"No skills found matching: {task_description}\n\n"
            "Consider trying a broader search query with search_skills."
        )

    parts = [
        "# Skill Discovery Results",
        "",
        f"Task: {task_description}",
        "",
        f"Found {len(skills)} relevant skill(s):",
        "",
    ]

    for i, skill in enumerate(skills, 1):
        parts.extend([f"## {i}. {skill.name}", skill.description, ""])
        if skill.tags:
            tags_str = ", ".join(f"{k}={v}" for k, v in skill.tags.items())
            parts.extend([f"Tags: {tags_str}", ""])

    parts.extend(
        [
            "---",
            "To activate a skill, use the activate_skill prompt with the skill name.",
            "To get more details, read its instructions: skill://{skill_name}/instructions",
        ]
    )

    return "\n".join(parts)


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
