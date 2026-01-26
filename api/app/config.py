from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    cors_origins: list[str] = Field(default_factory=list)

    # Registry
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_collection_name: str = Field(default="agents")

    embedding_model_id: str = Field(default="all-MiniLM-L6-v2")


config = Config()
