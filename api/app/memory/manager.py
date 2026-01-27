from abc import ABC, abstractmethod

from app.memory.models import CreateMemoryRequest, Memory, SearchMemoryRequest, UpdateMemoryRequest


class MemoryManager(ABC):
    @abstractmethod
    async def add(self, request: CreateMemoryRequest) -> Memory:
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
