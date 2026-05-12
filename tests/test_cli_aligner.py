"""Tests for cronparse.cli_aligner."""
import argparse
from datetime import datetime
from unittest.mock import patch

import pytest

from cronparse.cli_aligner import add_aligner_subcommand, _cmd_align


@pytest.fixture
def make_parser():
    def _make():
        p = argparse.ArgumentParser()
        sub = p.add_subparsers()
        add_aligner_subcommand(sub)
        return p
    return _make


def test_add_aligner_subcommand_registers_align(make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *"])
    assert hasattr(args, "func")


def test_align_default_labels_is_none(make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *"])
    assert args.labels is None


def test_align_custom_labels(make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *", "--labels", "job-a"])
    assert args.labels == ["job-a"]


def test_align_multiple_expressions(make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *", "0 * * * *"])
    assert len(args.expressions) == 2


def test_align_at_flag_parsed(make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *", "--at", "2024-01-15T12:00:00"])
    assert args.at == "2024-01-15T12:00:00"


def test_cmd_align_prints_output(capsys, make_parser):
    p = make_parser()
    args = p.parse_args(
        ["align", "* * * * *", "--at", "2024-01-15T12:00:00"]
    )
    args.func(args)
    captured = capsys.readouterr()
    assert "Reference" in captured.out
    assert "Aligned" in captured.out


def test_cmd_align_shows_expression(capsys, make_parser):
    p = make_parser()
    args = p.parse_args(
        ["align", "* * * * *", "--at", "2024-01-15T12:00:00"]
    )
    args.func(args)
    captured = capsys.readouterr()
    assert "* * * * *" in captured.out


def test_cmd_align_uses_now_when_no_at(capsys, make_parser):
    p = make_parser()
    args = p.parse_args(["align", "* * * * *"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Reference" in captured.out
