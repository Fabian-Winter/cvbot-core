"""Tests for the shared configuration validators."""

from __future__ import annotations

import pytest

from cvbot_core.validation import (
    require_at_least,
    require_below,
    require_choice,
    require_http_origins,
    require_in_range,
    require_non_empty,
    require_port,
    require_positive,
)


def test_require_non_empty_names_the_field() -> None:
    require_non_empty("value", "chroma_host")
    with pytest.raises(ValueError, match="chroma_host must not be empty"):
        require_non_empty("", "chroma_host")


@pytest.mark.parametrize("port", [1, 8000, 65535])
def test_require_port_accepts_the_valid_range(port: int) -> None:
    require_port(port, "chroma_port")


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_require_port_rejects_values_outside_the_range(port: int) -> None:
    with pytest.raises(ValueError, match=r"chroma_port outside 1-65535"):
        require_port(port, "chroma_port")


def test_require_positive_rejects_zero_and_below() -> None:
    require_positive(1, "batch_size")
    with pytest.raises(ValueError, match="batch_size must be positive: 0"):
        require_positive(0, "batch_size")


def test_require_below_rejects_reaching_the_limit() -> None:
    require_below(10, 20, "buffer", "budget")
    with pytest.raises(
        ValueError, match=r"buffer must be smaller than budget: 20 >= 20"
    ):
        require_below(20, 20, "buffer", "budget")


def test_require_at_least_rejects_falling_below_the_floor() -> None:
    require_at_least(60, 10, "per_hour", "per_minute")
    with pytest.raises(
        ValueError, match=r"per_hour must not be smaller than per_minute: 5 < 10"
    ):
        require_at_least(5, 10, "per_hour", "per_minute")


def test_require_in_range_rejects_negative_and_overflowing_values() -> None:
    require_in_range(0, 10, "overlap", "max_tokens")
    require_in_range(9, 10, "overlap", "max_tokens")
    with pytest.raises(ValueError, match="overlap must be smaller than max_tokens"):
        require_in_range(10, 10, "overlap", "max_tokens")
    with pytest.raises(ValueError, match="overlap must be smaller than max_tokens"):
        require_in_range(-1, 10, "overlap", "max_tokens")


def test_require_choice_rejects_an_unknown_value() -> None:
    require_choice("INFO", {"INFO", "DEBUG"}, "log_level")
    with pytest.raises(ValueError, match="unknown log_level: TRACE"):
        require_choice("TRACE", {"INFO", "DEBUG"}, "log_level")


def test_require_http_origins_accepts_bare_origins() -> None:
    require_http_origins(
        ("https://example.com", "http://localhost:8080"), "cors_allowed_origins"
    )


def test_require_http_origins_rejects_the_wildcard() -> None:
    with pytest.raises(ValueError, match="must not contain"):
        require_http_origins(("*",), "cors_allowed_origins")


def test_require_http_origins_rejects_a_missing_scheme() -> None:
    with pytest.raises(ValueError, match="must start with http"):
        require_http_origins(("example.com",), "cors_allowed_origins")


@pytest.mark.parametrize(
    "origin", ["https://example.com/", "https://example.com/app"]
)
def test_require_http_origins_rejects_a_path(origin: str) -> None:
    with pytest.raises(ValueError, match="must not contain a path"):
        require_http_origins((origin,), "cors_allowed_origins")
