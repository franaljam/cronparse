"""CLI subcommand for the rewinder module."""

from __future__ import annotations

import argparse
from datetime import datetime

from cronparse.rewinder import rewind


def add_rewinder_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "rewind",
        help="Show the most recent past run times for a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression (quoted)")
    parser.add_argument(
        "-n",
        type=int,
        default=5,
        dest="count",
        help="Number of past runs to show (default: 5)",
    )
    parser.add_argument(
        "--before",
        default=None,
        help="Anchor datetime in ISO format (default: now)",
    )
    parser.add_argument("--label", default=None, help="Optional label for the expression")
    parser.set_defaults(func=_cmd_rewind)


def _cmd_rewind(args: argparse.Namespace) -> None:
    before: datetime | None = None
    if args.before:
        before = datetime.fromisoformat(args.before)

    result = rewind(
        args.expression,
        before=before,
        n=args.count,
        label=args.label,
    )

    label_part = f" ({result.label})" if result.label else ""
    print(f"Past {result.count} runs for: {result.expression}{label_part}")
    for run in result.runs:
        print(f"  {run.isoformat(sep=' ')}")
