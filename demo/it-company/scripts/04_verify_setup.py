"""Verify TechFlow Solutions demo setup."""  # noqa: N999

import json
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REGISTERED_AGENTS_PATH = Path(__file__).parent / "registered_agents.json"


def load_registered_agents() -> dict:
    """Load registered agents from file."""
    with Path.open(REGISTERED_AGENTS_PATH) as f:
        return json.load(f)


def test_agent_search(client: httpx.Client) -> None:
    """Test agent semantic search."""
    print("Test 1: Agent Semantic Search")
    print("-" * 50)

    test_queries = [
        ("backend engineer", "Backend Team members"),
        ("payment", "Payment-related expertise"),
        ("design", "Design Team members"),
        ("devops kubernetes", "DevOps engineers"),
    ]

    for query, description in test_queries:
        try:
            response = client.get(f"{API_BASE_URL}/agents/search", params={"query": query, "limit": 5})
            response.raise_for_status()
            results = response.json()
            agents = results.get("agents", [])

            print(f"\n  Query: '{query}' ({description})")
            print(f"  Found {len(agents)} agents:")
            for agent in agents:
                print(f"    - {agent['name']} ({agent.get('description', 'N/A')[:60]}...)")

        except Exception as e:
            print(f"  ✗ Error searching for '{query}': {e}")

    print()


def test_memory_search_owner(client: httpx.Client, registered_agents: dict) -> None:
    """Test memory search by agent owner (sees private + public)."""
    print("Test 2: Memory Search by Owner")
    print("-" * 50)

    requester_id = "alice-chen"
    query = "chen"

    agent_id = None
    for a_id, info in registered_agents.items():
        if info["name"] == requester_id:
            agent_id = a_id
            break

    if not agent_id:
        print(f"  ✗ {requester_id} not found in registered agents")
        return

    try:
        payload = {"query": query, "agent_id": agent_id, "limit": 5}
        headers = {"X-Requester-Id": requester_id}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print(f"\n  Agent: {requester_id} (owner)")
        print(f"  Query: '{query}'")
        print(f"  Found {len(memories)} memories:")
        for i, memory in enumerate(memories, 1):
            print(f"   {i}. {memory['content']}")

        if len(memories) == 0:
            print("\n  ⚠ No memories found")

    except Exception as e:
        print(f"  ✗ Error searching memory of {requester_id}: {e}")

    print()


def test_cross_agent_memory_access(client: httpx.Client, registered_agents: dict) -> None:
    """Test cross-agent memory access (agent A reads agent B's public memories)."""
    print("Test 3: Cross-Agent Memory Access")
    print("-" * 50)

    requester_id = "maya-singh"
    target_agent = "alice-chen"
    query = "payment"

    target_agent_id = None
    for agent_id, info in registered_agents.items():
        if info["name"] == target_agent:
            target_agent_id = agent_id

    if not target_agent_id:
        print(f"  ✗ {target_agent} not found")
        return

    try:
        payload = {"query": query, "agent_id": target_agent_id, "limit": 5}
        headers = {"X-Requester-Id": requester_id}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print(f"\n  Requester: {requester_id}")
        print(f"  Target: {target_agent}")
        print(f"  Query: '{query}'")
        print(f"  Found {len(memories)} public memories:")
        for i, memory in enumerate(memories, 1):
            print(f"   {i}. {memory['content']}")

        if len(memories) == 0:
            print("\n  ⚠ No memories found")

    except Exception as e:
        print(f"  ✗ Error in cross-agent access: {e}")

    print()


def test_design_team_collaboration(client: httpx.Client, registered_agents: dict) -> None:
    """Test design team collaboration scenario."""
    print("Test 4: Design Team Collaboration Scenario")
    print("-" * 50)

    # Emily (Frontend) searches Olivia's (Design Lead) memories about checkout
    emily_id = None
    olivia_id = None

    for agent_id, info in registered_agents.items():
        if info["name"] == "emily-wang":
            emily_id = agent_id
        elif info["name"] == "olivia-taylor":
            olivia_id = agent_id

    if not emily_id or not olivia_id:
        print("  ✗ Emily Wang or Olivia Taylor not found")
        return

    try:
        payload = {"query": "checkout redesign user research", "agent_id": olivia_id, "limit": 3}
        headers = {"X-Requester-Id": "emily-wang"}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print("\n  Scenario: Emily (Frontend) needs checkout redesign requirements")
        print("  Searching: Olivia's (Design Lead) memories")
        print("  Query: 'checkout redesign user research'")
        print(f"  Found {len(memories)} memories:")
        for i, memory in enumerate(memories, 1):
            print(f"   {i}. {memory['content']}")

        if len(memories) > 0:
            print("\n  ✓ Design-Engineering collaboration scenario verified!")

    except Exception as e:
        print(f"  ✗ Error in design collaboration test: {e}")

    print()


def main() -> None:
    """Run all verification tests."""
    print("=" * 50)
    print("TechFlow Solutions Demo Verification")
    print("=" * 50)
    print()

    # Load registered agents
    try:
        registered_agents = load_registered_agents()
    except Exception as e:
        print(f"✗ Failed to load registered agents: {e}")
        return

    with httpx.Client(timeout=30.0) as client:
        # Run tests
        test_agent_search(client)
        test_memory_search_owner(client, registered_agents)
        test_cross_agent_memory_access(client, registered_agents)
        test_design_team_collaboration(client, registered_agents)

    print("=" * 50)
    print("Verification Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  - Run demo scenarios in demo/it-company/test_scenarios/")
    print("  - Interact with agents via their URLs (see registered_agents.json)")
    print("  - Monitor agents: docker ps | grep a4s-agent")


if __name__ == "__main__":
    main()
