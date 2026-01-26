from abc import ABC, abstractmethod

from app.skills.models import Skill, SkillFile


class SkillsRegistry(ABC):
    """Registry for agentskills."""

    @abstractmethod
    async def register_skill(self, skill: Skill, files: list[SkillFile] | None = None) -> Skill:
        """Register a skill in the registry.

        Args:
            skill: The skill to register.
            files: Optional list of files associated with the skill.

        Returns:
            The registered skill with generated ID.
        """

    @abstractmethod
    async def unregister_skill(self, skill_id: int) -> None:
        """Unregister a skill from the registry.

        Args:
            skill_id: The ID of the skill to unregister.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """

    @abstractmethod
    async def get_skill(self, skill_id: int) -> Skill:
        """Get a skill by ID.

        Args:
            skill_id: The ID of the skill to retrieve.

        Returns:
            The skill with the given ID.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """

    @abstractmethod
    async def get_skill_files(self, skill_id: int) -> list[SkillFile]:
        """Get all files associated with a skill.

        Args:
            skill_id: The ID of the skill.

        Returns:
            List of files associated with the skill.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """

    @abstractmethod
    async def list_skills(self) -> list[Skill]:
        """List all registered skills.

        Returns:
            List of all skills in the registry.
        """

    @abstractmethod
    async def search_skills(self, query: str, limit: int = 10) -> list[Skill]:
        """Search for skills using semantic search.

        Args:
            query: The search query text.
            limit: Maximum number of results to return.

        Returns:
            List of skills matching the query, ordered by relevance.
        """

    @abstractmethod
    async def close(self) -> None:
        """Close the registry and release resources."""
