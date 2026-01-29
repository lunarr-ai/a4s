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
    async def add(self, request: CreateMemoryRequest) -> Memory | QueuedMemoryResponse:
        """Add a new memory."""

    @abstractmethod
    async def search(self, request: SearchMemoryRequest) -> list[Memory]:
        """Search for memories."""

    @abstractmethod
    async def update(self, memory_id: str, request: UpdateMemoryRequest) -> Memory:
        """Update a memory."""

    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Delete a memory."""

    async def close(self) -> None:  # noqa: B027
        """Close any resources held by the manager."""
