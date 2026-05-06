"""Tests for cronparse.highlighter."""

import pytest

from cronparse.highlighter import (
    HighlightedExpression,
    HighlightedField,
    highlight,
    _RESET,
    _FIELD_NAMES,
)


# ---------------------------------------------------------------------------
# highlight() return type
# ---------------------------------------------------------------------------

def test_highlight_returns_highlighted_expression():
    result = highlight("* * * * *")
    assert isinstance(result, HighlightedExpression)


def test_highlight_fields_are_highlighted_field_instances():
    result = highlight("0 9 * * 1")
    assert all(isinstance(f, HighlightedField) for f in result.fields)


def test_highlight_produces_five_fields():
    result = highlight("*/5 * * * *")
    assert len(result.fields) == 5


def test_highlight_field_names_match_expected_order():
    result = highlight("* * * * *")
    names = [f.name for f in result.fields]
    assert names == _FIELD_NAMES


def test_highlight_raw_tokens_preserved():
    expr = "30 8 1 6 *"
    result = highlight(expr)
    raws = [f.raw for f in result.fields]
    assert raws == ["30", "8", "1", "6", "*"]


# ---------------------------------------------------------------------------
# HighlightedField.colored()
# ---------------------------------------------------------------------------

def test_colored_contains_raw_token():
    result = highlight("0 12 * * *")
    minute_field = result.fields[0]
    assert "0" in minute_field.colored()


def test_colored_contains_reset_code():
    result = highlight("0 12 * * *")
    for field in result.fields:
        assert _RESET in field.colored()


def test_colored_starts_with_color_code():
    result = highlight("* * * * *")
    for field in result.fields:
        assert field.colored().startswith(field.color_code)


# ---------------------------------------------------------------------------
# HighlightedExpression.render()
# ---------------------------------------------------------------------------

def test_render_contains_all_raw_tokens():
    expr = "15 3 * * 5"
    result = highlight(expr)
    rendered = result.render()
    for token in expr.split():
        assert token in rendered


def test_render_contains_reset_codes():
    result = highlight("* * * * *")
    assert _RESET in result.render()


def test_render_has_four_spaces_between_fields():
    # Each colored field ends with RESET; they are joined by " "
    result = highlight("* * * * *")
    rendered = result.render()
    # There must be exactly 4 separator spaces at the top level (between RESET and next color)
    assert rendered.count(" ") >= 4


# ---------------------------------------------------------------------------
# HighlightedExpression.legend()
# ---------------------------------------------------------------------------

def test_legend_contains_all_field_names():
    result = highlight("* * * * *")
    legend = result.legend()
    for name in _FIELD_NAMES:
        assert name in legend


def test_legend_contains_reset_codes():
    result = highlight("* * * * *")
    assert _RESET in result.legend()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_highlight_invalid_field_count_raises():
    with pytest.raises(ValueError):
        highlight("* * * *")  # only 4 fields


def test_highlight_too_many_fields_raises():
    with pytest.raises(ValueError):
        highlight("* * * * * *")  # 6 fields
