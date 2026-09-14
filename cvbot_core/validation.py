"""Validators shared by the configuration of the cvbot services.

Every check raises ``ValueError`` with the field name in the message, so the
configuration of a service can be validated field by field without repeating
the same comparisons in each repository.
"""

from __future__ import annotations

from collections.abc import Container, Iterable

_ORIGIN_SCHEMES = ("http://", "https://")

MIN_PORT = 1
MAX_PORT = 65535


def require_non_empty(value: str, name: str) -> None:
    """Rejects an empty string.

    Args:
        value: The configured value.
        name: Field name used in the error message.

    Raises:
        ValueError: If the value is empty.
    """
    if not value:
        raise ValueError(f"{name} must not be empty")


def require_port(value: int, name: str) -> None:
    """Rejects a port outside the valid TCP range.

    Args:
        value: The configured port.
        name: Field name used in the error message.

    Raises:
        ValueError: If the port is outside 1-65535.
    """
    if not MIN_PORT <= value <= MAX_PORT:
        raise ValueError(f"{name} outside {MIN_PORT}-{MAX_PORT}: {value}")


def require_positive(value: int, name: str) -> None:
    """Rejects a value that is not at least one.

    Args:
        value: The configured value.
        name: Field name used in the error message.

    Raises:
        ValueError: If the value is smaller than one.
    """
    if value < 1:
        raise ValueError(f"{name} must be positive: {value}")


def require_below(value: int, limit: int, name: str, limit_name: str) -> None:
    """Rejects a value that reaches or exceeds another one.

    Args:
        value: The configured value.
        limit: The value it has to stay below.
        name: Field name used in the error message.
        limit_name: Name of the limiting field.

    Raises:
        ValueError: If the value is not smaller than the limit.
    """
    if value >= limit:
        raise ValueError(
            f"{name} must be smaller than {limit_name}: {value} >= {limit}"
        )


def require_at_least(value: int, floor: int, name: str, floor_name: str) -> None:
    """Rejects a value that falls below another one.

    Args:
        value: The configured value.
        floor: The value it has to reach.
        name: Field name used in the error message.
        floor_name: Name of the limiting field.

    Raises:
        ValueError: If the value is smaller than the floor.
    """
    if value < floor:
        raise ValueError(
            f"{name} must not be smaller than {floor_name}: {value} < {floor}"
        )


def require_in_range(value: int, limit: int, name: str, limit_name: str) -> None:
    """Rejects a value outside ``0`` up to (excluding) another one.

    Args:
        value: The configured value.
        limit: The exclusive upper bound.
        name: Field name used in the error message.
        limit_name: Name of the limiting field.

    Raises:
        ValueError: If the value is negative or reaches the limit.
    """
    if not 0 <= value < limit:
        raise ValueError(
            f"{name} must be smaller than {limit_name}: {value} >= {limit}"
        )


def require_choice(value: str, allowed: Container[str], name: str) -> None:
    """Rejects a value that is not part of an allow list.

    Args:
        value: The configured value.
        allowed: The accepted values.
        name: Field name used in the error message.

    Raises:
        ValueError: If the value is not allowed.
    """
    if value not in allowed:
        raise ValueError(f"unknown {name}: {value}")


def require_http_origins(origins: Iterable[str], name: str) -> None:
    """Checks that every entry of a CORS allow list is a bare origin.

    Args:
        origins: The configured entries.
        name: Field name used in the error message.

    Raises:
        ValueError: If an entry is a wildcard, lacks a scheme or carries a
            path, since browsers match origins literally.
    """
    for origin in origins:
        if origin == "*":
            raise ValueError(
                f"{name} must not contain '*': list the origins explicitly"
            )
        if not origin.startswith(_ORIGIN_SCHEMES):
            raise ValueError(
                f"cors origin must start with http:// or https://: {origin!r}"
            )
        if origin.endswith("/") or "/" in origin.split("//", 1)[1]:
            raise ValueError(f"cors origin must not contain a path: {origin!r}")
