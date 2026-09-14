"""Reading of typed values from an environment mapping."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})


def read_str(env: Mapping[str, str], key: str, default: str) -> str:
    """Reads a string from the environment.

    Args:
        env: Mapping of variable names to values.
        key: Name of the variable.
        default: Value used if the variable is not set.

    Returns:
        The value or ``default``.
    """
    return env.get(key, default)


def read_path(env: Mapping[str, str], key: str, default: Path) -> Path:
    """Reads a filesystem path from the environment.

    Args:
        env: Mapping of variable names to values.
        key: Name of the variable.
        default: Value used if the variable is not set.

    Returns:
        The parsed path or ``default``.
    """
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    return Path(raw)


def read_int(env: Mapping[str, str], key: str, default: int) -> int:
    """Reads an integer from the environment.

    Args:
        env: Mapping of variable names to values.
        key: Name of the variable.
        default: Value used if the variable is not set.

    Returns:
        The parsed value or ``default``.

    Raises:
        ValueError: If the value is not an integer.
    """
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{key} is not an integer: {raw!r}") from exc


def read_bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    """Reads a boolean from the environment.

    Args:
        env: Mapping of variable names to values.
        key: Name of the variable.
        default: Value used if the variable is not set.

    Returns:
        The parsed value or ``default``.

    Raises:
        ValueError: If the value is not a known boolean spelling.
    """
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    normalized = raw.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError(f"{key} is not a boolean: {raw!r}")


def read_csv(
    env: Mapping[str, str], key: str, default: tuple[str, ...]
) -> tuple[str, ...]:
    """Reads a comma separated list from the environment.

    Args:
        env: Mapping of variable names to values.
        key: Name of the variable.
        default: Value used if the variable is not set.

    Returns:
        The parsed entries without surrounding whitespace, or ``default``.
    """
    raw = env.get(key)
    if raw is None or raw == "":
        return default
    return tuple(entry.strip() for entry in raw.split(",") if entry.strip())
