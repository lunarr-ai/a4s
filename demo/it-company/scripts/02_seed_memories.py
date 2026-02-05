"""Seed memories for all TechFlow Solutions agents via A4S API."""  # noqa: N999

import json
import time
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
    max_retries: int = 5,
) -> dict:
    """Add a single memory via API with retry logic.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        requester_id: ID of requester (for access control).
        memory_data: Memory data with name, episode_body, knowledge_type.
        visibility: "private" or "public".
        max_retries: Maximum number of retry attempts.

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
        "metadata": metadata,
    }

    headers = {"X-Requester-Id": requester_id}

    last_exception = None
    for _ in range(max_retries):
        try:
            response = client.post(f"{API_BASE_URL}/memories", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            last_exception = e
            time.sleep(10)

    raise last_exception if last_exception else RuntimeError("Unexpected error in add_memory")


def seed_agent_memories(client: httpx.Client, agent_id: str, agent_name: str) -> tuple[int, int]:
    """Seed all memories for a single agent.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name.

    Returns:
        Tuple of (successful_count, failed_count).
    """
    seed_data = load_agent_seed_data(agent_name)
    if not seed_data:
        print(f"  ⊘ No seed data found for {agent_name}")
        return 0, 0

    success_count = 0

    memories = seed_data.get("memories", [])
    for memory in memories:
        try:
            add_memory(
                client,
                agent_id=agent_id,
                requester_id=agent_name,
                memory_data=memory,
            )
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed to add private memory '{memory.get('name')}': {e}")
        finally:
            # Add delay to allow LLM processing
            time.sleep(10)

    print(f"{success_count}/{len(memories)} memories added.")
    return success_count, len(memories) - success_count


def main() -> None:
    """Seed memories for all registered agents."""
    # Load registered agents
    registered_agents = load_registered_agents()

    print(f"Seeding memories for {len(registered_agents)} agents...")
    print()

    total_success = 0
    total_failed = 0

    with httpx.Client(timeout=60.0) as client:
        for agent_id, agent_info in registered_agents.items():
            try:
                print("=" * 60)
                print(f"Seeding memories for agent '{agent_info['name']}' (ID: {agent_id})...")
                print()
                success_count, failed_count = seed_agent_memories(client, agent_id, agent_info["name"])
                print()
                print(f"Finished seeding for {agent_info['name']}: {success_count} succeeded, {failed_count} failed.")
                print("=" * 60)
                total_success += success_count
                total_failed += failed_count
            except Exception as e:
                print(f"  ✗ Error seeding memories for {agent_info['name']}: {e}")
                continue

    print()
    print(f"Success: {total_success}, Failed: {total_failed}, Total: {total_success + total_failed} memories")
    print()
    print("⏳ IMPORTANT: Memories are processed asynchronously by Graphiti.")
    print("   Wait 3-5 minutes before starting agents to allow processing to complete.")
    print("   You can verify in FalkorDB:")
    print("   docker exec a4s-a4s-memory-1 redis-cli GRAPH.QUERY graphiti 'MATCH (n) RETURN count(n)'")
    print()
    print("   Monitor processing in API logs:")
    print("   docker logs -f a4s-a4s-api-1 | grep 'Error processing\\|Successfully'")


if __name__ == "__main__":
    main()
