from __future__ import annotations

from pydantic import BaseModel, Field

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

MODEL_ID_TO_DIMENSION = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
}


class EmbeddingModel(BaseModel):
    model_id: str = Field(
        description="The model id of the embedding model.", default="sentence-transformers/all-MiniLM-L6-v2"
    )
    dimension: int = Field(description="The dimension of the embedding model.", default=384)

    @classmethod
    def create(cls, model_id: str | None = None) -> EmbeddingModel:
        dimension = MODEL_ID_TO_DIMENSION.get(model_id, DEFAULT_EMBEDDING_MODEL)
        if dimension is None:
            raise ValueError(f"Unknown embedding model id: {model_id}")

        return cls(model_id=model_id, dimension=dimension)
