"""Tests for reading typed values from the environment."""

from __future__ import annotations

from pathlib import Path

import pytest

from cvbot_core.env import read_bool, read_csv, read_int, read_path, read_str


def test_read_str_falls_back_to_the_default() -> None:
    assert read_str({}, "NAME", "fallback") == "fallback"
    assert read_str({"NAME": "value"}, "NAME", "fallback") == "value"


def test_read_path_treats_an_empty_value_as_unset() -> None:
    assert read_path({"DIR": ""}, "DIR", Path("/default")) == Path("/default")
    assert read_path({"DIR": "/data"}, "DIR", Path("/default")) == Path("/data")


def test_read_int_parses_and_falls_back() -> None:
    assert read_int({}, "PORT", 8000) == 8000
    assert read_int({"PORT": ""}, "PORT", 8000) == 8000
    assert read_int({"PORT": "9000"}, "PORT", 8000) == 9000


def test_read_int_rejects_a_non_numeric_value() -> None:
    with pytest.raises(ValueError, match="PORT is not an integer"):
        read_int({"PORT": "many"}, "PORT", 8000)


@pytest.mark.parametrize("raw", ["1", "true", "TRUE", " yes ", "on"])
def test_read_bool_accepts_the_true_spellings(raw: str) -> None:
    assert read_bool({"FLAG": raw}, "FLAG", False) is True


@pytest.mark.parametrize("raw", ["0", "false", "FALSE", " no ", "off"])
def test_read_bool_accepts_the_false_spellings(raw: str) -> None:
    assert read_bool({"FLAG": raw}, "FLAG", True) is False


def test_read_bool_falls_back_and_rejects_unknown_spellings() -> None:
    assert read_bool({}, "FLAG", True) is True
    assert read_bool({"FLAG": ""}, "FLAG", True) is True
    with pytest.raises(ValueError, match="FLAG is not a boolean"):
        read_bool({"FLAG": "maybe"}, "FLAG", True)


def test_read_csv_splits_and_strips_entries() -> None:
    assert read_csv({}, "ORIGINS", ("a",)) == ("a",)
    assert read_csv({"ORIGINS": ""}, "ORIGINS", ("a",)) == ("a",)
    assert read_csv({"ORIGINS": " x , y ,, z "}, "ORIGINS", ()) == ("x", "y", "z")
