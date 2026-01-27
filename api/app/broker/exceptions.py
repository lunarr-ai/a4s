class AgentRegistryError(Exception):
    """Base exception for registry errors."""


class AgentNotRegisteredError(AgentRegistryError):
    """Agent not found in registry."""


class AgentRegistryConnectionError(AgentRegistryError):
    """Failed to connect to registry backend."""
