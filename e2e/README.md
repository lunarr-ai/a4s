# E2E Tests

End-to-end testing for A4S agent orchestration and A2A communication.

## Quick Start

```bash
docker compose -f compose.dev.yml up -d

# Run e2e test
./e2e/run.sh
```

## Options

```bash
./e2e/run.sh --skip-build    # Skip Docker image build
./e2e/run.sh --cleanup       # Stop and delete agent after test
./e2e/run.sh --help          # Show all options
```

## Environment Variables

```bash
API_URL=http://localhost:8000
AGENT_NAME=test_agent
MODEL_PROVIDER=google        # google, openai, anthropic, openrouter
MODEL_ID=gemini-2.0-flash
IMAGE_NAME=hello-world-agent
```

Example:

```bash
MODEL_PROVIDER=openai MODEL_ID=gpt-4o ./e2e/run.sh --cleanup
```
