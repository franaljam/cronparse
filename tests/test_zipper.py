"""Tests for cronparse.zipper."""
import pytest
from datetime import datetime, timezone

from cronparse.zipper import ZipEntry, ZipResult, zip_runs


@pytest.fixture
def anchor():
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def test_zip_returns_zip_result(anchor):
    result = zip_runs(["* * * * *", "0 * * * *"], anchor, n=3)
    assert isinstance(result, ZipResult)


def test_zip_empty_expressions_returns_empty(anchor):
    result = zip_runs([], anchor, n=5)
    assert result.count() == 0
    assert result.expressions == []


def test_zip_entry_count_equals_n(anchor):
    result = zip_runs(["* * * * *", "*/5 * * * *"], anchor, n=4)
    assert result.count() == 4


def test_zip_entries_are_zip_entry_instances(anchor):
    result = zip_runs(["* * * * *"], anchor, n=3)
    for entry in result.entries:
        assert isinstance(entry, ZipEntry)


def test_zip_entry_index_starts_at_one(anchor):
    result = zip_runs(["* * * * *"], anchor, n=3)
    assert result.entries[0].index == 1
    assert result.entries[1].index == 2
    assert result.entries[2].index == 3


def test_zip_entry_runs_length_matches_expressions(anchor):
    result = zip_runs(["* * * * *", "0 * * * *", "0 0 * * *"], anchor, n=3)
    for entry in result.entries:
        assert len(entry.runs) == 3


def test_zip_labels_default_generated(anchor):
    result = zip_runs(["* * * * *", "0 * * * *"], anchor, n=2)
    assert result.labels == ["expr1", "expr2"]


def test_zip_custom_labels(anchor):
    result = zip_runs(["* * * * *", "0 * * * *"], anchor, n=2, labels=["A", "B"])
    assert result.labels == ["A", "B"]
    for entry in result.entries:
        run_labels = [label for label, _ in entry.runs]
        assert "A" in run_labels
        assert "B" in run_labels


def test_zip_label_length_mismatch_raises(anchor):
    with pytest.raises(ValueError, match="labels length"):
        zip_runs(["* * * * *", "0 * * * *"], anchor, n=2, labels=["only_one"])


def test_zip_first_and_last(anchor):
    result = zip_runs(["* * * * *"], anchor, n=5)
    assert result.first() is not None
    assert result.last() is not None
    assert result.first().index == 1
    assert result.last().index == 5


def test_zip_first_returns_none_for_empty(anchor):
    result = zip_runs([], anchor, n=5)
    assert result.first() is None
    assert result.last() is None


def test_zip_every_minute_runs_are_datetimes(anchor):
    result = zip_runs(["* * * * *"], anchor, n=3)
    for entry in result.entries:
        for _, dt in entry.runs:
            assert isinstance(dt, datetime)


def test_zip_str_representation(anchor):
    result = zip_runs(["* * * * *", "0 * * * *"], anchor, n=2)
    s = str(result)
    assert "ZipResult" in s
    assert "2" in s


def test_zip_entry_str_representation(anchor):
    result = zip_runs(["* * * * *"], anchor, n=1)
    s = str(result.entries[0])
    assert "ZipEntry" in s
    assert "index=1" in s


def test_zip_stores_n(anchor):
    result = zip_runs(["* * * * *"], anchor, n=7)
    assert result.n == 7


def test_zip_single_expression(anchor):
    result = zip_runs(["0 9 * * 1"], anchor, n=3)
    assert result.count() == 3
    for entry in result.entries:
        assert len(entry.runs) == 1
