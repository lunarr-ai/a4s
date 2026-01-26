class AgentRuntimeError(Exception):
    """Base exception for runtime errors."""


class AgentNotFoundError(AgentRuntimeError):
    """Agent container not found."""


class AgentSpawnError(AgentRuntimeError):
    """Failed to spawn agent."""


class ImageNotFoundError(AgentRuntimeError):
    """Docker image not found."""
