"""CLI subcommand for run history inspection."""

import argparse
from datetime import datetime, timezone

from cronparse.history import build_history, filter_history


def add_history_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'history' subcommand."""
    p = subparsers.add_parser(
        "history",
        help="Show historical scheduled runs for a cron expression",
    )
    p.add_argument("expression", help="Cron expression (quoted)")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=10,
        help="Number of past runs to generate (default: 10)",
    )
    p.add_argument(
        "--start",
        default=None,
        help="Start datetime in ISO format (default: now UTC)",
    )
    p.add_argument(
        "--after",
        default=None,
        help="Filter: only show runs at or after this ISO datetime",
    )
    p.add_argument(
        "--before",
        default=None,
        help="Filter: only show runs at or before this ISO datetime",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional label to attach to each run record",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary instead of individual records",
    )
    p.set_defaults(func=_cmd_history)


def _cmd_history(args: argparse.Namespace) -> None:
    """Execute the history subcommand."""
    start: datetime
    if args.start:
        start = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    else:
        start = datetime.now(tz=timezone.utc)

    history = build_history(
        expression=args.expression,
        start=start,
        n=args.count,
        label=args.label,
    )

    after = (
        datetime.fromisoformat(args.after).replace(tzinfo=timezone.utc)
        if args.after
        else None
    )
    before = (
        datetime.fromisoformat(args.before).replace(tzinfo=timezone.utc)
        if args.before
        else None
    )

    if after or before:
        history = filter_history(history, after=after, before=before)

    if args.summary:
        print(history.summary())
        return

    if not history.records:
        print("No records found for the given filters.")
        return

    for record in history.records:
        print(record)
