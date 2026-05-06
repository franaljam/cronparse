"""Tests for cronparse.grouper module."""

import pytest

from cronparse.grouper import (
    ExpressionGroup,
    GroupEntry,
    group_by_hour_pattern,
    group_by_tag,
)


EVERY_MINUTE = "* * * * *"
EVERY_HOUR = "0 * * * *"
DAILY_MIDNIGHT = "0 0 * * *"
DAILY_NOON = "0 12 * * *"
STEP_EXPR = "*/5 * * * *"


def test_group_by_tag_returns_dict():
    result = group_by_tag([EVERY_MINUTE, DAILY_MIDNIGHT])
    assert isinstance(result, dict)


def test_group_by_tag_keys_are_strings():
    result = group_by_tag([EVERY_MINUTE, EVERY_HOUR, DAILY_MIDNIGHT])
    for key in result:
        assert isinstance(key, str)


def test_group_by_tag_values_are_expression_groups():
    result = group_by_tag([EVERY_MINUTE, DAILY_MIDNIGHT])
    for group in result.values():
        assert isinstance(group, ExpressionGroup)


def test_group_by_tag_entries_are_group_entries():
    result = group_by_tag([EVERY_MINUTE])
    for group in result.values():
        for entry in group.entries:
            assert isinstance(entry, GroupEntry)


def test_group_by_tag_frequent_expressions_grouped_together():
    result = group_by_tag([EVERY_MINUTE, STEP_EXPR])
    assert "frequent" in result
    assert len(result["frequent"]) == 2


def test_group_by_tag_with_labels():
    result = group_by_tag([EVERY_MINUTE, DAILY_MIDNIGHT], labels=["a", "b"])
    all_entries = [e for g in result.values() for e in g.entries]
    label_set = {e.label for e in all_entries}
    assert "a" in label_set
    assert "b" in label_set


def test_group_by_tag_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        group_by_tag([EVERY_MINUTE, DAILY_MIDNIGHT], labels=["only-one"])


def test_group_by_tag_no_labels_defaults_none():
    result = group_by_tag([EVERY_MINUTE])
    for group in result.values():
        for entry in group.entries:
            assert entry.label is None


def test_expression_group_expressions_property():
    result = group_by_tag([EVERY_MINUTE, STEP_EXPR])
    frequent = result.get("frequent")
    assert frequent is not None
    assert EVERY_MINUTE in frequent.expressions
    assert STEP_EXPR in frequent.expressions


def test_expression_group_len():
    result = group_by_tag([EVERY_MINUTE, STEP_EXPR])
    frequent = result["frequent"]
    assert len(frequent) == 2


def test_expression_group_str():
    group = ExpressionGroup(key="daily")
    assert "daily" in str(group)


def test_group_entry_str_uses_label():
    from cronparse.parser import parse
    parsed = parse(EVERY_MINUTE)
    entry = GroupEntry(expression=EVERY_MINUTE, label="my-job", parsed=parsed)
    assert "my-job" in str(entry)


def test_group_by_hour_pattern_returns_dict():
    result = group_by_hour_pattern([EVERY_HOUR, DAILY_MIDNIGHT, DAILY_NOON])
    assert isinstance(result, dict)


def test_group_by_hour_pattern_every_hour_key():
    result = group_by_hour_pattern([EVERY_MINUTE, EVERY_HOUR])
    assert "every-hour" in result


def test_group_by_hour_pattern_specific_hours_separate():
    result = group_by_hour_pattern([DAILY_MIDNIGHT, DAILY_NOON])
    keys = list(result.keys())
    assert len(keys) == 2


def test_group_by_hour_pattern_label_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        group_by_hour_pattern([EVERY_HOUR, DAILY_MIDNIGHT], labels=["x"])
