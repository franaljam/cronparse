"""Tests for cronparse.cli_predictor."""

import argparse
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from cronparse.cli_predictor import add_predictor_subcommand, _cmd_predict
from cronparse.predictor import PredictionResult


def make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_predictor_subcommand(sub)
    return parser


def test_add_predictor_subcommand_registers_predict():
    parser = make_parser()
    args = parser.parse_args(["predict", "* * * * *"])
    assert hasattr(args, "func")


def test_predict_default_args_parsed():
    parser = make_parser()
    args = parser.parse_args(["predict", "0 * * * *"])
    assert args.expression == "0 * * * *"
    assert args.hours == 24.0
    assert args.start is None
    assert args.label is None


def test_predict_custom_hours():
    parser = make_parser()
    args = parser.parse_args(["predict", "* * * * *", "--hours", "1"])
    assert args.hours == 1.0


def test_predict_label_flag():
    parser = make_parser()
    args = parser.parse_args(["predict", "* * * * *", "--label", "test"])
    assert args.label == "test"


def test_cmd_predict_prints_output(capsys):
    start = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    fake_result = PredictionResult(
        expression="0 * * * *",
        window_start=start,
        window_end=start,
        fires=True,
        occurrences=[start],
    )
    args = argparse.Namespace(
        expression="0 * * * *",
        start=None,
        hours=1.0,
        label=None,
    )
    with patch("cronparse.cli_predictor.predict", return_value=fake_result):
        _cmd_predict(args)
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out


def test_cmd_predict_invalid_start_prints_error(capsys):
    args = argparse.Namespace(
        expression="* * * * *",
        start="not-a-date",
        hours=1.0,
        label=None,
    )
    _cmd_predict(args)
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_cmd_predict_no_fires_shows_message(capsys):
    start = datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc)
    from datetime import timedelta
    end = start + timedelta(hours=1)
    fake_result = PredictionResult(
        expression="0 12 * * *",
        window_start=start,
        window_end=end,
        fires=False,
        occurrences=[],
    )
    args = argparse.Namespace(
        expression="0 12 * * *",
        start=None,
        hours=1.0,
        label=None,
    )
    with patch("cronparse.cli_predictor.predict", return_value=fake_result):
        _cmd_predict(args)
    captured = capsys.readouterr()
    assert "does not fire" in captured.out
