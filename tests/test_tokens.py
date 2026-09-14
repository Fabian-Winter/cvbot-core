"""Tests for the shared token counting."""

from __future__ import annotations

from cvbot_core.tokens import ENCODING_NAME, count_tokens, get_encoding


def test_encoding_is_shared_across_calls() -> None:
    assert get_encoding() is get_encoding()
    assert get_encoding().name == ENCODING_NAME


def test_count_tokens_of_an_empty_text_is_zero() -> None:
    assert count_tokens("") == 0


def test_count_tokens_grows_with_the_text() -> None:
    short = count_tokens("one sentence")
    long = count_tokens("one sentence " * 20)

    assert 0 < short < long


def test_count_tokens_matches_the_encoding() -> None:
    text = "Die Urlaubsregelung gilt für alle Mitarbeitenden."

    assert count_tokens(text) == len(get_encoding().encode(text))
