from app.config import Config
from app.config import config as default_config
from app.memory.graphiti_manager import GraphitiMemoryManager
from app.memory.manager import MemoryManager


async def create_memory_manager(config: Config | None = None) -> MemoryManager:
    """Create a Graphiti memory manager.

    Args:
        config: Optional configuration. Uses default config if not provided.

    Returns:
        A configured GraphitiMemoryManager instance.
    """
    cfg = config or default_config
    return await GraphitiMemoryManager.create(cfg)
