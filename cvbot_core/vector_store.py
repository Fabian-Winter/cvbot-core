"""Connection to the ChromaDB instance (container running on AWS Fargate)."""

from __future__ import annotations

import logging

import chromadb

from .metadata import decode_schema

LOGGER = logging.getLogger(__name__)

# Collection metadata key cvbot-embedder writes and cvbot-retriever reads back.
EMBEDDING_MODEL_METADATA_KEY = "embedding_model_id"

# Observed section metadata schema, same write-once/read-back channel.
METADATA_SCHEMA_METADATA_KEY = "metadata_schema"

# Cosine matches embedding models optimized for cosine similarity (e.g. Titan).
DEFAULT_HNSW_SPACE = "cosine"

# Single source of truth so cvbot-embedder and cvbot-retriever cannot drift apart.
DEFAULT_COLLECTION_NAME = "cvbot_documents"
DEFAULT_CHROMA_HOST = "localhost"
DEFAULT_CHROMA_PORT = 8000


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


def read_metadata_schema(
    client: chromadb.ClientAPI, collection_name: str
) -> dict[str, list[str]]:
    """Reads the section metadata schema cvbot-embedder observed while indexing.

    Unlike the embedding model ID this is optional: a collection indexed before
    the feature existed, or one whose documents carry no metadata, simply has
    no filter fields.

    Args:
        client: The Chroma client.
        collection_name: Name of the collection.

    Returns:
        Field name mapped onto its known values, empty if the collection
        carries no schema.
    """
    collection = client.get_collection(collection_name)
    raw = (collection.metadata or {}).get(METADATA_SCHEMA_METADATA_KEY)
    return decode_schema(raw if isinstance(raw, str) else None)
