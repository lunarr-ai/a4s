from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from app.memory.models import (
    CreateMemoryRequest,
    Memory,
    QueuedMemoryResponse,
    SearchMemoryRequest,
    UpdateMemoryRequest,
)

if TYPE_CHECKING:
    from app.broker.registry import AgentRegistry
    from app.memory.manager import MemoryManager

router = APIRouter(prefix="/memories", tags=["memories"])

REQUESTER_ID_HEADER = "X-Requester-Id"


async def _get_agent_owner_id(request: Request, agent_id: str) -> str:
    registry: AgentRegistry = request.app.state.registry
    agent = await registry.get_agent(agent_id)
    return agent.owner_id


def _get_requester_id(request: Request) -> str:
    requester_id = request.headers.get(REQUESTER_ID_HEADER)
    if not requester_id:
        raise HTTPException(status_code=400, detail=f"Missing {REQUESTER_ID_HEADER} header")
    return requester_id


@router.post("", status_code=201)
async def add_memory(request: Request, body: CreateMemoryRequest) -> Memory | QueuedMemoryResponse:
    """Add a new memory.

    Args:
        request: FastAPI request object.
        body: Memory creation details.

    Returns:
        The created memory or queued response depending on the provider.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    owner_id = await _get_agent_owner_id(request, body.agent_id)
    requester_id = _get_requester_id(request)

    try:
        return await memory_manager.add(body, owner_id, requester_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.post("/search")
async def search_memories(request: Request, body: SearchMemoryRequest) -> list[Memory]:
    """Search memories by query.

    Args:
        request: FastAPI request object.
        body: Search parameters.

    Returns:
        List of matching memories.
    """
    # TODO: Replace X-Requester-Id header with proper auth (JWT/API keys)
    memory_manager: MemoryManager = request.app.state.memory_manager
    return await memory_manager.search(body)


@router.put("/{memory_id}")
async def update_memory(request: Request, memory_id: str, body: UpdateMemoryRequest) -> Memory:
    """Update a memory.

    Args:
        request: FastAPI request object.
        memory_id: ID of the memory to update.
        body: Update details.

    Returns:
        The updated memory.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    return await memory_manager.update(memory_id, body)


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    request: Request,
    memory_id: str,
    agent_id: Annotated[str, Query(description="Agent ID owning the memory.")],
) -> None:
    """Delete a memory.

    Args:
        request: FastAPI request object.
        memory_id: ID of the memory to delete.
        agent_id: Agent ID owning the memory.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    owner_id = await _get_agent_owner_id(request, agent_id)
    requester_id = _get_requester_id(request)

    try:
        await memory_manager.delete(memory_id, owner_id, requester_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
