"""Tests for cronparse.cloner."""

import pytest
from cronparse.cloner import CloneResult, clone


def test_clone_returns_clone_result():
    result = clone("0 9 * * 1")
    assert isinstance(result, CloneResult)


def test_clone_stores_original_expression():
    result = clone("0 9 * * 1")
    assert result.original == "0 9 * * 1"


def test_clone_no_substitutions_cloned_matches_original():
    result = clone("0 9 * * 1")
    assert result.cloned == "0 9 * * 1"


def test_clone_no_substitutions_empty_dict():
    result = clone("* * * * *")
    assert result.substitutions == {}


def test_clone_was_modified_false_when_no_changes():
    result = clone("0 9 * * *")
    assert result.was_modified is False


def test_clone_substitute_minute():
    result = clone("0 9 * * *", minute="30")
    assert result.cloned == "30 9 * * *"


def test_clone_substitute_hour():
    result = clone("0 9 * * *", hour="12")
    assert result.cloned == "0 12 * * *"


def test_clone_substitute_dom():
    result = clone("0 9 * * *", dom="15")
    assert result.cloned == "0 9 15 * *"


def test_clone_substitute_month():
    result = clone("0 9 * * *", month="6")
    assert result.cloned == "0 9 * 6 *"


def test_clone_substitute_dow():
    result = clone("0 9 * * *", dow="5")
    assert result.cloned == "0 9 * * 5"


def test_clone_multiple_substitutions():
    result = clone("0 9 * * 1", minute="15", hour="10", dow="5")
    assert result.cloned == "15 10 * * 5"


def test_clone_substitutions_dict_records_changes():
    result = clone("0 9 * * *", minute="30", hour="12")
    assert result.substitutions == {"minute": "30", "hour": "12"}


def test_clone_same_value_not_recorded_as_substitution():
    result = clone("0 9 * * *", minute="0")
    assert "minute" not in result.substitutions


def test_clone_was_modified_true_when_changed():
    result = clone("0 9 * * *", hour="10")
    assert result.was_modified is True


def test_clone_changed_fields_returns_list():
    result = clone("0 9 * * *", minute="5", dow="1")
    assert set(result.changed_fields) == {"minute", "dow"}


def test_clone_label_none_by_default():
    result = clone("* * * * *")
    assert result.label is None


def test_clone_label_propagated():
    result = clone("* * * * *", label="my-job")
    assert result.label == "my-job"


def test_clone_str_contains_original_and_cloned():
    result = clone("0 9 * * *", hour="10")
    s = str(result)
    assert "0 9 * * *" in s
    assert "0 10 * * *" in s


def test_clone_str_contains_label_when_set():
    result = clone("0 9 * * *", label="test")
    assert "test" in str(result)


def test_clone_result_is_valid_parseable_expression():
    from cronparse.parser import parse
    result = clone("*/5 * * * *", hour="9-17")
    parsed = parse(result.cloned)
    assert parsed is not None


def test_clone_wildcard_to_step():
    result = clone("* * * * *", minute="*/15")
    assert result.cloned == "*/15 * * * *"
    assert result.substitutions == {"minute": "*/15"}
