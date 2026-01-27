# API Server

The A4S API server provides REST endpoints and an MCP server (mounted at `/mcp`) for AI agent orchestration.

## MCP Capabilities

| Type | Name | Description |
|------|------|-------------|
| Tool | `search_agents(query, limit=10)` | Search for agents by name/description |
| Tool | `search_skills(query, limit=10)` | Search for skills by name/description |
| Tool | `get_skills(names)` | Get metadata for specific skills by exact name |
| Resource | `skill://{name}/instructions` | Get skill instructions |
| Resource | `skill://{name}/file/{path}` | Get skill file content |
| Prompt | `activate_skill(skill_name)` | Generate instructions for using a skill |
| Prompt | `discover_skills(task_description, limit=5)` | Find and recommend skills for a task |
