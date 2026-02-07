"""Start all registered TechFlow Solutions agents."""  # noqa: N999

import json
import time
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REGISTERED_AGENTS_PATH = Path(__file__).parent.parent / "data/registered_agents.json"
BATCH_SIZE = 5  # Start agents in batches to avoid overwhelming Docker
POLL_INTERVAL = 2  # Seconds between status checks
MAX_WAIT_TIME = 120  # Maximum seconds to wait for agent to start


def load_registered_agents() -> dict:
    """Load registered agents from file."""
    with Path.open(REGISTERED_AGENTS_PATH) as f:
        return json.load(f)


def start_agent(client: httpx.Client, agent_id: str) -> dict:
    """Start an agent via API.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.

    Returns:
        Start response with status.
    """
    response = client.post(f"{API_BASE_URL}/agents/{agent_id}/start")
    response.raise_for_status()
    return response.json()


def get_agent_status(client: httpx.Client, agent_id: str) -> str:
    """Get current status of an agent.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.

    Returns:
        Status string (e.g., "running", "pending", "stopped").
    """
    response = client.get(f"{API_BASE_URL}/agents/{agent_id}/status")
    response.raise_for_status()
    return response.json()["status"]


def wait_for_agent_running(client: httpx.Client, agent_id: str) -> bool:
    """Wait for agent to reach running status.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name for logging.

    Returns:
        True if agent started successfully, False if timeout.
    """
    elapsed = 0
    while elapsed < MAX_WAIT_TIME:
        try:
            status = get_agent_status(client, agent_id)
            if status == "running":
                return True
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
        except Exception:
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            continue

    return False


def start_agent_with_wait(client: httpx.Client, agent_id: str, agent_name: str) -> bool:
    """Start an agent and wait for it to be running.

    Args:
        client: HTTP client.
        agent_id: Agent identifier.
        agent_name: Agent display name for logging.

    Returns:
        True if started successfully, False otherwise.
    """
    try:
        # Start the agent
        start_agent(client, agent_id)
        print(f"  ⟳ Starting {agent_name}...", end=" ", flush=True)

        # Wait for running status
        if wait_for_agent_running(client, agent_id):
            print("✓ Running")
            return True
        print("✗ Timeout")
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main() -> None:
    """Start all registered agents in batches."""
    # Load registered agents
    registered_agents = load_registered_agents()
    agent_list = list(registered_agents.items())

    print(f"Starting {len(agent_list)} agents in batches of {BATCH_SIZE}...")
    print()

    success_count = 0
    fail_count = 0

    with httpx.Client(timeout=60.0) as client:
        # Process agents in batches
        for i in range(0, len(agent_list), BATCH_SIZE):
            batch = agent_list[i : i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(agent_list) + BATCH_SIZE - 1) // BATCH_SIZE

            print(f"Batch {batch_num}/{total_batches}:")

            for agent_id, agent_info in batch:
                if start_agent_with_wait(client, agent_id, agent_info["name"]):
                    success_count += 1
                else:
                    fail_count += 1

            # Small delay between batches
            if i + BATCH_SIZE < len(agent_list):
                print()
                time.sleep(2)

    print()
    print(f"Results: {success_count} started successfully, {fail_count} failed")
    print()

    if success_count > 0:
        print("✓ Agents are now running and ready for interactions!")
        print(f"  View status: curl {API_BASE_URL}/agents")
        print(f"  Search agents: curl '{API_BASE_URL}/agents/search?query=backend'")


if __name__ == "__main__":
    main()
