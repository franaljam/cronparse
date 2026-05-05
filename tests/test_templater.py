"""Tests for cronparse.templater module."""

import pytest
from cronparse.templater import (
    list_templates,
    get_template,
    resolve_template,
    describe_template,
    register_template,
    TemplateError,
)
from cronparse.parser import CronExpression


def test_list_templates_returns_list():
    result = list_templates()
    assert isinstance(result, list)
    assert len(result) > 0


def test_list_templates_includes_known_names():
    result = list_templates()
    assert "every_minute" in result
    assert "daily_midnight" in result
    assert "weekly_sunday" in result


def test_list_templates_filter_by_tag():
    daily = list_templates(tag="daily")
    assert "daily_midnight" in daily
    assert "daily_noon" in daily
    assert "every_minute" not in daily


def test_list_templates_unknown_tag_returns_empty():
    result = list_templates(tag="nonexistent_tag")
    assert result == []


def test_get_template_returns_dict():
    meta = get_template("every_hour")
    assert isinstance(meta, dict)
    assert "expression" in meta
    assert "description" in meta
    assert "tags" in meta


def test_get_template_correct_expression():
    meta = get_template("daily_midnight")
    assert meta["expression"] == "0 0 * * *"


def test_get_template_unknown_raises():
    with pytest.raises(TemplateError, match="Unknown template"):
        get_template("does_not_exist")


def test_get_template_returns_copy():
    meta1 = get_template("every_minute")
    meta1["expression"] = "mutated"
    meta2 = get_template("every_minute")
    assert meta2["expression"] == "* * * * *"


def test_resolve_template_returns_cron_expression():
    expr = resolve_template("every_hour")
    assert isinstance(expr, CronExpression)


def test_resolve_template_every_minute_all_values():
    expr = resolve_template("every_minute")
    assert len(expr.minute) == 60


def test_resolve_template_weekdays_9am():
    expr = resolve_template("weekdays_9am")
    assert 9 in expr.hour
    assert set(expr.weekday) == {1, 2, 3, 4, 5}


def test_resolve_template_unknown_raises():
    with pytest.raises(TemplateError):
        resolve_template("ghost_template")


def test_describe_template_contains_name_and_expression():
    desc = describe_template("monthly_first")
    assert "monthly_first" in desc
    assert "0 0 1 * *" in desc


def test_register_template_adds_to_list():
    register_template("custom_test", "30 8 * * 1", "Monday 8:30 AM", tags=["custom"])
    assert "custom_test" in list_templates()


def test_register_template_resolvable():
    register_template("custom_test2", "0 3 * * 5", "Friday 3 AM")
    expr = resolve_template("custom_test2")
    assert isinstance(expr, CronExpression)
    assert 3 in expr.hour


def test_register_template_invalid_name_raises():
    with pytest.raises(TemplateError, match="valid identifier"):
        register_template("bad name!", "* * * * *")


def test_register_template_invalid_expression_raises():
    with pytest.raises(Exception):
        register_template("bad_expr", "99 99 99 99 99")
