# TechFlow Solutions - IT Company Multi-Agent Demo

This demo showcases A4S (Agent-to-Agent Semantics) with ~20 personal-assistant agents representing employees at "TechFlow Solutions", an imaginary IT company. Each agent has pre-seeded personas and memories stored in FalkorDB, enabling realistic cross-team collaboration scenarios.

## Company Structure

**TechFlow Solutions** has 20 employees across 3 departments:

### Engineering Department (12 agents)

- **Backend Team**: Alice Chen (Manager), Bob Martinez (Senior), Carol Kim (Associate), David Patel (Associate)
- **Frontend Team**: Emily Wang (Senior), Frank Johnson (Associate), Grace Liu (Associate)
- **DevOps Team**: Henry Brooks (Lead), Isabel Gomez (Senior), James Park (Associate)
- **QA Team**: Kate Thompson (Lead), Luis Rodriguez (Associate)

### Product & Design Department (5 agents)

- **Product**: Maya Singh (PM), Nathan Lee (Product Designer)
- **Design**: Olivia Taylor (Lead), Paul Anderson (UX), Quinn Roberts (UI)

### Marketing Department (3 agents)

- Rachel Green (Manager), Sarah Miller (Content), Tom Wilson (Social Media)

## Quick Start

### Prerequisites

```bash
# Deploy the server from root directory
make setup-dev
make dev-up
```

### Setup Demo (15-20 minutes)

```bash
cd demo/it-company/scripts

# 1. Register all 20 agents
uv run python 01_register_agents.py

# 2. Seed memories
uv run python 02_seed_memories.py

# 3. Wait for async Graphiti processing (IMPORTANT!)
sleep 180  # 3 minutes

# 4. Start agents
uv run python 03_start_agents.py

# 5. Verify setup
uv run python 04_verify_setup.py
```

### Cleanup

```bash
cd demo/it-company/scripts
uv run python cleanup.py
```

To fully reset (including memories):

```bash
docker compose -f compose.dev.yml down -v
docker compose -f compose.dev.yml up -d
```

## Memory Structure

Each agent has memories using these knowledge types:

- **entity**: People, teams, projects (e.g., "Alice Chen is Backend Team Manager")
- **fact**: Stable truths (e.g., "Team uses Python/FastAPI")
- **definition**: Technical terms (e.g., "API Gateway is...")
- **episode**: Events with timestamps (e.g., "Fixed bug on Jan 15, 2026")
- **preference**: How someone works (e.g., "Prefers code reviews within 24h")
- **pattern**: Observed behaviors (e.g., "Does deep work 9-12 AM")

## Agent Discovery

Search for agents by expertise:

```bash
# Find backend engineers
curl "http://localhost:8000/api/v1/agents/search?query=backend+engineer&limit=5"

# Find people working on payment systems
curl "http://localhost:8000/api/v1/agents/search?query=payment+systems&limit=5"

# Find design team members
curl "http://localhost:8000/api/v1/agents/search?query=design+UX&limit=5"
```

## Monitoring

### Check agent status

```bash
# List all agents
curl http://localhost:8000/api/v1/agents

# Get specific agent status
curl http://localhost:8000/api/v1/agents/alice-chen/status

# View running containers
docker ps | grep a4s-agent
```

### Verify memories in FalkorDB

```bash
# Access FalkorDB CLI
docker exec -it a4s-memory redis-cli

# Count total nodes
GRAPH.QUERY {graph_name} "MATCH (n) RETURN count(n)"

# View entity nodes
GRAPH.QUERY {graph_name} "MATCH (n:Entity) RETURN n.name LIMIT 10"

# Find memories about payment
GRAPH.QUERY {graph_name} "MATCH (n) WHERE n.name CONTAINS 'payment' RETURN n.name, n.type LIMIT 10"
```
