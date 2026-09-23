"""Tests for the structural backend interfaces."""

from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from cvbot_core.protocols import (
    EmbeddingModel,
    VectorStoreReader,
    VectorStoreWriter,
)
from cvbot_core.testing import FakeEmbeddings


class _Writer:
    """Store double that only writes."""

    def add_documents(self, documents: list[Document], **kwargs: Any) -> list[str]:
        """Accepts a batch and returns pseudo IDs."""
        return [str(index) for index in range(len(documents))]


class _Reader:
    """Store double that only reads."""

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[tuple[Document, float]]:
        """Returns no chunks."""
        return []


def test_fake_embeddings_satisfies_the_embedding_protocol(
    fake_embeddings: FakeEmbeddings,
) -> None:
    assert isinstance(fake_embeddings, EmbeddingModel)


def test_writer_and_reader_are_independent() -> None:
    assert isinstance(_Writer(), VectorStoreWriter)
    assert not isinstance(_Writer(), VectorStoreReader)
    assert isinstance(_Reader(), VectorStoreReader)
    assert not isinstance(_Reader(), VectorStoreWriter)
