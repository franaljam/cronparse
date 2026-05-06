"""Tests for cronparse.predictor."""

import pytest
from datetime import datetime, timezone, timedelta

from cronparse.predictor import predict, predict_many, PredictionResult


UTC = timezone.utc


def dt(year, month, day, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


# ---------------------------------------------------------------------------
# predict()
# ---------------------------------------------------------------------------

def test_predict_returns_prediction_result():
    result = predict("* * * * *", dt(2024, 1, 1, 0, 0), dt(2024, 1, 1, 0, 5))
    assert isinstance(result, PredictionResult)


def test_predict_every_minute_fires_in_window():
    result = predict("* * * * *", dt(2024, 1, 1, 0, 0), dt(2024, 1, 1, 0, 4))
    assert result.fires is True
    assert result.count() == 5  # 0,1,2,3,4


def test_predict_specific_time_fires():
    result = predict("30 14 * * *", dt(2024, 6, 1, 14, 0), dt(2024, 6, 1, 15, 0))
    assert result.fires is True
    assert result.count() == 1
    assert result.first() == dt(2024, 6, 1, 14, 30)


def test_predict_specific_time_does_not_fire_outside_window():
    result = predict("30 14 * * *", dt(2024, 6, 1, 15, 0), dt(2024, 6, 1, 16, 0))
    assert result.fires is False
    assert result.count() == 0


def test_predict_first_and_last():
    result = predict("* * * * *", dt(2024, 1, 1, 0, 0), dt(2024, 1, 1, 0, 3))
    assert result.first() == dt(2024, 1, 1, 0, 0)
    assert result.last() == dt(2024, 1, 1, 0, 3)


def test_predict_first_none_when_no_fires():
    result = predict("30 23 * * *", dt(2024, 1, 1, 0, 0), dt(2024, 1, 1, 0, 5))
    assert result.first() is None
    assert result.last() is None


def test_predict_label_stored():
    result = predict("0 * * * *", dt(2024, 1, 1), dt(2024, 1, 1, 3), label="hourly")
    assert result.label == "hourly"


def test_predict_str_with_fires():
    result = predict("0 12 * * *", dt(2024, 1, 1, 11), dt(2024, 1, 1, 13))
    assert "fires" in str(result)
    assert "0 12 * * *" in str(result)


def test_predict_str_no_fires():
    result = predict("0 12 * * *", dt(2024, 1, 1, 13), dt(2024, 1, 1, 14))
    assert "does not fire" in str(result)


def test_predict_invalid_window_raises():
    with pytest.raises(ValueError, match="window_end must be after"):
        predict("* * * * *", dt(2024, 1, 1, 1), dt(2024, 1, 1, 0))


def test_predict_step_expression():
    # */15 fires at :00, :15, :30, :45 each hour
    result = predict("*/15 * * * *", dt(2024, 1, 1, 0, 0), dt(2024, 1, 1, 0, 59))
    assert result.count() == 4


# ---------------------------------------------------------------------------
# predict_many()
# ---------------------------------------------------------------------------

def test_predict_many_returns_list():
    results = predict_many(
        ["* * * * *", "0 * * * *"],
        dt(2024, 1, 1, 0, 0),
        dt(2024, 1, 1, 0, 5),
    )
    assert isinstance(results, list)
    assert len(results) == 2


def test_predict_many_with_labels():
    results = predict_many(
        ["* * * * *", "0 * * * *"],
        dt(2024, 1, 1, 0, 0),
        dt(2024, 1, 1, 1, 0),
        labels=["every-min", "every-hour"],
    )
    assert results[0].label == "every-min"
    assert results[1].label == "every-hour"


def test_predict_many_label_length_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        predict_many(
            ["* * * * *", "0 * * * *"],
            dt(2024, 1, 1),
            dt(2024, 1, 1, 1),
            labels=["only-one"],
        )
