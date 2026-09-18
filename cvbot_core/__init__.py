"""Shared building blocks of the cvbot RAG system."""

from __future__ import annotations

from .embeddings import build_bedrock_embeddings
from .env import read_bool, read_csv, read_int, read_path, read_str
from .logging_config import LOG_FORMAT, VALID_LOG_LEVELS, configure_logging
from .metadata import (
    MAX_SCHEMA_FIELDS,
    MAX_VALUE_LENGTH,
    MAX_VALUES_PER_FIELD,
    RESERVED_METADATA_KEYS,
    decode_schema,
    encode_schema,
    normalize_key,
    normalize_value,
    split_values,
)
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
    "MAX_SCHEMA_FIELDS",
    "MAX_VALUES_PER_FIELD",
    "MAX_VALUE_LENGTH",
    "RESERVED_METADATA_KEYS",
    "VALID_LOG_LEVELS",
    "EmbeddingModel",
    "VectorStoreReader",
    "VectorStoreWriter",
    "apply_overrides",
    "build_bedrock_embeddings",
    "configure_logging",
    "count_tokens",
    "create_chroma_client",
    "decode_schema",
    "encode_schema",
    "get_encoding",
    "normalize_key",
    "normalize_value",
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
    "split_values",
]
