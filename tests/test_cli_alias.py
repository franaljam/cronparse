"""Tests for cronparse.cli_alias."""

import argparse
import pytest
from cronparse.cli_alias import add_alias_subcommand, _cmd_alias


def make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_alias_subcommand(sub)
    return parser


def test_add_alias_subcommand_registers_alias():
    parser = make_parser()
    args = parser.parse_args(["alias", "list"])
    assert args.command == "alias"


def test_alias_list_sets_func():
    parser = make_parser()
    args = parser.parse_args(["alias", "list"])
    assert callable(args.func)


def test_alias_resolve_sets_expression():
    parser = make_parser()
    args = parser.parse_args(["alias", "resolve", "@daily"])
    assert args.expression == "@daily"


def test_cmd_alias_resolve_prints_output(capsys):
    parser = make_parser()
    args = parser.parse_args(["alias", "resolve", "@daily"])
    _cmd_alias(args)
    captured = capsys.readouterr()
    assert "@daily" in captured.out
    assert "0 0 * * *" in captured.out


def test_cmd_alias_resolve_plain_expression(capsys):
    parser = make_parser()
    args = parser.parse_args(["alias", "resolve", "0 0 * * *"])
    _cmd_alias(args)
    captured = capsys.readouterr()
    assert "unchanged" in captured.out


def test_cmd_alias_resolve_unknown_raises(capsys):
    parser = make_parser()
    args = parser.parse_args(["alias", "resolve", "@reboot"])
    with pytest.raises(SystemExit):
        _cmd_alias(args)
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_cmd_alias_list_prints_table(capsys):
    parser = make_parser()
    args = parser.parse_args(["alias", "list"])
    _cmd_alias(args)
    captured = capsys.readouterr()
    assert "@daily" in captured.out
    assert "@hourly" in captured.out
    assert "Alias" in captured.out
