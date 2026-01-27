from __future__ import annotations

from mem0 import AsyncMemory

from app.config import Config
from app.config import config as default_config
from app.memory.config import to_mem0_config
from app.memory.manager import MemoryManager
from app.memory.models import CreateMemoryRequest, Memory, SearchMemoryRequest, UpdateMemoryRequest


class Mem0MemoryManager(MemoryManager):
    def __init__(self, memory: AsyncMemory) -> None:
        self.memory = memory

    @classmethod
    async def create(cls, config: Config | None = None) -> Mem0MemoryManager:
        """Create a new Mem0MemoryManager instance.

        Args:
            config: Optional configuration. Uses default config if not provided.

        Returns:
            A configured Mem0MemoryManager instance.
        """
        mem0_config = to_mem0_config(config or default_config)
        memory = await AsyncMemory.from_config(mem0_config)
        return cls(memory)

    async def add(self, request: CreateMemoryRequest) -> Memory:
        result = await self.memory.add(
            messages=request.messages,
            user_id=request.user_id,
            agent_id=request.agent_id,
            metadata=request.metadata,
        )
        mem = result["results"][0] if result.get("results") else {}
        return Memory(
            id=mem.get("id", ""),
            content=mem.get("memory", ""),
            metadata=mem.get("metadata"),
        )

    async def search(self, request: SearchMemoryRequest) -> list[Memory]:
        options = request.options or {}
        results = await self.memory.search(
            query=request.query,
            user_id=request.user_id,
            agent_id=request.agent_id,
            limit=request.limit,
            filters=request.metadata_filter,
            **options,
        )
        return [
            Memory(
                id=r.get("id", ""),
                content=r.get("memory", ""),
                score=r.get("score"),
                metadata=r.get("metadata"),
            )
            for r in results.get("results", [])
        ]

    async def update(self, memory_id: str, request: UpdateMemoryRequest) -> Memory:
        await self.memory.update(memory_id, request.content)
        return Memory(id=memory_id, content=request.content)

    async def delete(self, memory_id: str) -> None:
        await self.memory.delete(memory_id)
