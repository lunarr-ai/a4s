from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import config
from app.runtime.docker_manager import DockerRuntimeManager
from app.runtime.exceptions import AgentNotFoundError, AgentSpawnError, ImageNotFoundError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    runtime_manager = DockerRuntimeManager()

    yield

    runtime_manager.close()


app = FastAPI(title="A4S API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(AgentNotFoundError)
async def agent_not_found_handler(_request: Request, exc: AgentNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(AgentSpawnError)
async def agent_spawn_error_handler(_request: Request, exc: AgentSpawnError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(ImageNotFoundError)
async def image_not_found_handler(_request: Request, exc: ImageNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
