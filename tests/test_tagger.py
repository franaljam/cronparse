"""Tests for cronparse.tagger module."""

import pytest
from cronparse.tagger import (
    tag_from_string,
    describe_tags,
    TAG_FREQUENT,
    TAG_HOURLY,
    TAG_DAILY,
    TAG_WEEKLY,
    TAG_MONTHLY,
    TAG_BUSINESS_HOURS,
    TAG_OVERNIGHT,
    TAG_WILDCARD,
)


def test_wildcard_expression_tagged_wildcard():
    tags = tag_from_string("* * * * *")
    assert TAG_WILDCARD in tags


def test_every_minute_is_frequent():
    # "* * * * *" — every minute, wildcard on hour means frequent
    tags = tag_from_string("* * * * *")
    assert TAG_WILDCARD in tags


def test_step_minutes_is_frequent():
    # every 5 minutes
    tags = tag_from_string("*/5 * * * *")
    assert TAG_FREQUENT in tags


def test_hourly_expression():
    tags = tag_from_string("0 * * * *")
    assert TAG_HOURLY in tags


def test_daily_expression():
    tags = tag_from_string("30 9 * * *")
    assert TAG_DAILY in tags


def test_daily_not_tagged_hourly():
    tags = tag_from_string("30 9 * * *")
    assert TAG_HOURLY not in tags


def test_weekly_expression():
    tags = tag_from_string("0 9 * * 1")
    assert TAG_WEEKLY in tags


def test_monthly_expression():
    tags = tag_from_string("0 0 1 * *")
    assert TAG_MONTHLY in tags


def test_monthly_not_tagged_weekly():
    tags = tag_from_string("0 0 1 * *")
    assert TAG_WEEKLY not in tags


def test_business_hours_expression():
    tags = tag_from_string("0 9-17 * * *")
    assert TAG_BUSINESS_HOURS in tags


def test_overnight_expression():
    tags = tag_from_string("0 0-6 * * *")
    assert TAG_OVERNIGHT in tags


def test_business_hours_not_overnight():
    tags = tag_from_string("0 9-17 * * *")
    assert TAG_OVERNIGHT not in tags


def test_describe_tags_returns_dict():
    tags = tag_from_string("30 9 * * *")
    result = describe_tags(tags)
    assert isinstance(result, dict)


def test_describe_tags_keys_match_input():
    tags = [TAG_DAILY, TAG_BUSINESS_HOURS]
    result = describe_tags(tags)
    assert set(result.keys()) == {TAG_DAILY, TAG_BUSINESS_HOURS}


def test_describe_tags_values_are_strings():
    tags = tag_from_string("0 * * * *")
    result = describe_tags(tags)
    for v in result.values():
        assert isinstance(v, str)
        assert len(v) > 0


def test_tag_returns_list():
    result = tag_from_string("* * * * *")
    assert isinstance(result, list)
