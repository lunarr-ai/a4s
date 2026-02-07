import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPServerParams,
)

from mcp import StdioServerParameters
from src.config import LLMProvider, config

DEFAULT_INSTRUCTION = """\
You are a helpful AI assistant. You have access to tools that let you \
search for agents, delegate tasks, and manage memories.

Use your tools proactively when they can help answer the user's request. \
Search memories at the start of conversations to recall relevant context.

{custom_instruction}\
"""

_LITELLM_PROVIDER_PREFIX = {
    LLMProvider.OPENAI: "openai",
    LLMProvider.ANTHROPIC: "anthropic",
    LLMProvider.OPENROUTER: "openrouter",
}

AGENT_TOOLS = {
    "google_search": google_search,
    "linear_mcp_server": McpToolset(
        connection_params=StreamableHTTPServerParams(
            url="https://mcp.linear.app/mcp",
            headers={
                "Authorization": f"Bearer {os.getenv('LINEAR_API_KEY')}",
            },
        ),
        tool_name_prefix="linear_",
    ),
    "github_mcp_server": McpToolset(
        connection_params=StreamableHTTPServerParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={
                "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                "X-MCP-Toolsets": "repos,issues,pull_requests,users",
                "X-MCP-Readonly": "true",
            },
        ),
        tool_name_prefix="github_",
    ),
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

    mcp_kwargs = {}
    if config.agent_mcp_tool_filter:
        mcp_kwargs["tool_filter"] = config.agent_mcp_tool_filter.split(",")

    agent_tools = [
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python",
                    args=["-m", "a4s_mcp"],
                    env=mcp_env,
                ),
                timeout=180,
            ),
            tool_name_prefix="a4s_",
            **mcp_kwargs,
        )
    ]

    available_tools = config.agent_tools.split(",") if config.agent_tools else []

    for tool in available_tools:
        if tool not in AGENT_TOOLS:
            raise ValueError(f"Unknown tool specified: {tool}")
        agent_tools.append(AGENT_TOOLS[tool])

    instruction = DEFAULT_INSTRUCTION.format(
        custom_instruction=config.agent_instruction,
    )

    return LlmAgent(
        model=_create_model(),
        name=config.agent_name,
        instruction=instruction,
        tools=agent_tools,
    )
