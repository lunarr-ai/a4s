from abc import ABC, abstractmethod

from app.memory.models import (
    CreateMemoryRequest,
    Memory,
    QueuedMemoryResponse,
    SearchMemoryRequest,
    UpdateMemoryRequest,
)


class MemoryManager(ABC):
    @abstractmethod
    async def add(
        self, request: CreateMemoryRequest, owner_id: str, requester_id: str
    ) -> Memory | QueuedMemoryResponse:
        """Add a new memory.

        Args:
            request: Memory creation request.
            owner_id: ID of the agent's owner.
            requester_id: ID of the requester.

        Returns:
            The created memory or queued response.

        Raises:
            PermissionError: If requester is not the owner.
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
    async def delete(self, memory_id: str, owner_id: str, requester_id: str) -> None:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete.
            owner_id: ID of the agent's owner.
            requester_id: ID of the requester.

        Raises:
            PermissionError: If requester is not the owner.
        """

    async def close(self) -> None:  # noqa: B027
        """Close any resources held by the manager."""
