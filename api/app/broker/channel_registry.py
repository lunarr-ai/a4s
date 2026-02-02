from abc import ABC, abstractmethod

from app.models import Channel


class ChannelRegistry(ABC):
    """Abstract interface for channel registry."""

    @abstractmethod
    async def create_channel(self, channel: Channel) -> None:
        """Create a new channel.

        Args:
            channel: The channel to create.

        Raises:
            ChannelRegistryConnectionError: If the operation fails.
        """
        ...

    @abstractmethod
    async def delete_channel(self, channel_id: str) -> None:
        """Delete a channel.

        Args:
            channel_id: The ID of the channel to delete.

        Raises:
            ChannelNotFoundError: If the channel does not exist.
        """
        ...

    @abstractmethod
    async def get_channel(self, channel_id: str) -> Channel:
        """Get a channel by ID.

        Args:
            channel_id: The ID of the channel to retrieve.

        Returns:
            The channel with the given ID.

        Raises:
            ChannelNotFoundError: If the channel does not exist.
        """
        ...

    @abstractmethod
    async def list_channels(self, offset: int = 0, limit: int = 50) -> list[Channel]:
        """List channels with pagination.

        Args:
            offset: Number of channels to skip.
            limit: Maximum number of channels to return.

        Returns:
            List of channels starting from offset.
        """
        ...

    @abstractmethod
    async def update_channel(self, channel_id: str, updates: dict) -> Channel:
        """Update a channel.

        Args:
            channel_id: The ID of the channel to update.
            updates: Dictionary of fields to update.

        Returns:
            The updated channel.

        Raises:
            ChannelNotFoundError: If the channel does not exist.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the registry connection."""
        ...
