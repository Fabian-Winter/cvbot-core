"""Tests for the shared log configuration."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from cvbot_core.logging_config import LOG_FORMAT, configure_logging


def test_configure_logging_passes_level_and_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(logging, "basicConfig", lambda **kw: captured.update(kw))

    configure_logging("DEBUG")

    assert captured == {"level": "DEBUG", "format": LOG_FORMAT}
