from typing import Any

from app.config import Config, LLMProvider, VectorStoreProvider


def to_mem0_config(config: Config) -> dict[str, Any]:
    """Convert Config to mem0-compatible dict.

    Args:
        config: The application configuration.

    Returns:
        A dictionary compatible with mem0's configuration format.
    """
    result: dict[str, Any] = {"version": "v1.1"}

    match config.memory_llm_provider:
        case LLMProvider.OPENAI:
            llm_provider = "openai"
        case LLMProvider.GOOGLE:
            llm_provider = "google"
        case LLMProvider.OPENROUTER:
            llm_provider = "openrouter"
        case _:
            llm_provider = config.memory_llm_provider.value

    result["llm"] = {
        "provider": llm_provider,
        "config": {"model": config.memory_llm_model},
    }

    match config.memory_embedding_provider:
        case _:
            emb_provider = config.memory_embedding_provider.value

    result["embedder"] = {"provider": emb_provider, "config": {"model": config.memory_embedding_model}}

    match config.memory_vector_store_provider:
        case VectorStoreProvider.QDRANT:
            vs_provider = "qdrant"
        case _:
            vs_provider = config.memory_vector_store_provider.value

    result["vector_store"] = {
        "provider": vs_provider,
        "config": {
            "url": config.qdrant_url,
            "collection_name": config.memory_qdrant_collection,
            "embedding_model_dims": config.memory_embedding_dims,
        },
    }

    return result
