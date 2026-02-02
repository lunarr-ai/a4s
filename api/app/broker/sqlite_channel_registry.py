from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from datetime import UTC, datetime

import aiosqlite

from app.broker.channel_registry import ChannelRegistry
from app.broker.exceptions import ChannelNotFoundError, ChannelRegistryConnectionError
from app.models import Channel

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "channels.db"


def _init_schema_sync(connection: sqlite3.Connection) -> None:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS channel (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            agent_ids TEXT NOT NULL DEFAULT '[]',
            owner_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)


async def _init_schema(db_path: str) -> None:
    def init_sync() -> None:
        conn = sqlite3.connect(db_path)
        try:
            _init_schema_sync(conn)
            conn.commit()
        finally:
            conn.close()

    await asyncio.to_thread(init_sync)


class SqliteChannelRegistry(ChannelRegistry):
    """Channel registry using SQLite."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    @classmethod
    async def create(cls, db_path: str = DEFAULT_DB_PATH) -> SqliteChannelRegistry:
        """Create a new SqliteChannelRegistry instance.

        Args:
            db_path: Path to the SQLite database file.

        Returns:
            Initialized registry instance.

        Raises:
            ChannelRegistryConnectionError: If database connection fails.
        """
        try:
            await _init_schema(db_path)
            db = await aiosqlite.connect(db_path)
            db.row_factory = aiosqlite.Row
            logger.info("Connected to channels database at %s", db_path)
            return cls(db)
        except Exception as e:
            logger.exception("Failed to initialize channel registry: %s", e)
            raise ChannelRegistryConnectionError(f"Failed to initialize channel registry: {e}") from e

    def _channel_to_row(self, channel: Channel) -> dict:
        return {
            "id": channel.id,
            "name": channel.name,
            "description": channel.description,
            "agent_ids": json.dumps(channel.agent_ids),
            "owner_id": channel.owner_id,
            "created_at": channel.created_at.isoformat(),
            "updated_at": channel.updated_at.isoformat(),
        }

    def _row_to_channel(self, row: aiosqlite.Row) -> Channel:
        return Channel(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            agent_ids=json.loads(row["agent_ids"]) if row["agent_ids"] else [],
            owner_id=row["owner_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    async def create_channel(self, channel: Channel) -> None:
        row = self._channel_to_row(channel)
        try:
            await self._db.execute(
                """
                INSERT INTO channel (id, name, description, agent_ids, owner_id, created_at, updated_at)
                VALUES (:id, :name, :description, :agent_ids, :owner_id, :created_at, :updated_at)
                """,
                row,
            )
            await self._db.commit()
            logger.info("Created channel %s", channel.id)
        except Exception as e:
            logger.exception("Failed to create channel: %s", e)
            raise ChannelRegistryConnectionError(f"Failed to create channel: {e}") from e

    async def get_channel(self, channel_id: str) -> Channel:
        async with self._db.execute("SELECT * FROM channel WHERE id = ?", (channel_id,)) as cursor:
            row = await cursor.fetchone()
        if not row:
            logger.error("Channel %s not found", channel_id)
            raise ChannelNotFoundError(f"Channel {channel_id} not found")
        return self._row_to_channel(row)

    async def list_channels(self, offset: int = 0, limit: int = 50) -> list[Channel]:
        async with self._db.execute(
            "SELECT * FROM channel ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
        return [self._row_to_channel(row) for row in rows]

    async def update_channel(self, channel_id: str, updates: dict) -> Channel:
        channel = await self.get_channel(channel_id)

        if "name" in updates:
            channel.name = updates["name"]
        if "description" in updates:
            channel.description = updates["description"]
        if "agent_ids" in updates:
            channel.agent_ids = updates["agent_ids"]
        if "add_agent_ids" in updates:
            for agent_id in updates["add_agent_ids"]:
                if agent_id not in channel.agent_ids:
                    channel.agent_ids.append(agent_id)
        if "remove_agent_ids" in updates:
            channel.agent_ids = [aid for aid in channel.agent_ids if aid not in updates["remove_agent_ids"]]

        channel.updated_at = datetime.now(UTC)

        await self._db.execute(
            """
            UPDATE channel SET name = ?, description = ?, agent_ids = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                channel.name,
                channel.description,
                json.dumps(channel.agent_ids),
                channel.updated_at.isoformat(),
                channel_id,
            ),
        )
        await self._db.commit()
        logger.info("Updated channel %s", channel_id)
        return channel

    async def delete_channel(self, channel_id: str) -> None:
        await self.get_channel(channel_id)
        await self._db.execute("DELETE FROM channel WHERE id = ?", (channel_id,))
        await self._db.commit()
        logger.info("Deleted channel %s", channel_id)

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            logger.info("Closed channel database connection")
