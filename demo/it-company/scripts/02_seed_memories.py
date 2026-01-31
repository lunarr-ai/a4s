"""Seed memories for all TechFlow Solutions agents via A4S API."""  # noqa: N999

import json
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
SEED_DATA_DIR = Path(__file__).parent.parent / "seed_data"
REGISTERED_AGENTS_PATH = Path(__file__).parent / "registered_agents.json"


def load_registered_agents() -> dict:
    """Load registered agents from file."""
    with Path.open(REGISTERED_AGENTS_PATH) as f:
        return json.load(f)


def load_agent_seed_data(agent_id: str) -> dict | None:
    """Load seed data for a specific agent.

    Args:
        agent_id: Agent identifier.

    Returns:
        Seed data dict or None if file doesn't exist.
    """
    # Convert agent_id to filename (e.g., "alice-chen" -> "alice_chen.json")
    filename = agent_id.replace("-", "_") + ".json"
    seed_file = SEED_DATA_DIR / filename

    if not seed_file.exists():
        return None

    with Path.open(seed_file) as f:
        return json.load(f)


def add_memory(
    client: httpx.Client,
    agent_id: str,
    requester_id: str,
    memory_data: dict,
    visibility: str,
) -> dict:
    """Add a single memory via API.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        requester_id: ID of requester (for access control).
        memory_data: Memory data with name, episode_body, knowledge_type.
        visibility: "private" or "public".

    Returns:
        API response.
    """
    # Format memory as episode message
    episode_body = memory_data.get("episode_body", "")

    # Prepare metadata with name and knowledge_type
    metadata = {
        "name": memory_data.get("name"),
        "knowledge_type": memory_data.get("knowledge_type"),
    }

    payload = {
        "messages": episode_body,
        "agent_id": agent_id,
        "visibility": visibility,
        "metadata": metadata,
    }

    headers = {"X-Requester-Id": requester_id}

    response = client.post(f"{API_BASE_URL}/memories", json=payload, headers=headers)
    response.raise_for_status()

    return response.json()


def seed_agent_memories(client: httpx.Client, agent_id: str, agent_name: str) -> int:
    """Seed all memories for a single agent.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name.

    Returns:
        Number of memories seeded.
    """
    seed_data = load_agent_seed_data(agent_name)
    if not seed_data:
        print(f"  ⊘ No seed data found for {agent_name}")
        return 0

    memory_count = 0

    # Seed private memories (requester is the agent itself)
    private_memories = seed_data.get("private_memories", [])
    for memory in private_memories:
        try:
            add_memory(
                client,
                agent_id=agent_id,
                requester_id=agent_name,
                memory_data=memory,
                visibility="private",
            )
            memory_count += 1
        except Exception as e:
            print(f"  ✗ Failed to add private memory '{memory.get('name')}': {e}")

    # Seed public memories (requester is the agent itself)
    public_memories = seed_data.get("public_memories", [])
    for memory in public_memories:
        try:
            add_memory(
                client,
                agent_id=agent_id,
                requester_id=agent_name,
                memory_data=memory,
                visibility="public",
            )
            memory_count += 1
        except Exception as e:
            print(f"  ✗ Failed to add public memory '{memory.get('name')}': {e}")

    print(f"  ✓ {agent_name}: {memory_count} memories ({len(private_memories)} private, {len(public_memories)} public)")
    return memory_count


def main() -> None:
    """Seed memories for all registered agents."""
    # Load registered agents
    registered_agents = load_registered_agents()

    print(f"Seeding memories for {len(registered_agents)} agents...")
    print()

    total_memories = 0

    with httpx.Client(timeout=30.0) as client:
        for agent_id, agent_info in registered_agents.items():
            try:
                count = seed_agent_memories(client, agent_id, agent_info["name"])
                total_memories += count
            except Exception as e:
                print(f"  ✗ Error seeding memories for {agent_info['name']}: {e}")
                continue

    print()
    print(f"Successfully seeded {total_memories} total memories")
    print()
    print("⏳ IMPORTANT: Memories are processed asynchronously by Graphiti.")
    print("   Wait 2-3 minutes before starting agents to allow processing to complete.")
    print("   You can verify in FalkorDB:")
    print("   docker exec -it a4s-memory falkordb-cli")
    print('   GRAPH.QUERY graphiti "MATCH (n) RETURN count(n)"')


if __name__ == "__main__":
    main()
