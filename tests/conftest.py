"""Shared fixtures and test doubles."""

from __future__ import annotations

import pytest

from cvbot_core.testing import FakeEmbeddings


@pytest.fixture
def fake_embeddings() -> FakeEmbeddings:
    """Provides a deterministic embedding model.

    Returns:
        An embedding model that works without network access.
    """
    return FakeEmbeddings()
