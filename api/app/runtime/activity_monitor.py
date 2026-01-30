import time


class AgentActivityMonitor:
    """Tracks last activity timestamp per agent."""

    def __init__(self) -> None:
        self._activity: dict[str, float] = {}

    def record(self, agent_id: str) -> None:
        """Record activity for an agent.

        Args:
            agent_id: The agent ID to record activity for.
        """
        self._activity[agent_id] = time.monotonic()

    def get_idle_agents(self, threshold_seconds: int) -> list[str]:
        """Return agent IDs idle longer than threshold.

        Args:
            threshold_seconds: Number of seconds before an agent is considered idle.

        Returns:
            List of agent IDs that have been idle longer than the threshold.
        """
        now = time.monotonic()
        return [
            agent_id for agent_id, last_activity in self._activity.items() if now - last_activity > threshold_seconds
        ]

    def remove(self, agent_id: str) -> None:
        """Remove agent from tracking.

        Args:
            agent_id: The agent ID to remove from tracking.
        """
        self._activity.pop(agent_id, None)
