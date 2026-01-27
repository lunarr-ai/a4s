from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from datetime import datetime

import aiosqlite
import sqlite_vec
from fastembed import TextEmbedding
from sqlalchemy import create_engine
from sqlmodel import SQLModel

from app.models import EmbeddingModel
from app.skills.exceptions import (
    SkillNotFoundError,
    SkillRegistryConnectionError,
    SkillValidationError,
)
from app.skills.models import Skill, SkillFile
from app.skills.registry import SkillsRegistry

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "skills.db"
EMBEDDING_DIMENSION = 384


def _load_sqlite_vec(connection: sqlite3.Connection) -> None:
    connection.enable_load_extension(True)
    connection.load_extension(sqlite_vec.loadable_path())
    connection.enable_load_extension(False)


async def _enable_vector_extension(db: aiosqlite.Connection) -> None:
    await db.enable_load_extension(True)
    await db.load_extension(sqlite_vec.loadable_path())
    await db.enable_load_extension(False)


def _init_schema_sync(connection: sqlite3.Connection) -> None:
    _load_sqlite_vec(connection)
    engine = create_engine("sqlite://", creator=lambda: connection)
    SQLModel.metadata.create_all(engine)
    connection.execute(f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS skill_embeddings USING vec0(
            skill_id INTEGER PRIMARY KEY,
            embedding FLOAT[{EMBEDDING_DIMENSION}]
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


class SqliteSkillsRegistry(SkillsRegistry):
    """Skills registry using SQLite with sqlite-vec for vector search."""

    def __init__(
        self,
        db: aiosqlite.Connection,
        embedding_client: TextEmbedding,
    ) -> None:
        self._db = db
        self._embedding_client = embedding_client

    @classmethod
    async def create(
        cls,
        db_path: str = DEFAULT_DB_PATH,
        embedding_model: EmbeddingModel | None = None,
    ) -> SqliteSkillsRegistry:
        """Create a new SqliteSkillsRegistry instance.

        Args:
            db_path: Path to the SQLite database file.
            embedding_model: Embedding model configuration.

        Returns:
            Initialized registry instance.

        Raises:
            SkillValidationError: If embedding model dimension doesn't match.
            SkillRegistryConnectionError: If database connection fails.
        """
        embedding_model = embedding_model or EmbeddingModel.create()
        if embedding_model.dimension != EMBEDDING_DIMENSION:
            raise SkillValidationError(
                f"Embedding model dimension {embedding_model.dimension} does not match "
                f"required dimension {EMBEDDING_DIMENSION}"
            )

        try:
            await _init_schema(db_path)

            db = await aiosqlite.connect(db_path)
            db.row_factory = aiosqlite.Row
            await _enable_vector_extension(db)

            embedding_client = await asyncio.to_thread(TextEmbedding, model_name=embedding_model.model_id)

            logger.info("Connected to skills database at %s", db_path)
            return cls(db, embedding_client)
        except Exception as e:
            logger.exception("Failed to initialize skills registry: %s", e)
            raise SkillRegistryConnectionError(f"Failed to initialize skills registry: {e}") from e

    async def _embed(self, text: str) -> list[float]:
        def embed_sync() -> list[float]:
            embeddings = list(self._embedding_client.embed([text]))
            return embeddings[0].tolist()

        return await asyncio.to_thread(embed_sync)

    def _skill_to_row(self, skill: Skill) -> dict:
        return {
            "name": skill.name,
            "description": skill.description,
            "body": skill.body,
            "license": skill.license,
            "compatibility": skill.compatibility,
            "tags": json.dumps(skill.tags),
            "allowed_tools": json.dumps(skill.allowed_tools),
            "created_at": skill.created_at.isoformat(),
            "updated_at": skill.updated_at.isoformat(),
        }

    def _row_to_skill(self, row: aiosqlite.Row) -> Skill:
        return Skill(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            body=row["body"],
            license=row["license"],
            compatibility=row["compatibility"],
            tags=json.loads(row["tags"]) if row["tags"] else {},
            allowed_tools=json.loads(row["allowed_tools"]) if row["allowed_tools"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_skill_file(self, row: aiosqlite.Row) -> SkillFile:
        return SkillFile(
            id=row["id"],
            skill_id=row["skill_id"],
            path=row["path"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    async def register_skill(self, skill: Skill, files: list[SkillFile] | None = None) -> Skill:
        """Register a skill in the registry.

        Args:
            skill: The skill to register.
            files: Optional list of files associated with the skill.

        Returns:
            The registered skill with generated ID.

        Raises:
            SkillValidationError: If a skill with the same name already exists.
            SkillRegistryConnectionError: If the operation fails.
        """
        row = self._skill_to_row(skill)
        try:
            cursor = await self._db.execute(
                """
                INSERT INTO skill (name, description, body, license, compatibility, tags, allowed_tools, created_at, updated_at)
                VALUES (:name, :description, :body, :license, :compatibility, :tags, :allowed_tools, :created_at, :updated_at)
                """,
                row,
            )
            skill_id = cursor.lastrowid

            document = f"{skill.name} {skill.description}"
            embedding = await self._embed(document)
            await self._db.execute(
                "INSERT INTO skill_embeddings (skill_id, embedding) VALUES (?, ?)",
                (skill_id, sqlite_vec.serialize_float32(embedding)),
            )

            if files:
                for file in files:
                    await self._db.execute(
                        """
                        INSERT INTO skillfile (skill_id, path, content, created_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (skill_id, file.path, file.content, file.created_at.isoformat()),
                    )

            await self._db.commit()
            logger.info("Registered skill %s", skill_id)

            skill.id = skill_id
            return skill
        except sqlite3.IntegrityError as e:
            logger.warning("Skill validation failed: %s", e)
            raise SkillValidationError(f"Skill with name '{skill.name}' already exists") from e
        except Exception as e:
            logger.exception("Failed to register skill: %s", e)
            raise SkillRegistryConnectionError(f"Failed to register skill: {e}") from e

    async def unregister_skill(self, skill_id: int) -> None:
        """Unregister a skill from the registry.

        Args:
            skill_id: The ID of the skill to unregister.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """
        await self.get_skill(skill_id)
        await self._db.execute("DELETE FROM skillfile WHERE skill_id = ?", (skill_id,))
        await self._db.execute("DELETE FROM skill_embeddings WHERE skill_id = ?", (skill_id,))
        await self._db.execute("DELETE FROM skill WHERE id = ?", (skill_id,))
        await self._db.commit()
        logger.info("Unregistered skill %s", skill_id)

    async def get_skill(self, skill_id: int) -> Skill:
        """Get a skill by ID.

        Args:
            skill_id: The ID of the skill to retrieve.

        Returns:
            The skill with the given ID.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """
        async with self._db.execute("SELECT * FROM skill WHERE id = ?", (skill_id,)) as cursor:
            row = await cursor.fetchone()
        if not row:
            logger.error("Skill %s not found", skill_id)
            raise SkillNotFoundError(f"Skill {skill_id} not found")
        return self._row_to_skill(row)

    async def get_skill_files(self, skill_id: int) -> list[SkillFile]:
        """Get all files associated with a skill.

        Args:
            skill_id: The ID of the skill.

        Returns:
            List of files associated with the skill.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """
        await self.get_skill(skill_id)
        async with self._db.execute("SELECT * FROM skillfile WHERE skill_id = ?", (skill_id,)) as cursor:
            rows = await cursor.fetchall()
        return [self._row_to_skill_file(row) for row in rows]

    async def list_skills(self, offset: int = 0, limit: int = 50) -> list[Skill]:
        """List skills with pagination.

        Args:
            offset: Number of skills to skip.
            limit: Maximum number of skills to return.

        Returns:
            List of skills starting from offset.
        """
        async with self._db.execute(
            "SELECT * FROM skill ORDER BY name LIMIT ? OFFSET ?",
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
        return [self._row_to_skill(row) for row in rows]

    async def search_skills(self, query: str, limit: int = 10) -> list[Skill]:
        """Search for skills using semantic search.

        Args:
            query: The search query text.
            limit: Maximum number of results to return.

        Returns:
            List of skills matching the query, ordered by relevance.
        """
        embedding = await self._embed(query)
        async with self._db.execute(
            """
            SELECT s.* FROM skill s
            JOIN skill_embeddings e ON s.id = e.skill_id
            WHERE e.embedding MATCH ?
            AND k = ?
            ORDER BY distance
            """,
            (sqlite_vec.serialize_float32(embedding), limit),
        ) as cursor:
            rows = await cursor.fetchall()
        return [self._row_to_skill(row) for row in rows]

    async def get_skill_by_name(self, name: str) -> Skill:
        """Get a skill by name.

        Args:
            name: The unique name of the skill.

        Returns:
            The skill with the given name.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """
        async with self._db.execute("SELECT * FROM skill WHERE name = ?", (name,)) as cursor:
            row = await cursor.fetchone()
        if not row:
            logger.error("Skill with name %s not found", name)
            raise SkillNotFoundError(f"Skill with name '{name}' not found")
        return self._row_to_skill(row)

    async def get_skill_file_by_path(self, skill_id: int, path: str) -> SkillFile:
        """Get a specific file associated with a skill by path.

        Args:
            skill_id: The ID of the skill.
            path: The file path within the skill.

        Returns:
            The file at the given path.

        Raises:
            SkillNotFoundError: If the skill or file does not exist.
        """
        await self.get_skill(skill_id)
        async with self._db.execute(
            "SELECT * FROM skillfile WHERE skill_id = ? AND path = ?",
            (skill_id, path),
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            logger.error("File %s not found for skill %s", path, skill_id)
            raise SkillNotFoundError(f"File '{path}' not found for skill {skill_id}")
        return self._row_to_skill_file(row)

    async def close(self) -> None:
        """Close the database connection."""
        if self._db:
            await self._db.close()
            logger.info("Closed database connection")
