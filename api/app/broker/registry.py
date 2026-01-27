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
    async def list_agents(self, offset: int = 0, limit: int = 50) -> list[Agent]:
        """List agents with pagination.

        Args:
            offset: Number of agents to skip.
            limit: Maximum number of agents to return.

        Returns:
            List of agents starting from offset.
        """

    @abstractmethod
    async def search_agents(self, query: str, limit: int = 10) -> list[Agent]:
        """Search for agents."""

    @abstractmethod
    async def close(self) -> None:
        """Close the registry and release resources."""
