from enum import Enum

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings


class LLMProvider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class Config(BaseSettings):
    agent_name: str = "hello_world"
    agent_id: str = ""
    agent_tools: str = ""
    agent_mcp_tool_filter: str = ""

    agent_model_provider: LLMProvider = LLMProvider.GOOGLE
    agent_model_id: str = "gemini-3-flash-preview"
    agent_instruction: str = "You are a helpful assistant."
    a4s_api_url: str = "http://host.docker.internal:8000"
    agent_host: str = "localhost"

    google_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    openrouter_api_key: SecretStr | None = None

    @field_validator("agent_name")
    @classmethod
    def sanitize_agent_name(cls, v: str) -> str:
        return v.replace("-", "_")


config = Config()
