from abc import ABC, abstractmethod

from app.memory.models import (
    CreateMemoryRequest,
    IngestDocumentRequest,
    IngestDocumentResponse,
    Memory,
    QueuedMemoryResponse,
    SearchMemoryRequest,
    UpdateMemoryRequest,
)


class MemoryManager(ABC):
    @abstractmethod
    async def add(
        self, request: CreateMemoryRequest, target_agent_id: str, requester_id: str
    ) -> Memory | QueuedMemoryResponse:
        """Add a new memory.

        Args:
            request: Memory creation request.
            target_agent_id: ID of the target agent.
            requester_id: ID of the requester.

        Returns:
            The created memory or queued response.

        Raises:
            PermissionError: If requester is not the target agent.
        """

    @abstractmethod
    async def search(self, request: SearchMemoryRequest) -> list[Memory]:
        """Search for memories.

        Args:
            request: Search request.

        Returns:
            List of matching memories based on access level.
        """

    @abstractmethod
    async def update(self, memory_id: str, request: UpdateMemoryRequest) -> Memory:
        """Update a memory."""

    @abstractmethod
    async def delete(self, memory_id: str, target_agent_id: str, requester_id: str) -> None:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete.
            target_agent_id: ID of the target agent.
            requester_id: ID of the requester.

        Raises:
            PermissionError: If requester is not the target agent.
        """

    @abstractmethod
    async def ingest_document(
        self, request: IngestDocumentRequest, target_agent_id: str, requester_id: str
    ) -> IngestDocumentResponse:
        """Ingest a document into memory.

        Args:
            request: Document ingestion request.
            target_agent_id: ID of the target agent.
            requester_id: ID of the requester.

        Returns:
            Response indicating the document has been queued.

        Raises:
            PermissionError: If requester is not the target agent.
        """

    async def close(self) -> None:  # noqa: B027
        """Close any resources held by the manager."""
