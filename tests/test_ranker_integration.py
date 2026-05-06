"""Integration tests for ranker with alias and humanizer."""

from cronparse.ranker import rank
from cronparse.alias_integration import parse_with_alias
from cronparse.humanizer import humanize


def test_rank_preserves_expression_strings():
    exprs = ["*/5 * * * *", "0 9-17 * * 1-5", "0 0 1 * *"]
    result = rank(exprs)
    returned_exprs = [r.expression for r in result]
    for e in exprs:
        assert e in returned_exprs


def test_rank_single_expression():
    result = rank(["30 6 * * *"])
    assert len(result) == 1
    assert result[0].rank == 1


def test_rank_step_expression_more_frequent_than_daily():
    result = rank(["0 0 * * *", "*/15 * * * *"])
    # */15 fires 4*24=96 times/day; daily fires once
    assert result[0].expression == "*/15 * * * *"


def test_ranked_expression_can_be_humanized():
    result = rank(["0 9 * * 1-5"])
    expr_str = result[0].expression
    from cronparse.parser import parse
    expr = parse(expr_str)
    desc = humanize(expr)
    assert isinstance(desc, str)
    assert len(desc) > 0


def test_rank_with_all_wildcards_has_zero_specificity():
    from cronparse.ranker import _specificity
    from cronparse.parser import parse
    expr = parse("* * * * *")
    assert _specificity(expr) == 0


def test_rank_tiebreak_by_specificity():
    # Both fire once per day but one is more specific
    exprs = ["0 0 * * *", "0 0 1 1 *"]
    result = rank(exprs)
    # more specific (0 0 1 1 *) should rank lower (less frequent)
    freq_first = result[0]
    # same runs_per_day=1, but 0 0 * * * has lower specificity so sorted after in desc
    # with reverse=False (most frequent first), ties broken by -specificity ascending
    # meaning higher specificity comes first among ties
    assert freq_first.expression == "0 0 1 1 *"
