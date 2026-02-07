from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from typing import TYPE_CHECKING

import httpx

from app.models import Agent, AgentMode, AgentStatus
from app.runtime.activity_monitor import AgentActivityMonitor
from app.runtime.exceptions import AgentNotFoundError
from app.runtime.models import SpawnAgentRequest

if TYPE_CHECKING:
    from app.broker.registry import AgentRegistry
    from app.runtime.manager import RuntimeManager

logger = logging.getLogger(__name__)

READINESS_TIMEOUT = 30.0
READINESS_POLL_INTERVAL = 0.5


class AgentScheduler:
    """Manages agent lifecycle.

    Args:
        runtime_manager: Runtime manager for spawning/stopping agents.
        registry: Agent registry for looking up agent metadata.
        idle_timeout: Seconds of inactivity before stopping an agent.
        reaper_interval: Seconds between idle reaper checks.
    """

    def __init__(
        self,
        runtime_manager: RuntimeManager,
        registry: AgentRegistry,
        idle_timeout: int = 300,
        reaper_interval: int = 30,
    ) -> None:
        self._runtime = runtime_manager
        self._registry = registry
        self._monitor = AgentActivityMonitor()
        self._idle_timeout = idle_timeout
        self._reaper_interval = reaper_interval
        self._reaper_task: asyncio.Task | None = None

    async def ensure_running(self, agent_id: str) -> tuple[Agent, int | None]:
        """Ensure agent is running, spawning if needed.

        Args:
            agent_id: The agent ID to ensure is running.

        Returns:
            Tuple of (agent, cold_start_ms or None if already running).

        Raises:
            AgentNotRegisteredError: If the agent is not in the registry.
        """
        agent = await self._registry.get_agent(agent_id)

        if agent.mode != AgentMode.SERVERLESS:
            return agent, None

        container_name = f"a4s-agent-{agent_id}"
        try:
            status = self._runtime.get_agent_status(container_name)
            if status == AgentStatus.RUNNING:
                return agent, None
        except AgentNotFoundError:
            pass

        start_time = time.monotonic()
        spawn_request = SpawnAgentRequest(
            agent_id=agent.id,
            name=agent.name,
            image=agent.spawn_config.image,
            version=agent.version,
            port=agent.port,
            model=agent.spawn_config.model,
            description=agent.description,
            instruction=agent.spawn_config.instruction,
            tools=agent.spawn_config.tools,
            mcp_tool_filter=agent.spawn_config.mcp_tool_filter,
        )
        self._runtime.spawn_agent(spawn_request)
        await self._wait_for_ready(agent.url)
        cold_start_ms = int((time.monotonic() - start_time) * 1000)

        logger.info("Cold started agent %s in %dms", agent_id, cold_start_ms)
        return agent, cold_start_ms

    async def _wait_for_ready(self, agent_url: str) -> None:
        """Poll agent until it responds or timeout."""
        deadline = time.monotonic() + READINESS_TIMEOUT
        async with httpx.AsyncClient(timeout=2.0) as client:
            while time.monotonic() < deadline:
                try:
                    resp = await client.get(agent_url)
                    if resp.status_code < 500:
                        return
                except httpx.RequestError:
                    pass
                await asyncio.sleep(READINESS_POLL_INTERVAL)
        logger.warning("Agent at %s did not become ready in time", agent_url)

    def record_activity(self, agent_id: str) -> None:
        """Record activity for idle tracking.

        Args:
            agent_id: The agent ID to record activity for.
        """
        self._monitor.record(agent_id)

    async def start(self) -> None:
        """Start the idle reaper background task."""
        if self._reaper_task is not None:
            return
        self._reaper_task = asyncio.create_task(self._reaper_loop())
        logger.info("Started agent reaper (timeout=%ds, interval=%ds)", self._idle_timeout, self._reaper_interval)

    async def stop(self) -> None:
        """Stop the idle reaper and cleanup."""
        if self._reaper_task is not None:
            self._reaper_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reaper_task
            self._reaper_task = None
            logger.info("Stopped agent reaper")

    async def _reaper_loop(self) -> None:
        """Background task that terminates idle agents."""
        while True:
            try:
                await asyncio.sleep(self._reaper_interval)
                idle_agents = self._monitor.get_idle_agents(self._idle_timeout)
                for agent_id in idle_agents:
                    try:
                        container_name = f"a4s-agent-{agent_id}"
                        self._runtime.stop_agent(container_name)
                        self._monitor.remove(agent_id)
                        logger.info("Reaped idle agent %s", agent_id)
                    except AgentNotFoundError:
                        self._monitor.remove(agent_id)
                    except Exception:
                        logger.exception("Failed to reap agent %s", agent_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error in reaper loop")
