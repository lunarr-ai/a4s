"""Cleanup TechFlow Solutions demo - stop and unregister all agents."""

import json
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REGISTERED_AGENTS_PATH = Path(__file__).parent.parent / "data/registered_agents.json"


def load_registered_agents() -> dict:
    """Load registered agents from file."""
    if not REGISTERED_AGENTS_PATH.exists():
        print(f"No registered agents file found at {REGISTERED_AGENTS_PATH}")
        return {}

    with Path.open(REGISTERED_AGENTS_PATH) as f:
        return json.load(f)


def stop_agent(client: httpx.Client, agent_id: str, agent_name: str) -> bool:
    """Stop an agent via API.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name for logging.

    Returns:
        True if stopped successfully, False otherwise.
    """
    try:
        response = client.post(f"{API_BASE_URL}/agents/{agent_id}/stop")
        response.raise_for_status()
        print(f"  ✓ Stopped: {agent_name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to stop {agent_name}: {e}")
        return False


def unregister_agent(client: httpx.Client, agent_id: str, agent_name: str) -> bool:
    """Unregister an agent via API.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name for logging.

    Returns:
        True if unregistered successfully, False otherwise.
    """
    try:
        response = client.delete(f"{API_BASE_URL}/agents/{agent_id}")
        response.raise_for_status()
        print(f"  ✓ Unregistered: {agent_name}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to unregister {agent_name}: {e}")
        return False


def main() -> None:
    """Stop and unregister all agents, remove registered_agents.json."""
    # Load registered agents
    registered_agents = load_registered_agents()

    if not registered_agents:
        print("No agents to cleanup.")
        return

    print(f"Cleaning up {len(registered_agents)} agents...")
    print()

    stop_count = 0
    unregister_count = 0

    with httpx.Client(timeout=30.0) as client:
        # Stop all agents
        print("Stopping agents...")
        for agent_id, agent_info in registered_agents.items():
            if stop_agent(client, agent_id, agent_info["name"]):
                stop_count += 1

        print()

        # Unregister all agents
        print("Unregistering agents...")
        for agent_id, agent_info in registered_agents.items():
            if unregister_agent(client, agent_id, agent_info["name"]):
                unregister_count += 1

    print()
    print(f"Stopped {stop_count}/{len(registered_agents)} agents")
    print(f"Unregistered {unregister_count}/{len(registered_agents)} agents")

    # Remove registered agents file
    if REGISTERED_AGENTS_PATH.exists():
        REGISTERED_AGENTS_PATH.unlink()
        print(f"\nRemoved {REGISTERED_AGENTS_PATH}")

    print()
    print("✓ Cleanup complete!")
    print()
    print("Note: Memories remain in FalkorDB/Qdrant. To fully reset:")
    print("  docker compose -f compose.dev.yml down -v")
    print("  docker compose -f compose.dev.yml up -d")


if __name__ == "__main__":
    main()
