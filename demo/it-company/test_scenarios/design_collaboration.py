"""Design Team Collaboration Scenario.

Demonstrates how Emily (Frontend Engineer) gathers checkout redesign requirements
from Design team (Olivia, Paul, Quinn) and Product (Maya) using memory search.

This simulates async knowledge transfer without requiring meetings.
"""

import json
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REGISTERED_AGENTS_PATH = Path(__file__).parent.parent / "scripts" / "registered_agents.json"


def load_registered_agents() -> dict:
    """Load registered agents from file."""
    with Path.open(REGISTERED_AGENTS_PATH) as f:
        return json.load(f)


def search_memory(client: httpx.Client, requester_id: str, target_agent_id: str, query: str, limit: int = 3) -> list:
    """Search an agent's memories.

    Args:
        client: HTTP client.
        requester_id: ID of agent making the request.
        target_agent_id: ID of agent whose memories to search.
        query: Search query.
        limit: Maximum results.

    Returns:
        List of memory results.
    """
    payload = {"query": query, "agent_id": target_agent_id, "limit": limit}
    headers = {"X-Requester-Id": requester_id}

    response = client.post(f"{API_BASE_URL}/memories/search", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def print_memory_results(memories: list, indent: str = "    ") -> None:
    """Pretty print memory search results."""
    for i, memory in enumerate(memories, 1):
        metadata = memory.get("metadata", {})
        score = memory.get("score", 0)
        name = metadata.get("name", "N/A")
        knowledge_type = metadata.get("knowledge_type", "N/A")

        print(f"{indent}{i}. [{knowledge_type}] {name}")
        print(f"{indent}   Score: {score:.2f}")

        # Print snippet of content
        content = memory.get("content", "")
        snippet = content[:120] + "..." if len(content) > 120 else content
        print(f"{indent}   Content: {snippet}")
        print()


def main() -> None:  # noqa: C901, PLR0912, PLR0915
    """Run design collaboration scenario."""
    print("=" * 70)
    print("Design Team Collaboration Scenario")
    print("=" * 70)
    print()
    print("Story: Emily (Frontend Engineer) needs to implement checkout redesign.")
    print("       She searches Design and Product team memories for requirements.")
    print()

    # Load registered agents
    try:
        registered_agents = load_registered_agents()
    except Exception as e:
        print(f"✗ Failed to load registered agents: {e}")
        return

    # Find agent IDs
    emily_id = None
    olivia_id = None
    paul_id = None
    quinn_id = None
    maya_id = None

    for agent_id, info in registered_agents.items():
        if info["name"] == "Emily Wang":
            emily_id = agent_id
        elif info["name"] == "Olivia Taylor":
            olivia_id = agent_id
        elif info["name"] == "Paul Anderson":
            paul_id = agent_id
        elif info["name"] == "Quinn Roberts":
            quinn_id = agent_id
        elif info["name"] == "Maya Singh":
            maya_id = agent_id

    if not all([emily_id, olivia_id, paul_id, quinn_id, maya_id]):
        print("✗ Could not find all required agents")
        return

    with httpx.Client(timeout=30.0) as client:
        # Step 1: Emily searches Olivia's memories for user research findings
        print("-" * 70)
        print("Step 1: Emily searches Olivia's (Design Lead) memories")
        print("-" * 70)
        print("  Query: 'checkout redesign user research'")
        print("  Goal: Understand user pain points and design recommendations")
        print()

        try:
            memories = search_memory(client, emily_id, olivia_id, "checkout redesign user research", limit=3)
            print(f"  Found {len(memories)} memories:")
            print()
            print_memory_results(memories)

            if len(memories) > 0:
                print("  ✓ Emily learned:")
                print("    - 73% of users struggle with payment method selection")
                print("    - Recommendation: Simplify to 3-step checkout flow")
                print("    - Use progressive disclosure pattern")
                print()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()

        # Step 2: Emily searches Maya's memories for product priorities
        print("-" * 70)
        print("Step 2: Emily searches Maya's (Product Manager) memories")
        print("-" * 70)
        print("  Query: 'Q1 priorities checkout optimization'")
        print("  Goal: Confirm this is priority work and understand success metrics")
        print()

        try:
            memories = search_memory(client, emily_id, maya_id, "Q1 priorities checkout optimization", limit=3)
            print(f"  Found {len(memories)} memories:")
            print()
            print_memory_results(memories)

            if len(memories) > 0:
                print("  ✓ Emily learned:")
                print("    - Checkout optimization is Q1 top priority")
                print("    - Target: Reduce abandonment from 27% to <20%")
                print("    - Will use A/B testing before full rollout")
                print()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()

        # Step 3: Emily searches Paul's memories for UX requirements
        print("-" * 70)
        print("Step 3: Emily searches Paul's (UX Designer) memories")
        print("-" * 70)
        print("  Query: 'accessibility requirements WCAG checkout'")
        print("  Goal: Understand accessibility compliance needs")
        print()

        try:
            memories = search_memory(client, emily_id, paul_id, "accessibility requirements WCAG checkout", limit=3)
            print(f"  Found {len(memories)} memories:")
            print()
            print_memory_results(memories)

            if len(memories) > 0:
                print("  ✓ Emily learned:")
                print("    - Must meet WCAG 2.1 AA compliance")
                print("    - Needs keyboard navigation and screen reader support")
                print("    - Color contrast minimum 4.5:1")
                print()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()

        # Step 4: Emily searches Quinn's memories for UI components
        print("-" * 70)
        print("Step 4: Emily searches Quinn's (UI Designer) memories")
        print("-" * 70)
        print("  Query: 'checkout UI components design system'")
        print("  Goal: Find which components to use from design system")
        print()

        try:
            memories = search_memory(client, emily_id, quinn_id, "checkout UI components design system", limit=3)
            print(f"  Found {len(memories)} memories:")
            print()
            print_memory_results(memories)

            if len(memories) > 0:
                print("  ✓ Emily learned:")
                print("    - Use: Card, Button, FormField, PaymentMethodSelector components")
                print("    - All components support dark mode and responsive breakpoints")
                print("    - Design tokens: primary #007AFF, 8px spacing grid, Inter font")
                print()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()

    # Summary
    print("=" * 70)
    print("Scenario Complete!")
    print("=" * 70)
    print()
    print("Emily successfully gathered all checkout redesign requirements:")
    print()
    print("  From Olivia (Design Lead):")
    print("    ✓ User research findings and design recommendations")
    print()
    print("  From Maya (Product Manager):")
    print("    ✓ Business priorities and success metrics")
    print()
    print("  From Paul (UX Designer):")
    print("    ✓ Accessibility requirements and UX patterns")
    print()
    print("  From Quinn (UI Designer):")
    print("    ✓ Component library and design system specs")
    print()
    print("Next steps for Emily:")
    print("  - Implement 3-step checkout flow with progressive disclosure")
    print("  - Use @techflow/ui component library (Card, Button, FormField)")
    print("  - Ensure WCAG 2.1 AA compliance with keyboard navigation")
    print("  - Set up A/B testing for gradual rollout")
    print()
    print("Key benefit: All requirements gathered asynchronously via memory search")
    print("             without scheduling 4 separate meetings!")
    print()


if __name__ == "__main__":
    main()
