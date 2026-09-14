"""Tests for the partial replacement of configuration objects."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from cvbot_core.overrides import apply_overrides


@dataclass(frozen=True)
class _Config:
    """Minimal configuration used as a stand-in for a service ``Settings``."""

    host: str = "localhost"
    port: int = 8000

    def __post_init__(self) -> None:
        """Validates the port.

        Raises:
            ValueError: If the port is not positive.
        """
        if self.port < 1:
            raise ValueError(f"port must be positive: {self.port}")


def test_apply_overrides_replaces_the_given_fields() -> None:
    updated = apply_overrides(_Config(), host="chroma.internal", port=8443)

    assert updated == _Config(host="chroma.internal", port=8443)


def test_apply_overrides_ignores_none_values() -> None:
    original = _Config(host="chroma.internal")

    updated = apply_overrides(original, host=None, port=None)

    assert updated == original


def test_apply_overrides_leaves_the_original_untouched() -> None:
    original = _Config()

    apply_overrides(original, port=9000)

    assert original.port == 8000


def test_apply_overrides_revalidates_the_result() -> None:
    with pytest.raises(ValueError, match="port must be positive"):
        apply_overrides(_Config(), port=0)
