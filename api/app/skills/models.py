import json
import re
from datetime import datetime

from pydantic import field_validator
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Skill(SQLModel, table=True):
    """Skill definition following the agentskills specification."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    body: str = Field(default="")
    license: str | None = Field(default=None)
    compatibility: str | None = Field(default=None)
    tags: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON), serialization_alias="metadata")
    allowed_tools: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not 1 <= len(v) <= 64:
            raise ValueError("name must be 1-64 characters")
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("name must be lowercase alphanumeric with hyphens")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not 1 <= len(v) <= 1024:
            raise ValueError("description must be 1-1024 characters")
        return v

    @field_validator("compatibility")
    @classmethod
    def validate_compatibility(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 500:
            raise ValueError("compatibility must be at most 500 characters")
        return v

    @field_validator("tags", "allowed_tools", mode="before")
    @classmethod
    def parse_json_field(cls, v: dict | list | str) -> dict | list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class SkillFile(SQLModel, table=True):
    """File associated with a skill."""

    id: int | None = Field(default=None, primary_key=True)
    skill_id: int = Field(foreign_key="skill.id")
    path: str
    content: bytes
    created_at: datetime = Field(default_factory=datetime.now)
