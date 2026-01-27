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
    async def list_skills(self, offset: int = 0, limit: int = 50) -> list[Skill]:
        """List skills with pagination.

        Args:
            offset: Number of skills to skip.
            limit: Maximum number of skills to return.

        Returns:
            List of skills starting from offset.
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
    async def get_skill_by_name(self, name: str) -> Skill:
        """Get a skill by name.

        Args:
            name: The unique name of the skill.

        Returns:
            The skill with the given name.

        Raises:
            SkillNotFoundError: If the skill does not exist.
        """

    @abstractmethod
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

    @abstractmethod
    async def close(self) -> None:
        """Close the registry and release resources."""
