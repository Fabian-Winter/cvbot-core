"""Tests for the ChromaDB connection."""

from __future__ import annotations

import pytest

from cvbot_core import vector_store


def test_create_chroma_client_passes_connection_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        vector_store.chromadb, "HttpClient", lambda **kw: captured.update(kw)
    )

    vector_store.create_chroma_client(host="chroma.internal", port=8443)

    assert captured["host"] == "chroma.internal"
    assert captured["port"] == 8443
