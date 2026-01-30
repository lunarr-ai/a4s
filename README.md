# A4S

A4S is an orchestration system for AI agents.

- **Zero-code integration**: Any agent can join the A4S ecosystem without code or prompt modifications.
- **Intelligent routing**: Agents can discover and collaborate with other agents based on their capabilities.

## Usage

### Docker Compose (recommended)

```bash
docker compose -f compose.dev.yml up
```

## Development

Ensure you have the following tools installed:

- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
uv run pre-commit install
```
