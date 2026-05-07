"""Tests for cronparse.cli_heatmap."""

import argparse
from unittest.mock import patch, MagicMock

import pytest

from cronparse.cli_heatmap import add_heatmap_subcommand, _cmd_heatmap


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_heatmap_subcommand(sub)
    return p


def test_add_heatmap_subcommand_registers_heatmap():
    p = make_parser()
    args = p.parse_args(["heatmap", "* * * * *"])
    assert hasattr(args, "func")


def test_heatmap_default_days():
    p = make_parser()
    args = p.parse_args(["heatmap", "0 * * * *"])
    assert args.days == 7


def test_heatmap_custom_days():
    p = make_parser()
    args = p.parse_args(["heatmap", "0 * * * *", "--days", "14"])
    assert args.days == 14


def test_heatmap_label_flag():
    p = make_parser()
    args = p.parse_args(["heatmap", "0 * * * *", "--label", "hourly"])
    assert args.label == "hourly"


def test_heatmap_label_default_none():
    p = make_parser()
    args = p.parse_args(["heatmap", "0 * * * *"])
    assert args.label is None


def test_cmd_heatmap_prints_output(capsys):
    p = make_parser()
    args = p.parse_args(["heatmap", "0 12 * * *", "--days", "7"])
    args.func(args)
    captured = capsys.readouterr()
    assert "0 12 * * *" in captured.out


def test_cmd_heatmap_prints_day_labels(capsys):
    p = make_parser()
    args = p.parse_args(["heatmap", "0 * * * *", "--days", "1"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Mon" in captured.out
    assert "Sun" in captured.out


def test_cmd_heatmap_prints_peak(capsys):
    p = make_parser()
    args = p.parse_args(["heatmap", "* * * * *", "--days", "1"])
    args.func(args)
    captured = capsys.readouterr()
    assert "Peak" in captured.out
