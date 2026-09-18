"""Shared vocabulary for the section metadata written into the Markdown files.

cvbot-embedder parses ``> key: value`` lines into chunk metadata and publishes
the observed schema on the collection; cvbot-retriever injects that schema into
the condensation prompt and matches the extracted filters against chunks. Both
sides must normalize keys and values identically, so the rules live here.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping, Sequence

LOGGER = logging.getLogger(__name__)

# Metadata keys owned by the loader, the chunker and the Markdown splitter.
# Sections cannot overwrite them and they never become filter fields.
RESERVED_METADATA_KEYS = frozenset(
    {"source", "filename", "chunk_index", "h1", "h2", "h3"}
)

# Chroma collection metadata has to stay small, and the schema is injected into
# a prompt, so both the field count and the value lists are capped.
MAX_SCHEMA_FIELDS = 30
MAX_VALUES_PER_FIELD = 50
MAX_VALUE_LENGTH = 80

# Separators used inside a single metadata line, e.g. "Java, Maven; SVN".
VALUE_SEPARATORS = re.compile(r"[,;]")

_UMLAUT_FOLDING = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
)
_NON_KEY_CHARS = re.compile(r"[^a-z0-9]+")
_WHITESPACE = re.compile(r"\s+")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def normalize_key(raw: str) -> str:
    """Turns a metadata key into a stable identifier.

    Umlauts are folded instead of dropped so that "Universität" and
    "Universitaet" end up as the same field.

    Args:
        raw: The key as written in the Markdown file.

    Returns:
        The lowercase, ASCII-only key, or an empty string if nothing remains.
    """
    folded = raw.strip().lower().translate(_UMLAUT_FOLDING)
    return _NON_KEY_CHARS.sub("_", folded).strip("_")


def normalize_value(raw: str) -> str:
    """Turns a metadata value into its comparable form.

    Args:
        raw: The value as written in the Markdown file or as returned by the
            model.

    Returns:
        The lowercase value with collapsed whitespace and control characters
        removed, truncated to ``MAX_VALUE_LENGTH``.
    """
    cleaned = _CONTROL_CHARS.sub(" ", raw)
    return _WHITESPACE.sub(" ", cleaned).strip().lower()[:MAX_VALUE_LENGTH]


def split_values(raw: str) -> list[str]:
    """Splits a metadata value into its individual, comparable values.

    Multi-value fields are stored as one delimited string because Chroma only
    accepts scalar metadata values.

    Args:
        raw: The raw value, e.g. ``"Java, Maven, SVN"``.

    Returns:
        The distinct normalized values in their original order.
    """
    values: list[str] = []
    for part in VALUE_SEPARATORS.split(raw):
        value = normalize_value(part)
        if value and value not in values:
            values.append(value)
    return values


def encode_schema(schema: Mapping[str, Sequence[str]]) -> str:
    """Serializes an observed schema for the Chroma collection metadata.

    Args:
        schema: Field name mapped onto its known values.

    Returns:
        Deterministic JSON so that re-indexing an unchanged corpus produces an
        unchanged collection metadata value.
    """
    return json.dumps(
        {field: sorted(values) for field, values in sorted(schema.items())},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def decode_schema(raw: str | None) -> dict[str, list[str]]:
    """Reads back a schema written by ``encode_schema``.

    Never raises: a collection indexed before this feature existed, or one
    carrying a corrupted value, simply has no filter fields.

    Args:
        raw: The stored JSON string, or ``None`` if the key is absent.

    Returns:
        Field name mapped onto its known values, or an empty mapping.
    """
    if not raw:
        return {}

    try:
        decoded = json.loads(raw)
    except (ValueError, TypeError):
        LOGGER.warning("metadata schema is not valid JSON, ignoring it")
        return {}

    if not isinstance(decoded, dict):
        LOGGER.warning("metadata schema is not an object, ignoring it")
        return {}

    schema: dict[str, list[str]] = {}
    for field, values in decoded.items():
        key = normalize_key(str(field))
        if not key or not isinstance(values, list):
            continue
        schema[key] = [
            normalize_value(str(value)) for value in values if str(value).strip()
        ]
    return schema
