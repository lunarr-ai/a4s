from abc import ABC, abstractmethod

from app.models import Agent, AgentStatus
from app.runtime.models import SpawnAgentRequest


class RuntimeManager(ABC):
    """Managing lifecycle of AI agent runtimes."""

    @abstractmethod
    def spawn_agent(self, request: SpawnAgentRequest) -> Agent:
        """Spawn a new agent runtime."""

    @abstractmethod
    def stop_agent(self, agent_id: str) -> Agent:
        """Stop an agent runtime."""

    @abstractmethod
    def list_agents(self) -> list[Agent]:
        """List all agent runtimes."""

    @abstractmethod
    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get the status of an agent runtime."""
