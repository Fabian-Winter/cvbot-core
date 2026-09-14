"""Test doubles shared by the test suites of the cvbot services."""

from __future__ import annotations

import hashlib

from langchain_core.embeddings import Embeddings


class FakeEmbeddings(Embeddings):
    """Deterministic embedding model without network access.

    Produces reproducible vectors from a hash of the text so that similarity
    based logic can be tested without calling AWS.
    """

    def __init__(self, dimensions: int = 8) -> None:
        """Initializes the model.

        Args:
            dimensions: Length of the produced vectors.
        """
        self.dimensions = dimensions
        self.calls: list[list[str]] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Produces vectors for several texts.

        Args:
            texts: The texts to embed.

        Returns:
            One vector per text.
        """
        self.calls.append(list(texts))
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Produces a vector for a single text.

        Args:
            text: The text to embed.

        Returns:
            The vector.
        """
        self.calls.append([text])
        return self._vector(text)

    def _vector(self, text: str) -> list[float]:
        """Maps a text deterministically onto a vector.

        Args:
            text: The text to embed.

        Returns:
            The vector of length ``dimensions``.
        """
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [digest[i % len(digest)] / 255.0 for i in range(self.dimensions)]
