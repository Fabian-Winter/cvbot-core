"""Tests for the Bedrock embedding factory."""

from __future__ import annotations

import pytest

from cvbot_core import embeddings


def test_build_bedrock_embeddings_passes_model_and_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(embeddings, "BedrockEmbeddings", lambda **kw: kw)

    model = embeddings.build_bedrock_embeddings(
        model_id="amazon.titan-embed-text-v2:0", region_name="eu-west-1"
    )

    assert model == {
        "model_id": "amazon.titan-embed-text-v2:0",
        "region_name": "eu-west-1",
    }
