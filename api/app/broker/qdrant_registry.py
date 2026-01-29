import logging
import uuid
from datetime import datetime

from fastembed import TextEmbedding
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.broker.exceptions import AgentNotRegisteredError, AgentRegistryConnectionError
from app.broker.registry import AgentRegistry
from app.models import Agent, AgentMode, AgentStatus, EmbeddingModel, SpawnConfig

logger = logging.getLogger(__name__)

DEFAULT_URL = "http://localhost:6333"
DEFAULT_COLLECTION_NAME = "agents"


class QdrantAgentRegistry(AgentRegistry):
    """Registry for AI agents using Qdrant vector database.

    Args:
        url: The URL of the Qdrant server.
        collection_name: The name of the collection to store agents.
        embedding_model: The embedding model for semantic search.
    """

    def __init__(
        self,
        url: str = DEFAULT_URL,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        self._client = AsyncQdrantClient(url=url)
        self._collection_name = collection_name

        self._embedding_model = embedding_model or EmbeddingModel.create()
        self._embedding_client = TextEmbedding(model_name=self._embedding_model.model_id)

    async def _ensure_collection(self) -> None:
        if not await self._client.collection_exists(self._collection_name):
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(
                    size=self._embedding_model.dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created collection %s", self._collection_name)

    def _embed(self, text: str) -> list[float]:
        embeddings = list(self._embedding_client.embed([text]))
        return embeddings[0].tolist()

    def _agent_to_payload(self, agent: Agent) -> dict:
        return {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "url": agent.url,
            "port": agent.port,
            "owner_id": agent.owner_id,
            "status": agent.status.value,
            "created_at": agent.created_at.isoformat(),
            "mode": agent.mode.value,
            "spawn_config": agent.spawn_config.model_dump() if agent.spawn_config else None,
        }

    def _payload_to_agent(self, payload: dict) -> Agent:
        spawn_config_data = payload.get("spawn_config")
        return Agent(
            id=payload["id"],
            name=payload["name"],
            description=payload["description"],
            version=payload["version"],
            url=payload["url"],
            port=payload["port"],
            owner_id=payload["owner_id"],
            status=AgentStatus(payload["status"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            mode=AgentMode(payload.get("mode", AgentMode.SERVERLESS.value)),
            spawn_config=SpawnConfig(**spawn_config_data) if spawn_config_data else None,
        )

    async def register_agent(self, agent: Agent) -> None:
        """Register an agent in the registry.

        Args:
            agent: The agent to register.

        Raises:
            AgentRegistryConnectionError: If the registry is unreachable.
        """
        await self._ensure_collection()
        try:
            document = f"{agent.name} {agent.description}"
            vector = self._embed(document)
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=self._agent_to_payload(agent),
            )
            await self._client.upsert(
                collection_name=self._collection_name,
                points=[point],
            )
            logger.info("Registered agent %s", agent.id)
        except UnexpectedResponse as e:
            logger.error("Failed to register agent %s: %s", agent.id, e)
            raise AgentRegistryConnectionError(f"Failed to register agent: {e}") from e

    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the registry.

        Args:
            agent_id: The ID of the agent to unregister.

        Raises:
            AgentNotRegisteredError: If the agent does not exist.
        """
        await self.get_agent(agent_id)
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=Filter(must=[FieldCondition(key="id", match=MatchValue(value=agent_id))]),
        )
        logger.info("Unregistered agent %s", agent_id)

    async def get_agent(self, agent_id: str) -> Agent:
        """Get an agent by ID.

        Args:
            agent_id: The ID of the agent to retrieve.

        Returns:
            The agent with the given ID.

        Raises:
            AgentNotRegisteredError: If the agent does not exist.
        """
        results, _ = await self._client.scroll(
            collection_name=self._collection_name,
            scroll_filter=Filter(must=[FieldCondition(key="id", match=MatchValue(value=agent_id))]),
            limit=1,
            with_payload=True,
        )
        if not results:
            logger.error("Agent %s not found", agent_id)
            raise AgentNotRegisteredError(f"Agent {agent_id} not found")
        return self._payload_to_agent(results[0].payload)

    async def list_agents(self, offset: int = 0, limit: int = 50) -> list[Agent]:
        """List agents with pagination.

        Args:
            offset: Number of agents to skip.
            limit: Maximum number of agents to return.

        Returns:
            List of agents starting from offset.
        """
        await self._ensure_collection()
        records, _ = await self._client.scroll(
            collection_name=self._collection_name,
            limit=limit,
            offset=offset,
            with_payload=True,
        )
        return [self._payload_to_agent(r.payload) for r in records]

    async def search_agents(self, query: str, limit: int = 10) -> list[Agent]:
        """Search for agents using semantic search.

        Args:
            query: The search query text.

        Returns:
            List of agents matching the query, ordered by relevance.
        """
        await self._ensure_collection()
        vector = self._embed(query)
        results = await self._client.query_points(
            collection_name=self._collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return [self._payload_to_agent(r.payload) for r in results.points]

    async def close(self) -> None:
        """Close the Qdrant client connection."""
        await self._client.close()
