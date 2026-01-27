from typing import Any

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """A stored memory unit."""

    id: str = Field(description="Unique identifier for the memory.")
    content: str = Field(description="The content of the memory.")
    score: float | None = Field(default=None, description="Relevance score from search.")
    metadata: dict[str, Any] | None = Field(default=None, description="Associated metadata.")


class CreateMemoryRequest(BaseModel):
    """Request to create a new memory."""

    messages: str | list[dict[str, str]] = Field(
        description="Message content or conversation to store.",
        examples=[
            "I prefer dark mode for all applications.",
            [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}],
        ],
    )
    user_id: str | None = Field(default=None, description="User identifier for scoping.")
    agent_id: str | None = Field(default=None, description="Agent identifier for scoping.")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata.")


class SearchMemoryRequest(BaseModel):
    """Request to search memories."""

    query: str = Field(description="Search query text.")
    user_id: str | None = Field(default=None, description="Filter by user.")
    agent_id: str | None = Field(default=None, description="Filter by agent.")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return.")
    metadata_filter: dict[str, Any] | None = Field(
        default=None,
        description="Filter by metadata key-value pairs.",
    )
    options: dict[str, Any] | None = Field(
        default=None,
        description="Provider-specific search options.",
    )


class UpdateMemoryRequest(BaseModel):
    """Request to update an existing memory."""

    content: str = Field(description="New content for the memory.")
