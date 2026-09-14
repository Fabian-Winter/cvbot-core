"""Token counting shared by chunking and context management.

Uses ``cl100k_base`` for every service, which is an approximation for the
Bedrock models but keeps chunk sizes and context budgets consistent across the
repositories and makes both deterministic and testable.
"""

from __future__ import annotations

from functools import lru_cache

import tiktoken

ENCODING_NAME = "cl100k_base"


@lru_cache(maxsize=1)
def get_encoding() -> tiktoken.Encoding:
    """Loads the encoding once per process.

    Returns:
        The ``cl100k_base`` encoding.
    """
    return tiktoken.get_encoding(ENCODING_NAME)


def count_tokens(text: str) -> int:
    """Counts the tokens of a text.

    Args:
        text: The text to measure.

    Returns:
        The token count according to ``cl100k_base``.
    """
    if not text:
        return 0
    return len(get_encoding().encode(text))
