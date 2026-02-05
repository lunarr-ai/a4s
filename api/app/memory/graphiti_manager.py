from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable, Iterable
from datetime import UTC, datetime

from fastembed import TextEmbedding
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.client import EmbedderClient, EmbedderConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.nodes import EpisodeType

from app.config import Config, EmbeddingProvider, LLMProvider
from app.config import config as default_config
from app.memory.manager import MemoryManager
from app.memory.models import (
    CreateMemoryRequest,
    Memory,
    QueuedMemoryResponse,
    SearchMemoryRequest,
    UpdateMemoryRequest,
)

logger = logging.getLogger(__name__)


class FastEmbedEmbedderConfig(EmbedderConfig):
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"


class FastEmbedEmbedder(EmbedderClient):
    """Embedder using fastembed for local embeddings."""

    def __init__(self, config: FastEmbedEmbedderConfig | None = None) -> None:
        if config is None:
            config = FastEmbedEmbedderConfig()
        self.config = config
        self._client = TextEmbedding(model_name=config.embedding_model)

    async def create(self, input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]]) -> list[float]:
        if isinstance(input_data, str):
            texts = [input_data]
        else:
            texts = list(input_data)
        embeddings = list(self._client.embed(texts))
        return embeddings[0].tolist()[: self.config.embedding_dim]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        embeddings = list(self._client.embed(input_data_list))
        return [emb.tolist()[: self.config.embedding_dim] for emb in embeddings]


class GraphitiMemoryManager(MemoryManager):
    """Memory manager implementation using Graphiti knowledge graph."""

    def __init__(self, graphiti: Graphiti) -> None:
        self._graphiti = graphiti
        self._queues: dict[str, asyncio.Queue[Callable[[], Awaitable[None]]]] = {}
        self._workers: dict[str, asyncio.Task[None]] = {}

    @classmethod
    async def create(cls, config: Config | None = None) -> GraphitiMemoryManager:
        """Create a new GraphitiMemoryManager instance.

        Args:
            config: Optional configuration. Uses default config if not provided.

        Returns:
            A configured GraphitiMemoryManager instance.
        """
        cfg = config or default_config

        driver = FalkorDriver(
            host=cfg.graphiti_falkordb_host,
            port=cfg.graphiti_falkordb_port,
            username=cfg.graphiti_falkordb_username,
            password=cfg.graphiti_falkordb_password.get_secret_value() if cfg.graphiti_falkordb_password else None,
            database=cfg.graphiti_falkordb_database,
        )

        llm_client = cls._build_llm_client(cfg)
        embedder = cls._build_embedder(cfg)

        graphiti = Graphiti(
            graph_driver=driver,
            llm_client=llm_client,
            embedder=embedder,
        )
        await graphiti.build_indices_and_constraints()

        logger.info("Graphiti memory manager initialized")
        return cls(graphiti)

    @classmethod
    def _build_llm_client(cls, config: Config) -> OpenAIGenericClient:
        if config.memory_llm_provider == LLMProvider.OPENAI:
            api_key = config.openai_api_key.get_secret_value() if config.openai_api_key else ""
            llm_config = LLMConfig(
                api_key=api_key,
                model=config.memory_llm_model,
                base_url=config.memory_llm_base_url,
            )
        elif config.memory_llm_provider == LLMProvider.GOOGLE:
            api_key = config.google_api_key.get_secret_value() if config.google_api_key else ""
            llm_config = LLMConfig(
                api_key=api_key,
                model=config.memory_llm_model,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        elif config.memory_llm_provider == LLMProvider.OPENROUTER:
            api_key = config.openrouter_api_key.get_secret_value() if config.openrouter_api_key else ""
            llm_config = LLMConfig(
                api_key=api_key,
                model=config.memory_llm_model,
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.memory_llm_provider}")

        return OpenAIGenericClient(config=llm_config)

    @classmethod
    def _build_embedder(cls, config: Config) -> EmbedderClient:
        if config.memory_embedding_provider == EmbeddingProvider.FASTEMBED:
            return FastEmbedEmbedder(
                config=FastEmbedEmbedderConfig(
                    embedding_model=config.memory_embedding_model,
                    embedding_dim=config.memory_embedding_dims,
                )
            )

        if config.memory_embedding_provider == EmbeddingProvider.OPENAI:
            api_key = config.openai_api_key.get_secret_value() if config.openai_api_key else ""
            return OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    api_key=api_key,
                    embedding_model=config.memory_embedding_model,
                    embedding_dim=config.memory_embedding_dims,
                )
            )

        raise ValueError(f"Unsupported embedding provider for Graphiti: {config.memory_embedding_provider}")

    def _build_group_id(self, agent_id: str) -> str:
        return f"agent-{agent_id}"

    async def add(self, request: CreateMemoryRequest, owner_id: str, requester_id: str) -> QueuedMemoryResponse:
        """Add a new memory to the knowledge graph.

        Args:
            request: Memory creation request.
            owner_id: ID of the agent's owner.
            requester_id: ID of the requester.

        Returns:
            Response indicating the memory has been queued for processing.

        Raises:
            PermissionError: If requester is not the owner.
        """
        if requester_id != owner_id:
            raise PermissionError("Only the owner can write to agent memory")

        if isinstance(request.messages, str):
            body = request.messages
        else:
            body = "\n".join(f"{m['role']}: {m['content']}" for m in request.messages)

        group_id = self._build_group_id(request.agent_id)
        name = f"memory_{datetime.now(UTC).isoformat()}"

        async def process_episode() -> None:
            await self._graphiti.add_episode(
                name=name,
                episode_body=body,
                source=EpisodeType.text,
                source_description="memory_api",
                reference_time=datetime.now(UTC),
                group_id=group_id,
            )

        await self._enqueue_episode(group_id, process_episode)

        return QueuedMemoryResponse(
            message=f"Memory '{name}' queued for processing",
            group_id=group_id,
        )

    async def _enqueue_episode(self, group_id: str, process_func: Callable[[], Awaitable[None]]) -> None:
        if group_id not in self._queues:
            self._queues[group_id] = asyncio.Queue()

        await self._queues[group_id].put(process_func)

        if group_id not in self._workers or self._workers[group_id].done():
            self._workers[group_id] = asyncio.create_task(self._process_queue(group_id))

    async def _process_queue(self, group_id: str) -> None:
        logger.info("Starting queue worker for group_id: %s", group_id)

        try:
            while True:
                try:
                    process_func = await asyncio.wait_for(self._queues[group_id].get(), timeout=60.0)
                except TimeoutError:
                    if self._queues[group_id].empty():
                        logger.info("Queue empty, stopping worker for: %s", group_id)
                        break
                    continue

                try:
                    await process_func()
                except Exception:
                    logger.exception("Error processing episode for group_id: %s", group_id)
                finally:
                    self._queues[group_id].task_done()
        except asyncio.CancelledError:
            logger.info("Queue worker cancelled for group_id: %s", group_id)
        finally:
            self._workers.pop(group_id, None)

    async def search(self, request: SearchMemoryRequest) -> list[Memory]:
        """Search for memories.

        Args:
            request: Search request.

        Returns:
            List of matching memories.
        """
        group_ids = [self._build_group_id(request.agent_id)]

        edges = await self._graphiti.search(
            query=request.query,
            group_ids=group_ids,
            num_results=request.limit,
        )

        return [
            Memory(
                id=edge.uuid,
                content=edge.fact,
                metadata={
                    "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
                },
            )
            for edge in edges
        ]

    async def update(self, memory_id: str, request: UpdateMemoryRequest) -> Memory:
        raise NotImplementedError(
            "Graphiti does not support direct memory updates. "
            "Add new information as a new memory to update the knowledge graph."
        )

    async def delete(self, memory_id: str, owner_id: str, requester_id: str) -> None:
        """Delete a memory.

        Args:
            memory_id: ID of the memory to delete.
            owner_id: ID of the agent's owner.
            requester_id: ID of the requester.

        Raises:
            PermissionError: If requester is not the owner.
        """
        if requester_id != owner_id:
            raise PermissionError("Only the owner can delete agent memory")
        await self._graphiti.remove_episode(memory_id)

    async def close(self) -> None:
        for task in self._workers.values():
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers.values(), return_exceptions=True)
        self._workers.clear()
        self._queues.clear()
        await self._graphiti.close()
