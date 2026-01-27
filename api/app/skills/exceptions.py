class SkillRegistryError(Exception):
    """Base exception for skill registry errors."""


class SkillNotFoundError(SkillRegistryError):
    """Skill not found in registry."""


class SkillValidationError(SkillRegistryError):
    """Skill data validation failed."""


class SkillRegistryConnectionError(SkillRegistryError):
    """Failed to connect to registry backend."""
