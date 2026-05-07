"""Tests for cronparse.cli_recommender."""

import argparse
import pytest
from cronparse.cli_recommender import add_recommender_subcommand, _cmd_recommend


def make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_recommender_subcommand(sub)
    return p


def test_add_recommender_subcommand_registers_recommend():
    p = make_parser()
    args = p.parse_args(["recommend", "every hour"])
    assert hasattr(args, "func")
    assert args.func is _cmd_recommend


def test_recommend_default_max_results():
    p = make_parser()
    args = p.parse_args(["recommend", "every hour"])
    assert args.max_results == 5


def test_recommend_custom_max():
    p = make_parser()
    args = p.parse_args(["recommend", "every hour", "--max", "2"])
    assert args.max_results == 2


def test_recommend_best_flag():
    p = make_parser()
    args = p.parse_args(["recommend", "daily", "--best"])
    assert args.best is True


def test_recommend_best_flag_default_false():
    p = make_parser()
    args = p.parse_args(["recommend", "daily"])
    assert args.best is False


def test_cmd_recommend_prints_output(capsys):
    p = make_parser()
    args = p.parse_args(["recommend", "every hour"])
    _cmd_recommend(args)
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_cmd_recommend_best_prints_single(capsys):
    p = make_parser()
    args = p.parse_args(["recommend", "every hour", "--best"])
    _cmd_recommend(args)
    out = capsys.readouterr().out
    assert "Expression" in out
    assert "Human" in out


def test_cmd_recommend_no_match_prints_message(capsys):
    p = make_parser()
    args = p.parse_args(["recommend", "xyzzy impossible"])
    _cmd_recommend(args)
    out = capsys.readouterr().out
    assert "No recommendations" in out


def test_cmd_recommend_query_stored():
    p = make_parser()
    args = p.parse_args(["recommend", "midnight"])
    assert args.query == "midnight"
