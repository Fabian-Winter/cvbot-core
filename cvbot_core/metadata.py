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
from typing import Any

LOGGER = logging.getLogger(__name__)

# Metadata keys owned by the loader, the chunker and the Markdown splitter.
# Sections cannot overwrite them and they never become filter fields.
RESERVED_METADATA_KEYS = frozenset(
    {"source", "filename", "chunk_index", "h1", "h2", "h3"}
)

# Period fields written by the documents and the coarse recency marker.
# Both sides read and write them, so their spelling lives here.
PERIOD_START_KEY = "startdate"
PERIOD_END_KEY = "enddate"
STATUS_KEY = "status"

# Values of ``enddate`` that mean "still running" rather than a concrete end date.
OPEN_PERIOD_MARKERS = frozenset(
    {
        "",
        "-",
        "laufend",
        "heute",
        "jetzt",
        "aktuell",
        "today",
        "now",
        "current",
        "present",
    }
)

_PERIOD_YEAR = re.compile(r"\b(\d{4})\b")

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


def parse_period_year(raw: str | None) -> int | None:
    """Reads the year out of a period bound.

    Accepts ``2011``, ``2011-10``, ``2011-10-01`` and prose like
    ``Oktober 2011``. Both the embedder that derives the year lists and the
    retriever that reads them back at query time use the same rule.

    Args:
        raw: The raw field value, if present.

    Returns:
        The year, or ``None`` if the value carries none.
    """
    if not raw:
        return None
    match = _PERIOD_YEAR.search(raw)
    return int(match.group(1)) if match else None


def period_end_year(
    metadata: Mapping[str, Any], now_year: int
) -> int | None:
    """Determines the last year a chunk speaks about, or ``None``.

    Single source of truth for the period semantics of ``startdate``/``enddate``/
    ``status``: cvbot-embedder derives the published ``years`` lists from it,
    cvbot-retriever rates recency with it, so both sides always agree on when
    a period ends. An open-ended ``enddate`` (``now``, ``laufend``, absent) reaches
    into the present, a concrete one ends at its year, and an open ``status``
    marks the undated sections as up to date.

    Args:
        metadata: The metadata of the chunk.
        now_year: The current year, passed in so callers stay deterministic.

    Returns:
        The end year, or ``None`` if the metadata carries no usable signal.
    """
    end_raw = metadata.get(PERIOD_END_KEY)
    end_text = end_raw if isinstance(end_raw, str) else None
    if end_text is not None and normalize_value(end_text) in OPEN_PERIOD_MARKERS:
        return now_year
    parsed = parse_period_year(end_text)
    if parsed is not None:
        return parsed

    start_raw = metadata.get(PERIOD_START_KEY)
    start = parse_period_year(start_raw if isinstance(start_raw, str) else None)
    if end_text is None and start is not None:
        # Absent end reads as "still running", exactly like the year list the
        # embedder derives from the same fields.
        return now_year
    if start is not None:
        # Unparsable end: conservative, a single-year period.
        return start

    status = metadata.get(STATUS_KEY)
    if isinstance(status, str) and normalize_value(status) in OPEN_PERIOD_MARKERS:
        return now_year
    return None


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
