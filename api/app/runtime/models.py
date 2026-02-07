from pydantic import BaseModel, Field

from app.models import AgentModel


class SpawnAgentRequest(BaseModel):
    agent_id: str = Field(description="The unique identifier of the agent.")
    name: str = Field(description="The name of the agent.")
    image: str = Field(description="The docker image of the agent.")
    version: str = Field(description="The version of the agent.", default="1.0.0")
    port: int = Field(description="The port of the agent.", default=8000)
    model: AgentModel = Field(description="The model of the agent.")
    description: str = Field(description="The description of the agent for human.")
    instruction: str = Field(description="The additional instruction of the agent.")
    tools: list[str] = Field(description="The enabled tools of the agent.")
    mcp_tool_filter: str = Field(default="", description="Comma-separated MCP tool names to expose.")
