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

1. **Docker image built**:
   ```bash
   cd /Users/minsuk/work_dir/a4s
   docker build -t a4s-personal-assistant:latest -f agents/personal-assistant/Dockerfile .
   ```

2. **A4S infrastructure running**:
   ```bash
   docker compose -f compose.dev.yml up -d
   ```

3. **Verify infrastructure**:
   ```bash
   # API health
   curl http://localhost:8000/livez

   # Qdrant health
   curl http://localhost:6333/readyz

   # FalkorDB health
   docker ps | grep a4s-memory
   ```

### Setup Demo (15-20 minutes)

```bash
cd demo/it-company/scripts

# 1. Register all 20 agents (~2-3 min)
uv run python 01_register_agents.py

# 2. Seed memories (~5-10 min for ~200 memories)
uv run python 02_seed_memories.py

# 3. Wait for async Graphiti processing (IMPORTANT!)
sleep 180  # 3 minutes

# 4. Start agents (~5-10 min for 20 agents)
uv run python 03_start_agents.py

# 5. Verify setup (~1 min)
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

### Memory Visibility

- **Private**: Performance reviews, personal work patterns, learning goals (owner-only access)
- **Public**: Role info, team structure, project details, technical decisions (readable by all agents)

## Demo Scenarios

### Scenario 1: Cross-Team Query
**Story**: Maya (Product Manager) needs payment project status.

**Test**:
```bash
# Maya searches Bob's (Backend Engineer) public memories
curl -X POST http://localhost:8000/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -H "X-Requester-Id: maya-singh" \
  -d '{
    "query": "payment service architecture",
    "agent_id": "bob-martinez",
    "limit": 5
  }'
```

**Expected**: Maya sees Bob's public memories about payment gateway integration, tech stack, deployment requirements.

### Scenario 2: Manager Context
**Story**: Alice (Engineering Manager) reviews team information.

**Test**:
```bash
# Alice searches her own memories (sees private + public)
curl -X POST http://localhost:8000/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -H "X-Requester-Id: alice-chen" \
  -d '{
    "query": "team performance",
    "agent_id": "alice-chen",
    "limit": 5
  }'
```

**Expected**: Alice sees both private performance notes and public project memories.

### Scenario 3: DevOps Coordination
**Story**: Henry (DevOps Lead) needs deployment info for payment service.

**Test**:
```bash
# Henry searches Bob's public memories
curl -X POST http://localhost:8000/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -H "X-Requester-Id: henry-brooks" \
  -d '{
    "query": "payment service deployment requirements",
    "agent_id": "bob-martinez",
    "limit": 5
  }'
```

**Expected**: Henry sees deployment specs: environment variables, resource limits, health checks.

### Scenario 4: Design Team Collaboration
**Story**: Frontend team needs checkout redesign requirements from Design team.

**Interaction Flow**:

1. **Emily (Frontend) searches Olivia's (Design Lead) memories for checkout redesign**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/memories/search \
     -H "Content-Type: application/json" \
     -H "X-Requester-Id: emily-wang" \
     -d '{
       "query": "checkout redesign user research",
       "agent_id": "olivia-taylor",
       "limit": 3
     }'
   ```
   **Finds**: User research showing 73% struggle with payment selection, recommendation for 3-step flow

2. **Emily searches Maya's (PM) memories for priorities**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/memories/search \
     -H "Content-Type: application/json" \
     -H "X-Requester-Id: emily-wang" \
     -d '{
       "query": "Q1 priorities checkout",
       "agent_id": "maya-singh",
       "limit": 3
     }'
   ```
   **Finds**: Checkout optimization is Q1 top priority, target <20% abandonment rate

3. **Emily searches Paul's (UX) memories for accessibility requirements**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/memories/search \
     -H "Content-Type: application/json" \
     -H "X-Requester-Id: emily-wang" \
     -d '{
       "query": "accessibility requirements WCAG",
       "agent_id": "paul-anderson",
       "limit": 3
     }'
   ```
   **Finds**: WCAG 2.1 AA compliance needs, keyboard navigation, screen reader support

4. **Emily searches Quinn's (UI) memories for component specs**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/memories/search \
     -H "Content-Type: application/json" \
     -H "X-Requester-Id: emily-wang" \
     -d '{
       "query": "checkout UI components design system",
       "agent_id": "quinn-roberts",
       "limit": 3
     }'
   ```
   **Finds**: Component library details, design tokens, responsive breakpoints

**Result**: Emily has complete context to implement checkout redesign with proper requirements, UX patterns, and UI specs - all gathered asynchronously via memory search without meetings!

**Demonstrates**:
- Cross-department collaboration (Design → Engineering → Product)
- Public memory sharing enables async knowledge transfer
- Multiple agents contributing different expertise to one project
- Semantic search across different knowledge types

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
docker exec -it a4s-memory falkordb-cli

# Count total nodes
GRAPH.QUERY graphiti "MATCH (n) RETURN count(n)"

# View entity nodes
GRAPH.QUERY graphiti "MATCH (n:Entity) RETURN n.name LIMIT 10"

# Find memories about payment
GRAPH.QUERY graphiti "MATCH (n) WHERE n.name CONTAINS 'payment' RETURN n.name, n.type LIMIT 10"
```

## File Structure

```
demo/it-company/
├── README.md                           # This file
├── company_structure.json              # Agent definitions with spawn configs
├── seed_data/                          # Individual memory files (20 agents)
│   ├── alice_chen.json
│   ├── bob_martinez.json
│   └── ... (18 more)
├── scripts/
│   ├── 01_register_agents.py          # Register all agents via API
│   ├── 02_seed_memories.py            # Seed memories via HTTP API
│   ├── 03_start_agents.py             # Start agent containers
│   ├── 04_verify_setup.py             # Test interactions
│   ├── cleanup.py                      # Cleanup demo
│   └── registered_agents.json          # Generated agent IDs (after step 1)
└── test_scenarios/                     # (Future) Interactive demo scripts
```

## Key Concepts Demonstrated

### 1. Agent-to-Agent Memory Access
- Agents can search each other's public memories
- Private memories remain owner-only
- Enables async knowledge sharing without direct communication

### 2. Semantic Search
- Find agents by expertise keywords
- Search memories by natural language queries
- Ranked results based on relevance scores

### 3. Knowledge Organization
- Structured memory types (entity, fact, definition, episode, preference, pattern)
- Metadata for categorization and filtering
- Temporal context with timestamps

### 4. Realistic Organizational Context
- Department and team hierarchies
- Role-based expertise and responsibilities
- Cross-functional collaboration scenarios

## Troubleshooting

### Agents fail to start
- Check Docker resources (20 agents need ~4GB RAM)
- View logs: `docker logs a4s-agent-<agent-id>`
- Reduce batch size in `03_start_agents.py`

### No memories found in searches
- Wait 2-3 minutes after seeding for Graphiti processing
- Verify in FalkorDB: `docker exec -it a4s-memory falkordb-cli`
- Check API logs: `docker logs a4s-api`

### Memory API returns 403 Forbidden
- Verify `X-Requester-Id` header is set
- Check requester has permission (owner for private, anyone for public)

### Agent search returns no results
- Verify agents are registered: `curl http://localhost:8000/api/v1/agents`
- Check Qdrant is running: `curl http://localhost:6333/readyz`
- Descriptions are indexed - use keywords from agent descriptions

## Technical Details

- **Model**: Google Gemini 2.0 Flash (fast, cost-effective)
- **Memory Backend**: FalkorDB (knowledge graph) + Qdrant (vector search)
- **Runtime Mode**: Serverless (agents auto-start on request, auto-stop when idle)
- **Memory Count**: ~200 total (~10 per agent)
- **Setup Time**: ~15-20 minutes
- **Resource Usage**: ~4GB RAM for 20 agents

## Next Steps

1. **Build interactive scenarios**: Create Python scripts in `test_scenarios/` that demonstrate multi-agent interactions
2. **Add more agents**: Expand to other departments (Sales, Support, Finance)
3. **Implement workflows**: Create task delegation and collaboration flows
4. **Add tools**: Integrate with Jira, GitHub, Slack for real work
5. **Monitor metrics**: Track memory access patterns, search relevance, collaboration effectiveness

## Credits

This demo was created for A4S (Agent-to-Agent Semantics) to showcase:
- Multi-agent orchestration
- Memory sharing with access control
- Semantic agent and memory discovery
- Realistic organizational scenarios

Built with: A4S, FalkorDB, Qdrant, FastAPI, Docker
