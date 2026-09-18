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


class FakeCollection:
    def __init__(self, metadata: dict[str, object] | None) -> None:
        self.metadata = metadata


class FakeClient:
    def __init__(self, collection: FakeCollection) -> None:
        self._collection = collection

    def get_collection(self, name: str) -> FakeCollection:
        self.requested_name = name
        return self._collection


def test_read_embedding_model_id_returns_the_stored_value() -> None:
    client = FakeClient(FakeCollection({"embedding_model_id": "amazon.titan-embed-text-v2:0"}))

    model_id = vector_store.read_embedding_model_id(client, "jobs")

    assert model_id == "amazon.titan-embed-text-v2:0"
    assert client.requested_name == "jobs"


def test_read_embedding_model_id_raises_when_metadata_is_missing() -> None:
    client = FakeClient(FakeCollection(None))

    with pytest.raises(RuntimeError, match="jobs"):
        vector_store.read_embedding_model_id(client, "jobs")


def test_read_embedding_model_id_raises_when_key_is_absent() -> None:
    client = FakeClient(FakeCollection({"other_key": "value"}))

    with pytest.raises(RuntimeError, match="embedding_model_id"):
        vector_store.read_embedding_model_id(client, "jobs")


def test_read_metadata_schema_returns_the_stored_schema() -> None:
    client = FakeClient(FakeCollection({"metadata_schema": '{"status":["aktuell"]}'}))

    assert vector_store.read_metadata_schema(client, "jobs") == {
        "status": ["aktuell"]
    }


def test_read_metadata_schema_returns_empty_when_key_is_absent() -> None:
    client = FakeClient(FakeCollection({"embedding_model_id": "titan"}))

    assert vector_store.read_metadata_schema(client, "jobs") == {}


def test_read_metadata_schema_returns_empty_without_collection_metadata() -> None:
    client = FakeClient(FakeCollection(None))

    assert vector_store.read_metadata_schema(client, "jobs") == {}
