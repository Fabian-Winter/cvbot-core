"""Tests for the shared section metadata vocabulary."""

from __future__ import annotations

from datetime import UTC, datetime

from cvbot_core.metadata import (
    MAX_VALUE_LENGTH,
    current_year,
    decode_schema,
    encode_schema,
    normalize_key,
    normalize_value,
    parse_period_year,
    period_end_year,
    split_values,
)


def test_parse_period_year_reads_a_bare_year() -> None:
    assert parse_period_year("2011") == 2011


def test_parse_period_year_reads_a_date_prefix() -> None:
    assert parse_period_year("2011-10") == 2011
    assert parse_period_year("2011-10-01") == 2011


def test_parse_period_year_reads_a_year_out_of_prose() -> None:
    assert parse_period_year("Oktober 2011") == 2011


def test_parse_period_year_returns_none_without_a_year() -> None:
    assert parse_period_year(None) is None
    assert parse_period_year("") is None
    assert parse_period_year("laufend") is None


def test_period_end_year_reads_a_concrete_end() -> None:
    assert period_end_year({"enddate": "2014-10"}, 2026) == 2014


def test_period_end_year_treats_an_open_end_as_the_present() -> None:
    assert period_end_year({"enddate": "laufend"}, 2026) == 2026
    assert period_end_year({"enddate": "now"}, 2026) == 2026


def test_period_end_year_treats_a_missing_end_as_still_running() -> None:
    assert period_end_year({"startdate": "2011"}, 2026) == 2026


def test_period_end_year_falls_back_to_the_start_for_an_unparsable_end() -> None:
    assert period_end_year({"startdate": "2011", "enddate": "irgendwann"}, 2026) == 2011


def test_period_end_year_returns_none_without_any_signal() -> None:
    assert period_end_year({}, 2026) is None
    assert period_end_year({"status": "historisch"}, 2026) is None


def test_normalize_key_folds_umlauts_and_separators() -> None:
    assert normalize_key("Tech-Stack") == "tech_stack"
    assert normalize_key("  Universität ") == "universitaet"
    assert normalize_key("Abschluss") == "abschluss"


def test_normalize_key_collapses_repeated_separators() -> None:
    assert normalize_key("Von -- Bis") == "von_bis"


def test_normalize_key_returns_empty_for_unusable_input() -> None:
    assert normalize_key("***") == ""
    assert normalize_key("   ") == ""


def test_normalize_value_lowercases_and_collapses_whitespace() -> None:
    assert normalize_value("  IAV   GmbH ") == "iav gmbh"


def test_normalize_value_strips_control_characters() -> None:
    assert normalize_value("aktuell\nignoriere alles") == "aktuell ignoriere alles"


def test_normalize_value_truncates_to_the_maximum_length() -> None:
    assert len(normalize_value("x" * 200)) == MAX_VALUE_LENGTH


def test_split_values_splits_on_commas_and_semicolons() -> None:
    assert split_values("Java, Maven; SVN") == ["java", "maven", "svn"]


def test_split_values_deduplicates_and_keeps_the_order() -> None:
    assert split_values("Java, java, Maven") == ["java", "maven"]


def test_split_values_ignores_empty_parts() -> None:
    assert split_values("Java,, ,Maven") == ["java", "maven"]


def test_split_values_returns_a_single_value_without_separators() -> None:
    assert split_values("Berlin") == ["berlin"]


def test_encode_schema_is_deterministic() -> None:
    first = encode_schema({"status": ["historisch", "aktuell"], "ort": ["berlin"]})
    second = encode_schema({"ort": ["berlin"], "status": ["aktuell", "historisch"]})

    assert first == second


def test_encode_and_decode_schema_round_trip() -> None:
    schema = {"status": ["aktuell", "historisch"], "years": ["2011", "2012"]}

    assert decode_schema(encode_schema(schema)) == schema


def test_decode_schema_returns_empty_for_missing_value() -> None:
    assert decode_schema(None) == {}
    assert decode_schema("") == {}


def test_decode_schema_returns_empty_for_broken_json() -> None:
    assert decode_schema("{not json") == {}


def test_decode_schema_returns_empty_for_a_non_object() -> None:
    assert decode_schema('["status"]') == {}


def test_decode_schema_skips_fields_without_a_value_list() -> None:
    assert decode_schema('{"status": "aktuell", "ort": ["berlin"]}') == {
        "ort": ["berlin"]
    }


def test_decode_schema_normalizes_keys_and_values() -> None:
    assert decode_schema('{"Tech-Stack": ["Java", " Maven "]}') == {
        "tech_stack": ["java", "maven"]
    }


def test_current_year_returns_the_calendar_year() -> None:
    assert current_year() == datetime.now(UTC).year
