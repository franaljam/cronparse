"""Tests for cronparse.cli_ranker."""

import argparse
import pytest
from cronparse.cli_ranker import add_ranker_subcommand, _cmd_rank


def make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_ranker_subcommand(sub)
    return p


def test_add_ranker_subcommand_registers_rank():
    p = make_parser()
    args = p.parse_args(["rank", "* * * * *"])
    assert hasattr(args, "func")


def test_rank_default_args():
    p = make_parser()
    args = p.parse_args(["rank", "* * * * *", "0 0 * * *"])
    assert args.expressions == ["* * * * *", "0 0 * * *"]
    assert args.labels is None
    assert args.reverse is False
    assert args.verbose is False


def test_rank_reverse_flag():
    p = make_parser()
    args = p.parse_args(["rank", "--reverse", "* * * * *"])
    assert args.reverse is True


def test_rank_labels_flag():
    p = make_parser()
    args = p.parse_args(["rank", "* * * * *", "0 0 * * *", "--labels", "all", "daily"])
    assert args.labels == ["all", "daily"]


def test_cmd_rank_prints_output(capsys):
    args = argparse.Namespace(
        expressions=["* * * * *", "0 0 * * *"],
        labels=None,
        reverse=False,
        verbose=False,
    )
    _cmd_rank(args)
    captured = capsys.readouterr()
    assert "[1]" in captured.out
    assert "[2]" in captured.out


def test_cmd_rank_verbose_output(capsys):
    args = argparse.Namespace(
        expressions=["* * * * *"],
        labels=None,
        reverse=False,
        verbose=True,
    )
    _cmd_rank(args)
    captured = capsys.readouterr()
    assert "runs/day" in captured.out


def test_cmd_rank_label_mismatch_prints_error(capsys):
    args = argparse.Namespace(
        expressions=["* * * * *", "0 * * * *"],
        labels=["only-one"],
        reverse=False,
        verbose=False,
    )
    _cmd_rank(args)
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_cmd_rank_with_labels(capsys):
    args = argparse.Namespace(
        expressions=["0 0 * * *"],
        labels=["midnight-job"],
        reverse=False,
        verbose=False,
    )
    _cmd_rank(args)
    captured = capsys.readouterr()
    assert "midnight-job" in captured.out
