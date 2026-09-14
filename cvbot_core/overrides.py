"""Partial replacement of frozen configuration objects."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, TypeVar

T = TypeVar("T")


def apply_overrides(instance: T, **overrides: Any) -> T:
    """Returns a copy of a dataclass with the given fields replaced.

    ``None`` values are ignored so that unset CLI arguments do not override the
    configuration coming from the environment.

    Args:
        instance: The dataclass instance to copy.
        **overrides: Field names and their new values.

    Returns:
        A new, validated instance.
    """
    effective = {
        key: value for key, value in overrides.items() if value is not None
    }
    return replace(instance, **effective)
