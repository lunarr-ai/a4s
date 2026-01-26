from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


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


class Agent(BaseModel):
    """Metadata for an AI agent runtime."""

    id: UUID = Field(description="The unique identifier of the agent.")
    name: str = Field(description="The name of the agent.")
    description: str = Field(description="The description of the agent.")
    version: str = Field(description="The version of the agent.")
    url: str = Field(description="The URL of the agent.")
    port: int = Field(description="The port of the agent.")
    status: AgentStatus = Field(description="The status of the agent.", default=AgentStatus.PENDING)
    created_at: datetime = Field(description="The timestamp of the agent creation.", default_factory=datetime.now)
