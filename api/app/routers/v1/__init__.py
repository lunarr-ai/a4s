from fastapi import APIRouter

from app.routers.v1.agents import router as agents_router
from app.routers.v1.memory import router as memory_router
from app.routers.v1.skills import router as skills_router

router = APIRouter(prefix="/api/v1")
router.include_router(agents_router)
router.include_router(memory_router)
router.include_router(skills_router)

__all__ = ["router"]
