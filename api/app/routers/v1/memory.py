from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Request

from app.memory.models import (
    CreateMemoryRequest,
    Memory,
    QueuedMemoryResponse,
    SearchMemoryRequest,
    UpdateMemoryRequest,
)

if TYPE_CHECKING:
    from app.memory.manager import MemoryManager

router = APIRouter(prefix="/memories", tags=["memories"])


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
    return await memory_manager.add(body)


@router.post("/search")
async def search_memories(request: Request, body: SearchMemoryRequest) -> list[Memory]:
    """Search memories by query.

    Args:
        request: FastAPI request object.
        body: Search parameters.

    Returns:
        List of matching memories.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    return await memory_manager.search(body)


@router.get("/{memory_id}")
async def get_memory(request: Request, memory_id: str) -> Memory:
    """Get a memory by ID.

    Args:
        request: FastAPI request object.
        memory_id: ID of the memory to retrieve.

    Returns:
        The memory.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    search_request = SearchMemoryRequest(query="", limit=100)
    memories = await memory_manager.search(search_request)
    for mem in memories:
        if mem.id == memory_id:
            return mem
    raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")


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
async def delete_memory(request: Request, memory_id: str) -> None:
    """Delete a memory.

    Args:
        request: FastAPI request object.
        memory_id: ID of the memory to delete.
    """
    memory_manager: MemoryManager = request.app.state.memory_manager
    await memory_manager.delete(memory_id)
