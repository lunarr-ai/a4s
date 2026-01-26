from abc import ABC, abstractmethod

from app.models import Agent


class AgentRegistry(ABC):
    """Registry for AI agents."""

    @abstractmethod
    async def register_agent(self, agent: Agent) -> None:
        """Register an agent."""

    @abstractmethod
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""

    @abstractmethod
    async def get_agent(self, agent_id: str) -> Agent:
        """Get an agent."""

    @abstractmethod
    async def list_agents(self) -> list[Agent]:
        """List all agents."""

    @abstractmethod
    async def search_agents(self, query: str, limit: int = 10) -> list[Agent]:
        """Search for agents."""
