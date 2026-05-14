"""Tests for cronparse.cli_batcher."""

from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from cronparse.cli_batcher import add_batcher_subcommand, _cmd_batch


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    add_batcher_subcommand(sub)
    return p


def _make(args_str: str) -> argparse.Namespace:
    return make_parser().parse_args(args_str.split())


def test_add_batcher_subcommand_registers_batch():
    p = make_parser()
    ns = p.parse_args(["batch", "* * * * *"])
    assert hasattr(ns, "func")


def test_batch_default_windows():
    ns = _make("batch * * * * *")
    assert ns.windows == 6


def test_batch_custom_windows():
    ns = _make("batch * * * * * --windows 12")
    assert ns.windows == 12


def test_batch_default_minutes():
    ns = _make("batch * * * * *")
    assert ns.minutes == 60


def test_batch_custom_minutes():
    ns = _make("batch * * * * * --minutes 30")
    assert ns.minutes == 30


def test_batch_label_flag():
    ns = _make("batch 0 * * * * --label hourly")
    assert ns.label == "hourly"


def test_batch_label_default_none():
    ns = _make("batch * * * * *")
    assert ns.label is None


def test_batch_show_empty_default_false():
    ns = _make("batch * * * * *")
    assert ns.show_empty is False


def test_batch_show_empty_flag():
    ns = _make("batch * * * * * --show-empty")
    assert ns.show_empty is True


def test_cmd_batch_prints_output(capsys):
    ns = argparse.Namespace(
        expression="0 * * * *",
        windows=3,
        minutes=60,
        label=None,
        show_empty=False,
    )
    _cmd_batch(ns)
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out


def test_cmd_batch_show_empty_includes_empty_windows(capsys):
    ns = argparse.Namespace(
        expression="0 9 * * *",
        windows=3,
        minutes=60,
        label=None,
        show_empty=True,
    )
    _cmd_batch(ns)
    captured = capsys.readouterr()
    assert "(empty)" in captured.out or "run" in captured.out
