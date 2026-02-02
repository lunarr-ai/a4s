class AgentRegistryError(Exception):
    """Base exception for registry errors."""


class AgentNotRegisteredError(AgentRegistryError):
    """Agent not found in registry."""


class AgentRegistryConnectionError(AgentRegistryError):
    """Failed to connect to registry backend."""


class ChannelRegistryError(Exception):
    """Base exception for channel registry errors."""


class ChannelNotFoundError(ChannelRegistryError):
    """Channel not found in registry."""


class ChannelRegistryConnectionError(ChannelRegistryError):
    """Failed to connect to channel registry backend."""
