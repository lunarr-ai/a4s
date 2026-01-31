# TechFlow Solutions Demo - Setup Guide

This guide will walk you through setting up the TechFlow Solutions multi-agent demo step-by-step.

## Prerequisites

### 1. Build the Personal Assistant Docker Image

```bash
cd /Users/minsuk/work_dir/a4s
docker build -t a4s-personal-assistant:latest -f agents/personal-assistant/Dockerfile .
```

Expected output: `Successfully tagged a4s-personal-assistant:latest`

### 2. Start A4S Infrastructure

```bash
docker compose -f compose.dev.yml up -d
```

Wait ~30 seconds for all services to start.

### 3. Verify Infrastructure Health

```bash
# Check API health
curl http://localhost:8000/livez
# Expected: {"status": "ok"}

# Check Qdrant (vector database)
curl http://localhost:6333/readyz
# Expected: {"status": "ok"}

# Check FalkorDB (knowledge graph)
docker ps | grep a4s-memory
# Expected: Container running
```

If any check fails, wait 30 more seconds and retry. Services may take time to initialize.

## Demo Setup (15-20 minutes)

Navigate to the demo scripts directory:

```bash
cd /Users/minsuk/work_dir/a4s/demo/it-company/scripts
```

### Step 1: Register Agents (~2-3 minutes)

This registers all 20 TechFlow employees as agents in the A4S registry.

```bash
uv run python 01_register_agents.py
```

Expected output:
```
Registering 20 agents for TechFlow Solutions...

✓ Registered: Alice Chen (ID: alice-chen)
✓ Registered: Bob Martinez (ID: bob-martinez)
...

Successfully registered 20/20 agents
Saved agent IDs to: .../registered_agents.json
```

**Troubleshooting**:
- If you see connection errors, verify the API is running: `curl http://localhost:8000/livez`
- If agents already exist, run cleanup first: `uv run python cleanup.py`

### Step 2: Seed Memories (~5-10 minutes)

This adds ~200 memories (personal experiences, technical knowledge, project details) to each agent's memory.

```bash
uv run python 02_seed_memories.py
```

Expected output:
```
Seeding memories for 20 agents...

  ✓ Alice Chen: 9 memories (3 private, 6 public)
  ✓ Bob Martinez: 9 memories (2 private, 7 public)
  ...

Successfully seeded 185 total memories

⏳ IMPORTANT: Memories are processed asynchronously by Graphiti.
   Wait 2-3 minutes before starting agents to allow processing to complete.
```

**CRITICAL**: Do NOT skip the wait time. Memories are processed asynchronously and need time to be indexed.

### Step 3: Wait for Memory Processing (3 minutes)

```bash
# Wait 3 minutes for Graphiti to process all memories
sleep 180
```

**Optional**: Verify memories in FalkorDB:
```bash
docker exec -it a4s-memory falkordb-cli

# In the FalkorDB CLI:
GRAPH.QUERY graphiti "MATCH (n) RETURN count(n)"
# Expected: At least 185+ nodes

# Exit the CLI
exit
```

### Step 4: Start Agents (~5-10 minutes)

This starts all 20 agent containers. Agents are started in batches of 5 to avoid overwhelming Docker.

```bash
uv run python 03_start_agents.py
```

Expected output:
```
Starting 20 agents in batches of 5...

Batch 1/4:
  ⟳ Starting Alice Chen... ✓ Running
  ⟳ Starting Bob Martinez... ✓ Running
  ...

Results: 20 started successfully, 0 failed

✓ Agents are now running and ready for interactions!
```

**Troubleshooting**:
- If agents fail to start, check Docker resources (need ~4GB RAM)
- View logs: `docker logs a4s-agent-<agent-id>`
- Agents may take 10-30 seconds each to start

### Step 5: Verify Setup (~1 minute)

Run automated tests to verify everything is working:

```bash
uv run python 04_verify_setup.py
```

Expected output:
```
==================================================
TechFlow Solutions Demo Verification
==================================================

Test 1: Agent Semantic Search
--------------------------------------------------

  Query: 'backend engineer' (Backend Team members)
  Found 4 agents:
    - Bob Martinez (Senior Backend Engineer...)
    - Alice Chen (Engineering Manager for Backend Team...)
    - Carol Kim (Associate Backend Engineer...)

Test 2: Memory Search by Owner
--------------------------------------------------

  Agent: Alice Chen (owner)
  Query: 'team performance'
  Found 3 memories:
    - [private] Team Performance Review Q1 2026 (score: 0.85)
    - [public] Backend Tech Stack (score: 0.72)
    ...

Test 3: Cross-Agent Memory Access
--------------------------------------------------

  Requester: Maya Singh (Product Manager)
  Target: Bob Martinez (Backend Engineer)
  Query: 'payment gateway architecture'
  Found 5 public memories:
    - fact: Payment Gateway Integration Experience (score: 0.89)
    - fact: Kafka Event Schema Design (score: 0.81)
    ...

  ✓ Cross-agent memory access working!

Test 4: Design Team Collaboration Scenario
--------------------------------------------------

  Scenario: Emily (Frontend) needs checkout redesign requirements
  Searching: Olivia's (Design Lead) memories
  Query: 'checkout redesign user research'
  Found 2 memories:
    - User Research Findings - Checkout Flow (score: 0.92)
    ...

  ✓ Design-Engineering collaboration scenario verified!

==================================================
Verification Complete!
==================================================
```

If all tests pass, you're ready to run demo scenarios!

## Run Demo Scenarios

### Interactive Scenario: Design Team Collaboration

This demonstrates how Emily (Frontend Engineer) gathers requirements from the Design and Product teams:

```bash
cd /Users/minsuk/work_dir/a4s/demo/it-company/test_scenarios
uv run python design_collaboration.py
```

This scenario shows:
- Emily searching Olivia's memories for user research findings
- Emily searching Maya's memories for product priorities
- Emily searching Paul's memories for accessibility requirements
- Emily searching Quinn's memories for UI component specs

All gathered asynchronously via memory search without meetings!

### Manual Testing with curl

You can also test manually using curl:

```bash
# Search for backend engineers
curl "http://localhost:8000/api/v1/agents/search?query=backend+engineer&limit=5"

# Maya searches Bob's payment-related memories
curl -X POST http://localhost:8000/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -H "X-Requester-Id: maya-singh" \
  -d '{
    "query": "payment service architecture deployment",
    "agent_id": "bob-martinez",
    "limit": 5
  }'
```

## Monitoring

### View Running Agents

```bash
# List all agents
curl http://localhost:8000/api/v1/agents

# Check specific agent status
curl http://localhost:8000/api/v1/agents/alice-chen/status

# View Docker containers
docker ps | grep a4s-agent
# Should show 20 containers
```

### View Agent Logs

```bash
# View logs for specific agent
docker logs a4s-agent-alice-chen

# Follow logs in real-time
docker logs -f a4s-agent-bob-martinez
```

## Cleanup

When you're done with the demo:

```bash
cd /Users/minsuk/work_dir/a4s/demo/it-company/scripts
uv run python cleanup.py
```

This will:
- Stop all 20 agents
- Unregister agents from the registry
- Remove registered_agents.json

**Note**: Memories remain in FalkorDB/Qdrant. To fully reset:

```bash
docker compose -f compose.dev.yml down -v
docker compose -f compose.dev.yml up -d
```

## Common Issues

### "Connection refused" errors
- **Cause**: A4S infrastructure not running
- **Fix**: `docker compose -f compose.dev.yml up -d`

### "Agent already exists" errors
- **Cause**: Leftover agents from previous run
- **Fix**: Run `uv run python cleanup.py` first

### "No memories found" in searches
- **Cause**: Didn't wait for Graphiti processing
- **Fix**: Wait 2-3 minutes after seeding, verify in FalkorDB

### Agents fail to start / timeout
- **Cause**: Insufficient Docker resources
- **Fix**: Increase Docker memory to 4GB+, or reduce BATCH_SIZE in script

### "Docker image not found"
- **Cause**: Personal assistant image not built
- **Fix**: `docker build -t a4s-personal-assistant:latest -f agents/personal-assistant/Dockerfile .`

## Next Steps

See [README.md](README.md) for:
- Full company structure
- Memory architecture details
- Additional demo scenarios
- Technical details

Enjoy exploring TechFlow Solutions! 🚀
