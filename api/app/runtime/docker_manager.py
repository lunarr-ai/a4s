import logging

from docker import DockerClient
from docker.errors import DockerException, ImageNotFound, NotFound

from app.models import Agent, AgentStatus
from app.runtime.exceptions import (
    AgentNotFoundError,
    AgentSpawnError,
    ImageNotFoundError,
)
from app.runtime.manager import RuntimeManager
from app.runtime.models import SpawnAgentRequest

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "unix:///var/run/docker.sock"
DEFAULT_API_BASE_URL = "http://host.docker.internal:8000"
DEFAULT_NETWORK = "a4s-agents"
LABEL_PREFIX = "a4s"
CONTAINER_PORT = 8000


class DockerRuntimeManager(RuntimeManager):
    """Runtime manager implementation using Docker.

    Args:
        base_url: Docker daemon URL. Defaults to unix socket.
        network_name: Docker network name.
    """

    def __init__(
        self, base_url: str | None = None, network_name: str = DEFAULT_NETWORK, api_base_url: str = DEFAULT_API_BASE_URL
    ) -> None:
        self._client = DockerClient(base_url=base_url or DEFAULT_BASE_URL)
        self._network_name = network_name
        self._ensure_network()

        self._api_base_url = api_base_url

    # TODO: uniqueness
    def _container_name(self, name: str) -> str:
        return f"a4s-agent-{name}"

    def _ensure_network(self) -> None:
        try:
            self._client.networks.get(self._network_name)
        except NotFound:
            self._client.networks.create(self._network_name, driver="bridge")
            logger.info("Created network %s", self._network_name)

    def _ensure_image(self, image: str) -> None:
        try:
            self._client.images.get(image)
        except ImageNotFound:
            logger.info("Pulling image %s", image)
            try:
                self._client.images.pull(image)
            except DockerException as e:
                raise ImageNotFoundError(f"Failed to pull image {image}: {e}") from e

    def spawn_agent(self, request: SpawnAgentRequest) -> Agent:
        """Spawn a new agent container.

        Args:
            request: Agent spawn configuration.

        Returns:
            Agent metadata for the spawned container.

        Raises:
            ImageNotFoundError: If the image cannot be pulled.
            AgentSpawnError: If the container fails to start.
        """
        container_name = self._container_name(request.name)
        self._ensure_image(request.image)
        try:
            labels = {
                f"{LABEL_PREFIX}.managed": "true",
                f"{LABEL_PREFIX}.name": request.name,
                f"{LABEL_PREFIX}.description": request.description,
                f"{LABEL_PREFIX}.version": request.version,
            }
            environment = {
                "AGENT_NAME": request.name,
                "AGENT_MODEL_PROVIDER": request.model.provider.value,
                "AGENT_MODEL_ID": request.model.model_id,
                "AGENT_INSTRUCTION": request.instruction,
                "AGENT_TOOLS": ",".join(request.tools),
                "A4S_API_URL": self._api_base_url,
            }
            container = self._client.containers.run(
                request.image,
                detach=True,
                name=container_name,
                network=self._network_name,
                labels=labels,
                environment=environment,
            )
            logger.info("Spawned agent %s (container %s)", request.name, container.id)
            return Agent(
                id=container.id,
                name=request.name,
                description=request.description,
                version=request.version,
                url=f"http://{container_name}:{CONTAINER_PORT}",
                port=CONTAINER_PORT,
                status=AgentStatus.RUNNING,
            )
        except DockerException as e:
            logger.error("Failed to spawn agent %s: %s", request.name, e)
            raise AgentSpawnError(f"Failed to spawn agent {request.name}: {e}") from e

    def stop_agent(self, agent_id: str) -> Agent:
        """Stop and remove an agent container.

        Args:
            agent_id: Container ID or name.

        Returns:
            Agent metadata with stopped status.

        Raises:
            AgentNotFoundError: If the container does not exist.
        """
        try:
            container = self._client.containers.get(agent_id)
            labels = container.labels
            container.stop()
            container.remove()
            logger.info("Stopped agent %s", agent_id)
            return Agent(
                id=container.id,
                name=labels.get(f"{LABEL_PREFIX}.name", ""),
                description=labels.get(f"{LABEL_PREFIX}.description", ""),
                version=labels.get(f"{LABEL_PREFIX}.version", ""),
                url="",
                port=0,
                status=AgentStatus.STOPPED,
            )
        except NotFound as e:
            logger.error("Agent %s not found", agent_id)
            raise AgentNotFoundError(f"Agent {agent_id} not found") from e
        except DockerException as e:
            logger.error("Failed to stop agent %s: %s", agent_id, e)
            raise AgentNotFoundError(f"Failed to stop agent {agent_id}: {e}") from e

    def list_agents(self) -> list[Agent]:
        """List all managed agent containers.

        Returns:
            List of agent metadata for all running containers.
        """
        containers = self._client.containers.list(filters={"label": f"{LABEL_PREFIX}.managed=true"})
        agents = []
        for c in containers:
            labels = c.labels
            agents.append(
                Agent(
                    id=c.id,
                    name=labels.get(f"{LABEL_PREFIX}.name", ""),
                    description=labels.get(f"{LABEL_PREFIX}.description", ""),
                    version=labels.get(f"{LABEL_PREFIX}.version", ""),
                    url=f"http://{c.name}:{CONTAINER_PORT}",
                    port=CONTAINER_PORT,
                    status=self._map_status(c.status),
                )
            )
        return agents

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get the status of an agent container.

        Args:
            agent_id: Container ID or name.

        Returns:
            Current status of the agent.

        Raises:
            AgentNotFoundError: If the container does not exist.
        """
        try:
            container = self._client.containers.get(agent_id)
            return self._map_status(container.status)
        except NotFound as e:
            logger.error("Agent %s not found", agent_id)
            raise AgentNotFoundError(f"Agent {agent_id} not found") from e

    def _map_status(self, docker_status: str) -> AgentStatus:
        mapping = {
            "created": AgentStatus.PENDING,
            "running": AgentStatus.RUNNING,
            "paused": AgentStatus.RUNNING,
            "restarting": AgentStatus.PENDING,
            "removing": AgentStatus.STOPPED,
            "exited": AgentStatus.STOPPED,
            "dead": AgentStatus.ERROR,
        }
        return mapping.get(docker_status, AgentStatus.ERROR)

    def close(self) -> None:
        """Close the Docker runtime manager."""
        self._client.close()
