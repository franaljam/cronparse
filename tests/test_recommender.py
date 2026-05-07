"""Tests for cronparse.recommender."""

import pytest
from cronparse.recommender import recommend, Recommendation, RecommendationResult


def test_recommend_returns_recommendation_result():
    result = recommend("every hour")
    assert isinstance(result, RecommendationResult)


def test_recommend_every_hour():
    result = recommend("every hour")
    assert result.best is not None
    assert result.best.expression == "0 * * * *"


def test_recommend_daily():
    result = recommend("daily")
    assert result.best is not None
    assert result.best.expression == "0 0 * * *"


def test_recommend_every_minute():
    result = recommend("every minute")
    assert result.best is not None
    assert result.best.expression == "* * * * *"


def test_recommend_no_match_returns_empty():
    result = recommend("run on a blue moon")
    assert len(result) == 0
    assert result.best is None


def test_recommend_best_is_first_recommendation():
    result = recommend("every 5 minutes")
    assert result.best is result.recommendations[0]


def test_recommend_human_is_string():
    result = recommend("every day")
    assert isinstance(result.best.human, str)
    assert len(result.best.human) > 0


def test_recommend_max_results_respected():
    # A broad query that matches many entries
    result = recommend("every", max_results=3)
    assert len(result) <= 3


def test_recommend_no_duplicates():
    result = recommend("every day daily", max_results=10)
    exprs = [r.expression for r in result.recommendations]
    assert len(exprs) == len(set(exprs))


def test_recommendation_str():
    result = recommend("every hour")
    text = str(result.best)
    assert "0 * * * *" in text


def test_recommendation_result_str_with_results():
    result = recommend("every hour")
    text = str(result)
    assert "every hour" in text
    assert "0 * * * *" in text


def test_recommendation_result_str_no_results():
    result = recommend("xyzzy impossible query")
    text = str(result)
    assert "No recommendations" in text


def test_recommend_weekday():
    result = recommend("every weekday")
    assert result.best.expression == "0 9 * * 1-5"


def test_recommend_monthly():
    result = recommend("monthly")
    assert result.best.expression == "0 0 1 * *"


def test_recommend_description_is_string():
    result = recommend("midnight")
    assert isinstance(result.best.description, str)
