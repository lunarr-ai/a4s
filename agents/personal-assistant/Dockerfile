FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY api/ ./api/
COPY mcp/ ./mcp/
COPY e2e/ ./e2e/
COPY agents/personal-assistant ./agents/personal-assistant

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

EXPOSE 8000

CMD ["python", "-m", "agents.personal-assistant.src.server"]
