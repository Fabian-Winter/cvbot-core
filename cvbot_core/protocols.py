"""Structural interfaces of the backends the cvbot services talk to.

The services depend on these protocols instead of the concrete LangChain and
Chroma classes: the ingestion only needs to write, the retrieval only needs to
read, and neither has to be changed when the other side of the store does.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from langchain_core.documents import Document


@runtime_checkable
class EmbeddingModel(Protocol):
    """Turns text into vectors."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Produces vectors for several texts.

        Args:
            texts: The texts to embed.

        Returns:
            One vector per text.
        """
        ...

    def embed_query(self, text: str) -> list[float]:
        """Produces a vector for a single text.

        Args:
            text: The text to embed.

        Returns:
            The vector.
        """
        ...


@runtime_checkable
class VectorStoreWriter(Protocol):
    """Target store of the ingestion pipeline."""

    def add_documents(self, documents: list[Document], **kwargs: Any) -> list[str]:
        """Writes chunks to the store.

        Args:
            documents: The chunks to index.
            **kwargs: Store specific options.

        Returns:
            The identifiers of the written chunks.
        """
        ...


@runtime_checkable
class VectorStoreReader(Protocol):
    """Source store of the retrieval pipeline."""

    def similarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[Document]:
        """Looks up the chunks that match a query.

        Args:
            query: The text to match against.
            k: Number of chunks to return.
            **kwargs: Store specific options.

        Returns:
            The matching chunks, ordered by decreasing similarity.
        """
        ...
