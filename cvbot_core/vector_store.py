"""Connection to the ChromaDB instance (container running on AWS Fargate)."""

from __future__ import annotations

import logging

import chromadb

LOGGER = logging.getLogger(__name__)


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
