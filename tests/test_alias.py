"""Tests for cronparse.alias."""

import pytest
from cronparse.alias import (
    AliasError,
    describe_alias,
    is_alias,
    list_aliases,
    resolve,
)


def test_is_alias_known():
    assert is_alias("@daily") is True


def test_is_alias_case_insensitive():
    assert is_alias("@DAILY") is True


def test_is_alias_unknown_at_prefix():
    assert is_alias("@unknown") is False


def test_is_alias_plain_expression():
    assert is_alias("0 0 * * *") is False


def test_resolve_daily():
    assert resolve("@daily") == "0 0 * * *"


def test_resolve_midnight_equals_daily():
    assert resolve("@midnight") == resolve("@daily")


def test_resolve_annually_equals_yearly():
    assert resolve("@annually") == resolve("@yearly")


def test_resolve_hourly():
    assert resolve("@hourly") == "0 * * * *"


def test_resolve_weekly():
    assert resolve("@weekly") == "0 0 * * 0"


def test_resolve_monthly():
    assert resolve("@monthly") == "0 0 1 * *"


def test_resolve_case_insensitive():
    assert resolve("@HOURLY") == "0 * * * *"


def test_resolve_plain_expression_unchanged():
    expr = "15 3 * * 1-5"
    assert resolve(expr) == expr


def test_resolve_unknown_alias_raises():
    with pytest.raises(AliasError, match="Unknown alias"):
        resolve("@reboot")


def test_list_aliases_returns_dict():
    aliases = list_aliases()
    assert isinstance(aliases, dict)
    assert "@daily" in aliases


def test_list_aliases_is_copy():
    aliases = list_aliases()
    aliases["@fake"] = "0 0 0 0 0"
    assert "@fake" not in list_aliases()


def test_describe_alias_known():
    assert describe_alias("@yearly") == "0 0 1 1 *"


def test_describe_alias_unknown_returns_none():
    assert describe_alias("@reboot") is None


def test_workday_alias():
    assert resolve("@workday") == "0 9 * * 1-5"


def test_weekend_alias():
    assert resolve("@weekend") == "0 10 * * 6,0"
