from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/template-agents", tags=["template-agents"])


class TemplateAgent(BaseModel):
    """Represents a pre-configured agent template."""

    template_id: str = Field(description="Unique identifier for the template.")
    image_name: str = Field(description="Docker image name for the agent.")
    version: str = Field(description="Template version.")
    description: str = Field(description="Description of the agent's capabilities.")
    available_tools: list[str] = Field(description="All available tools that can be enabled.")
    tags: list[str] = Field(description="Tags for categorizing and filtering templates.")


class TemplateAgentListResponse(BaseModel):
    """Response for listing agent templates."""

    templates: list[TemplateAgent]
    total: int


def _get_hardcoded_templates() -> list[TemplateAgent]:
    return [
        TemplateAgent(
            template_id="personal-assistant",
            image_name="a4s-personal-assistant:latest",
            version="1.0.0",
            description="Personal AI companion that learns from conversations and builds a knowledge graph of people, projects, preferences, and context.",
            available_tools=["google_search", "linear_mcp_server", "github_mcp_server"],
            tags=["personal-assistant", "memory", "knowledge-graph", "learning"],
        )
    ]


@router.get("")
async def list_template_agents() -> TemplateAgentListResponse:
    """List available agent templates.

    Returns:
        List of agent templates with metadata.
    """
    templates = _get_hardcoded_templates()

    return TemplateAgentListResponse(
        templates=templates,
        total=len(templates),
    )
