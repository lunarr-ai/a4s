from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

MODEL_ID_TO_DIMENSION = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
}


class EmbeddingModel(BaseModel):
    model_id: str = Field(
        description="The model id of the embedding model.", default="sentence-transformers/all-MiniLM-L6-v2"
    )
    dimension: int = Field(description="The dimension of the embedding model.", default=384)

    @classmethod
    def create(cls, model_id: str | None = None) -> EmbeddingModel:
        model_id = model_id or DEFAULT_EMBEDDING_MODEL
        dimension = MODEL_ID_TO_DIMENSION.get(model_id)
        if dimension is None:
            raise ValueError(f"Unknown embedding model id: {model_id}")

        return cls(model_id=model_id, dimension=dimension)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"


class AgentModel(BaseModel):
    provider: ModelProvider = Field(description="The provider of the agent model.", default=ModelProvider.GOOGLE)
    model_id: str = Field(description="The model id of the agent model.", default="gemini-3-flash-preview")


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class AgentMode(str, Enum):
    SERVERLESS = "serverless"
    PERMANENT = "permanent"


class SpawnConfig(BaseModel):
    """Configuration for spawning an agent container."""

    image: str = Field(description="Docker image to use for the agent.")
    model: AgentModel = Field(description="Model configuration for the agent.")
    instruction: str = Field(default="", description="Instruction for the agent.")
    tools: list[str] = Field(default_factory=list, description="Enabled tools for the agent.")
    mcp_tool_filter: str = Field(default="", description="Comma-separated MCP tool names to expose.")


# Removed owner_id field from Agent model to simplify ownership management.
# The agent itself is its owner in this design.
class Agent(BaseModel):
    """Metadata for an AI agent runtime."""

    id: str = Field(description="The unique identifier of the agent.")
    name: str = Field(description="The name of the agent.")
    description: str = Field(description="The description of the agent.")
    version: str = Field(description="The version of the agent.")
    url: str = Field(description="The URL of the agent.")
    port: int = Field(description="The port of the agent.")
    status: AgentStatus = Field(description="The status of the agent.", default=AgentStatus.PENDING)
    created_at: datetime = Field(description="The timestamp of the agent creation.", default_factory=datetime.now)
    mode: AgentMode = Field(default=AgentMode.SERVERLESS, description="Runtime mode of the agent.")
    spawn_config: SpawnConfig | None = Field(default=None, description="Configuration for spawning agent containers.")


class Channel(BaseModel):
    """Metadata for a channel containing agents."""

    id: str = Field(description="The unique identifier of the channel.")
    name: str = Field(description="The name of the channel.")
    description: str = Field(description="The description of the channel's purpose.")
    agent_ids: list[str] = Field(default_factory=list, description="List of agent IDs in this channel.")
    owner_id: str = Field(description="The ID of the channel's owner.")
    created_at: datetime = Field(description="Timestamp of creation.", default_factory=datetime.now)
    updated_at: datetime = Field(description="Timestamp of last update.", default_factory=datetime.now)
