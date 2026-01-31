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
            for agent in agents[:3]:
                print(f"    - {agent['name']} ({agent.get('description', 'N/A')[:60]}...)")

        except Exception as e:
            print(f"  ✗ Error searching for '{query}': {e}")

    print()


def test_memory_search_owner(client: httpx.Client, registered_agents: dict) -> None:
    """Test memory search by agent owner (sees private + public)."""
    print("Test 2: Memory Search by Owner")
    print("-" * 50)

    # Test Alice Chen's memories (as Alice)
    alice_id = None
    for agent_id, info in registered_agents.items():
        if info["name"] == "Alice Chen":
            alice_id = agent_id
            break

    if not alice_id:
        print("  ✗ Alice Chen not found in registered agents")
        return

    try:
        payload = {"query": "team performance", "agent_id": alice_id, "limit": 5}
        headers = {"X-Requester-Id": alice_id}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print("\n  Agent: Alice Chen (owner)")
        print("  Query: 'team performance'")
        print(f"  Found {len(memories)} memories:")
        for memory in memories[:3]:
            metadata = memory.get("metadata", {})
            visibility = "private" if "private" in metadata.get("group_id", "") else "public"
            print(f"    - [{visibility}] {metadata.get('name', 'N/A')[:50]} (score: {memory.get('score', 0):.2f})")

    except Exception as e:
        print(f"  ✗ Error searching Alice's memories: {e}")

    print()


def test_cross_agent_memory_access(client: httpx.Client, registered_agents: dict) -> None:
    """Test cross-agent memory access (agent A reads agent B's public memories)."""
    print("Test 3: Cross-Agent Memory Access")
    print("-" * 50)

    # Maya searches Bob's public memories about payment
    maya_id = None
    bob_id = None

    for agent_id, info in registered_agents.items():
        if info["name"] == "Maya Singh":
            maya_id = agent_id
        elif info["name"] == "Bob Martinez":
            bob_id = agent_id

    if not maya_id or not bob_id:
        print("  ✗ Maya Singh or Bob Martinez not found")
        return

    try:
        payload = {"query": "payment gateway architecture", "agent_id": bob_id, "limit": 5}
        headers = {"X-Requester-Id": maya_id}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print("\n  Requester: Maya Singh (Product Manager)")
        print("  Target: Bob Martinez (Backend Engineer)")
        print("  Query: 'payment gateway architecture'")
        print(f"  Found {len(memories)} public memories:")
        for memory in memories[:3]:
            metadata = memory.get("metadata", {})
            print(
                f"    - {metadata.get('knowledge_type', 'N/A')}: {metadata.get('name', 'N/A')[:50]} (score: {memory.get('score', 0):.2f})"
            )

        if len(memories) > 0:
            print("\n  ✓ Cross-agent memory access working!")
        else:
            print("\n  ⚠ No memories found - may need more time for Graphiti processing")

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
        if info["name"] == "Emily Wang":
            emily_id = agent_id
        elif info["name"] == "Olivia Taylor":
            olivia_id = agent_id

    if not emily_id or not olivia_id:
        print("  ✗ Emily Wang or Olivia Taylor not found")
        return

    try:
        payload = {"query": "checkout redesign user research", "agent_id": olivia_id, "limit": 3}
        headers = {"X-Requester-Id": emily_id}

        response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
        response.raise_for_status()
        memories = response.json()

        print("\n  Scenario: Emily (Frontend) needs checkout redesign requirements")
        print("  Searching: Olivia's (Design Lead) memories")
        print("  Query: 'checkout redesign user research'")
        print(f"  Found {len(memories)} memories:")
        for memory in memories:
            metadata = memory.get("metadata", {})
            print(f"    - {metadata.get('name', 'N/A')[:60]} (score: {memory.get('score', 0):.2f})")

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
