"""Shared building blocks of the cvbot RAG system."""

from __future__ import annotations

from .embeddings import build_bedrock_embeddings
from .env import read_bool, read_csv, read_int, read_path, read_str
from .logging_config import LOG_FORMAT, VALID_LOG_LEVELS, configure_logging
from .overrides import apply_overrides
from .protocols import EmbeddingModel, VectorStoreReader, VectorStoreWriter
from .tokens import ENCODING_NAME, count_tokens, get_encoding
from .validation import (
    require_at_least,
    require_below,
    require_choice,
    require_http_origins,
    require_in_range,
    require_non_empty,
    require_port,
    require_positive,
)
from .vector_store import create_chroma_client

__all__ = [
    "ENCODING_NAME",
    "LOG_FORMAT",
    "VALID_LOG_LEVELS",
    "EmbeddingModel",
    "VectorStoreReader",
    "VectorStoreWriter",
    "apply_overrides",
    "build_bedrock_embeddings",
    "configure_logging",
    "count_tokens",
    "create_chroma_client",
    "get_encoding",
    "read_bool",
    "read_csv",
    "read_int",
    "read_path",
    "read_str",
    "require_at_least",
    "require_below",
    "require_choice",
    "require_http_origins",
    "require_in_range",
    "require_non_empty",
    "require_port",
    "require_positive",
]
