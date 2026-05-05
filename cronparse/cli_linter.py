"""CLI subcommand for the cron expression linter."""

from __future__ import annotations

import argparse
from cronparse.linter import lint


def add_lint_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'lint' subcommand on *subparsers*."""
    parser = subparsers.add_parser(
        "lint",
        help="Lint a cron expression for suspicious or non-portable patterns.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to lint (quote it to avoid shell expansion).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any warnings are found.",
    )
    parser.set_defaults(func=_cmd_lint)


def _cmd_lint(args: argparse.Namespace) -> int:
    """Execute the lint command; returns an exit code."""
    result = lint(args.expression)
    print(result.summary())
    if args.strict and not result.clean:
        return 1
    return 0
