"""Factory for the Bedrock embedding model."""

from __future__ import annotations

import logging

from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import Embeddings

LOGGER = logging.getLogger(__name__)


def build_bedrock_embeddings(model_id: str, region_name: str) -> Embeddings:
    """Creates the embedding model used for indexing and querying.

    Ingestion and retrieval have to use the same model, otherwise the query
    vectors do not match the indexed ones.

    AWS credentials are resolved through the usual boto3 chain (environment
    variables, profile, IAM role of the Fargate task).

    Args:
        model_id: Bedrock model ID of the embedding model.
        region_name: AWS region of the Bedrock client.

    Returns:
        The configured Bedrock embedding model.
    """
    LOGGER.info(
        "Bedrock embeddings: model_id=%s region=%s", model_id, region_name
    )
    return BedrockEmbeddings(model_id=model_id, region_name=region_name)
