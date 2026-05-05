"""CLI subcommand: summarize one or more cron expressions."""

import argparse
import json
from typing import List

from .summarizer import summarize_many, report


def add_summarize_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'summarize' subcommand on *subparsers*."""
    parser = subparsers.add_parser(
        "summarize",
        help="Summarize one or more cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expression(s) to summarize.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output summaries as JSON.",
    )
    parser.set_defaults(func=_cmd_summarize)


def _cmd_summarize(args: argparse.Namespace) -> int:
    """Handle the 'summarize' subcommand."""
    summaries = summarize_many(args.expressions)

    if args.as_json:
        data = [s.to_dict() for s in summaries]
        print(json.dumps(data, indent=2))
        return 0

    print(report(args.expressions))

    # Exit with non-zero if any expression is invalid.
    if any(not s.valid for s in summaries):
        return 1
    return 0
