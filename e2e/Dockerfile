FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY api/ ./api/
COPY mcp/ ./mcp/
COPY e2e/ ./e2e/

RUN uv sync --frozen

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

EXPOSE 8000

CMD [".venv/bin/python", "-m", "hello_world_agent.server"]
