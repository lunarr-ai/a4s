import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

from mcp import StdioServerParameters
from placeholder_agent.config import LLMProvider, config

AGENT_INSTRUCTION = """You are {agent_name}, a collaborative AI agent.

{custom_instruction}
"""

_LITELLM_PROVIDER_PREFIX = {
    LLMProvider.OPENAI: "openai",
    LLMProvider.ANTHROPIC: "anthropic",
    LLMProvider.OPENROUTER: "openrouter",
}


def _setup_api_keys() -> None:
    if config.google_api_key:
        os.environ["GEMINI_API_KEY"] = config.google_api_key.get_secret_value()
    if config.openai_api_key:
        os.environ["OPENAI_API_KEY"] = config.openai_api_key.get_secret_value()
    if config.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_api_key.get_secret_value()
    if config.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = config.openrouter_api_key.get_secret_value()


def _create_model() -> str | LiteLlm:
    if config.agent_model_provider == LLMProvider.GOOGLE:
        return config.agent_model_id

    _setup_api_keys()
    prefix = _LITELLM_PROVIDER_PREFIX[config.agent_model_provider]
    return LiteLlm(model=f"{prefix}/{config.agent_model_id}")


def create_agent() -> LlmAgent:
    mcp_env = {"API_BASE_URL": config.a4s_api_url}
    if config.agent_id:
        mcp_env["REQUESTER_ID"] = config.agent_id
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="python",
                args=["-m", "a4s_mcp"],
                env=mcp_env,
            ),
            timeout=180,
        ),
        tool_filter=["search_agents", "send_a2a_message"],
    )

    instruction = AGENT_INSTRUCTION.format(
        agent_name=config.agent_name,
        custom_instruction=config.agent_instruction,
    )

    return LlmAgent(
        model=_create_model(),
        name=config.agent_name,
        instruction=instruction,
        tools=[mcp_toolset],
    )
