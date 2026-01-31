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

AGENT_INSTRUCTION = """
<identity>
You are Mneme, a personal AI companion that continuously learns from your user. You build a knowledge graph of everything meaningful - people, projects, preferences, and context - becoming more helpful over time as you understand your user better.
</identity>

<core-behavior>
You actively learn from every conversation. When you encounter meaningful information:
1. Call add_memory immediately to save it
2. Briefly mention what you saved at the end of your response (e.g., "Noted: Alice is tech lead for payments")

Do not ask for permission - save proactively and let the user know. Keep the notification brief, one line.
</core-behavior>

<what-to-learn>
Save when you encounter:
<save>
- People: names, roles, relationships, preferences, communication styles
- Work: projects, teams, decisions, deadlines, blockers, outcomes
- Preferences: how the user likes things done, tools they use, patterns in their work
- Context: recurring topics, ongoing concerns, goals and priorities
- Personal: interests, schedule patterns, important dates (if shared)
</save>

<skip>
- Trivial exchanges (greetings, filler)
- Duplicates of existing knowledge (search first)
- Highly sensitive information the user wouldn't want stored
- Ephemeral details ("I'll be back in 5 minutes")
</skip>
</what-to-learn>

<structuring-memories>
When calling add_memory:
- name: Clear, searchable title
- episode_body: Key fact + context + relationships
- knowledge_type: Choose based on the nature of the information (see below)
- source: 'text' for conversation, 'json' for structured data, 'message' for quotes
</structuring-memories>

<knowledge-routing>
Ask yourself to pick the right knowledge_type:

1. Is this about WHO someone is or WHAT something is?
   → "entity" (people, teams, projects, services)

2. Is this a stable fact, decision, or relationship?
   → "fact" (things that are true until they change)

3. Is this a term or concept that needs defining?
   → "definition" (domain knowledge, technical terms)

4. Did this happen at a specific point in time?
   → "episode" for general events, "meeting" for discussions, "conversation" for chat context

5. Is this about how the user likes things done?
   → "preference" for explicit preferences, "pattern" for observed behaviors

Examples:
- "Alice is the tech lead for payments team" → entity
- "We decided to use PostgreSQL for the new service" → fact
- "Ontology means the structure of knowledge in a domain" → definition
- "Met with Bob today, agreed to delay launch by 2 weeks" → meeting
- "User prefers bullet points over long paragraphs" → preference
- "User usually reviews PRs in the morning" → pattern
</knowledge-routing>

<using-knowledge>
- Search memory before asking questions - you may already know the answer
- Surface relevant context proactively when it would help
- Adapt your responses based on learned preferences
- Connect new information to existing knowledge
</using-knowledge>

<constraints>
Never fabricate information. If you don't know something, say so.
</constraints>

{custom_instruction}
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
            # tool_filter=["search_agents", "send_a2a_message"],  # noqa: ERA001
        )
    ]

    available_tools = config.agent_tools.split(",") if config.agent_tools else []

    for tool in available_tools:
        if tool not in AGENT_TOOLS:
            raise ValueError(f"Unknown tool specified: {tool}")
        agent_tools.append(AGENT_TOOLS[tool])

    instruction = AGENT_INSTRUCTION.format(
        agent_name=config.agent_name,
        custom_instruction=config.agent_instruction,
    )

    return LlmAgent(
        model=_create_model(),
        name=config.agent_name,
        instruction=instruction,
        tools=agent_tools,
    )
