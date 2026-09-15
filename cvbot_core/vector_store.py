"""Connection to the ChromaDB instance (container running on AWS Fargate)."""

from __future__ import annotations

import logging

import chromadb

LOGGER = logging.getLogger(__name__)

# Collection metadata key cvbot-embedder writes and cvbot-retriever reads back.
EMBEDDING_MODEL_METADATA_KEY = "embedding_model_id"

# Single source of truth so cvbot-embedder and cvbot-retriever cannot drift apart.
DEFAULT_COLLECTION_NAME = "cvbot_documents"


def create_chroma_client(host: str, port: int) -> chromadb.ClientAPI:
    """Creates an HTTP client for the ChromaDB instance.

    Args:
        host: Hostname of the ChromaDB instance.
        port: Port of the ChromaDB instance.

    Returns:
        The connected Chroma client.
    """
    LOGGER.info("connecting to ChromaDB: %s:%d", host, port)
    return chromadb.HttpClient(host=host, port=port)


def read_embedding_model_id(
    client: chromadb.ClientAPI, collection_name: str
) -> str:
    """Reads the embedding model ID cvbot-embedder stored in the collection.

    Args:
        client: The Chroma client.
        collection_name: Name of the collection.

    Returns:
        The Bedrock model ID the collection was indexed with.

    Raises:
        RuntimeError: If the collection does not exist or was not created by
            cvbot-embedder (i.e. it carries no embedding model metadata).
    """
    collection = client.get_collection(collection_name)
    model_id = (collection.metadata or {}).get(EMBEDDING_MODEL_METADATA_KEY)
    if not model_id:
        raise RuntimeError(
            f"collection {collection_name!r} has no "
            f"{EMBEDDING_MODEL_METADATA_KEY!r} metadata; it must be "
            "(re)created by cvbot-embedder"
        )
    return model_id
