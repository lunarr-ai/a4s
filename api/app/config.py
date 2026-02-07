from enum import Enum

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from app.models import ModelProvider


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    OPENROUTER = "openrouter"


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    FASTEMBED = "fastembed"


class MemoryProvider(str, Enum):
    GRAPHITI = "graphiti"


class VectorStoreProvider(str, Enum):
    QDRANT = "qdrant"


class Config(BaseSettings):
    # Backend
    cors_origins: list[str] = Field(default_factory=list)
    api_base_url: str = "http://localhost:8000"
    agent_gateway_url: str = "http://localhost:8080"
    agent_network: str = "a4s-network"
    backbone_agent_id: str = "backbone-router"
    backbone_agent_image: str = "a4s-personal-assistant:latest"
    backbone_agent_model_provider: ModelProvider = ModelProvider.GOOGLE
    backbone_agent_model_id: str = "gemini-3-flash-preview"

    # Agent runtime
    agent_idle_timeout: int = Field(default=300, description="Idle timeout in seconds")
    agent_reaper_interval: int = Field(default=30, description="Reaper check interval")

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # Agent registry
    registry_qdrant_collection: str = "agents"
    registry_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Skills registry
    skills_db_path: str = "skills.db"

    # Channels registry
    channel_db_path: str = "channels.db"

    # Memory - LLM
    memory_llm_provider: LLMProvider = LLMProvider.OPENAI
    memory_llm_model: str = "gpt-4o-mini"
    memory_llm_base_url: str | None = None

    # Memory - Embedding
    memory_embedding_provider: EmbeddingProvider = EmbeddingProvider.FASTEMBED
    memory_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    memory_embedding_dims: int = 384

    # Memory - Vector store
    memory_vector_store_provider: VectorStoreProvider = VectorStoreProvider.QDRANT
    memory_qdrant_collection: str = "memories"

    # Memory provider selection
    memory_provider: MemoryProvider = MemoryProvider.GRAPHITI

    # Graphiti - FalkorDB
    graphiti_falkordb_host: str = "localhost"
    graphiti_falkordb_port: int = 6379
    graphiti_falkordb_username: str | None = None
    graphiti_falkordb_password: SecretStr | None = None
    graphiti_falkordb_database: str = "graphiti"
    graphiti_default_group_id: str = "default"

    # API keys
    openai_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None


config = Config()
