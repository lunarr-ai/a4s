from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile

from app.memory.models import (
    ALLOWED_EXTENSIONS,
    MAX_DOCUMENT_SIZE,
    CreateMemoryRequest,
    IngestDocumentRequest,
    IngestDocumentResponse,
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


@router.post("/ingest-document", status_code=202)
async def ingest_document(
    request: Request,
    file: Annotated[UploadFile, File(description="Document file (.md, .txt)")],
    agent_id: Annotated[str, Form(description="Agent identifier for scoping")],
) -> IngestDocumentResponse:
    """Ingest a document file into agent memory.

    Args:
        request: FastAPI request object.
        file: Uploaded document file (markdown or text).
        agent_id: Agent identifier for scoping.

    Returns:
        Response indicating the document has been queued.

    Raises:
        HTTPException: If file format is invalid or content too large.
    """
    filename = file.filename or "unknown.txt"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {list(ALLOWED_EXTENSIONS.keys())}",
        )
    doc_format = ALLOWED_EXTENSIONS[ext]

    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text") from e

    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Document exceeds maximum size of {MAX_DOCUMENT_SIZE} characters",
        )
    if not content.strip():
        raise HTTPException(status_code=400, detail="Document content cannot be empty")

    doc_request = IngestDocumentRequest(
        content=content,
        agent_id=agent_id,
        format=doc_format,
        source=filename,
    )

    memory_manager: MemoryManager = request.app.state.memory_manager
    owner_id = await _get_agent_owner_id(request, agent_id)
    requester_id = _get_requester_id(request)

    try:
        return await memory_manager.ingest_document(doc_request, owner_id, requester_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
