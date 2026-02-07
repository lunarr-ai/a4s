"""Register all TechFlow Solutions agents via A4S API."""  # noqa: N999

import json
from pathlib import Path

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
COMPANY_STRUCTURE_PATH = Path(__file__).parent.parent / "data/agents.json"
REGISTERED_AGENTS_PATH = Path(__file__).parent.parent / "data/registered_agents.json"


def load_company_structure() -> dict:
    """Load company structure from JSON file."""
    with Path.open(COMPANY_STRUCTURE_PATH) as f:
        return json.load(f)


def register_agent(client: httpx.Client, agent_data: dict) -> dict:
    """Register a single agent via API.

    Args:
        client: HTTP client.
        agent_data: Agent configuration from agents.json.

    Returns:
        Registered agent response.
    """
    # Prepare request payload
    payload = {
        "name": agent_data["id"],
        "description": agent_data["description"],
        "version": "1.0.0",
        "port": 8000,
        "mode": "permanent",
        "spawn_config": agent_data["spawn_config"],
    }

    # Register agent
    response = client.post(f"{API_BASE_URL}/agents", json=payload)
    response.raise_for_status()

    registered_agent = response.json()
    print(f"✓ Registered: {agent_data['name']} (ID: {registered_agent['id']})")

    return registered_agent


def main() -> None:
    """Register all agents and save their IDs."""
    # Load company structure
    company_data = load_company_structure()
    agents = company_data["agents"]

    print(f"Registering {len(agents)} agents for {company_data['company_name']}...")
    print()

    registered_agents = {}

    with httpx.Client(timeout=30.0) as client:
        for agent_data in agents:
            try:
                registered = register_agent(client, agent_data)
                registered_agents[registered["id"]] = {
                    "id": registered["id"],
                    "name": registered["name"],
                    "description": registered["description"],
                    "department": agent_data.get("department"),
                    "team": agent_data.get("team"),
                    "role": agent_data.get("role"),
                }
            except Exception as e:
                print(f"✗ Failed to register {agent_data['name']}: {e}")
                continue

    # Save registered agents to file
    with Path.open(REGISTERED_AGENTS_PATH, "w") as f:
        json.dump(registered_agents, f, indent=2)

    print()
    print(f"Successfully registered {len(registered_agents)}/{len(agents)} agents")
    print(f"Saved agent IDs to: {REGISTERED_AGENTS_PATH}")


if __name__ == "__main__":
    main()
