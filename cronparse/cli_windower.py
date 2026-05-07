"""CLI subcommand for the windower module."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .windower import window


def add_windower_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "window",
        help="List all runs within a time window",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Window size in hours (default: 24)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO",
        help="Window start as ISO-8601 datetime (default: now UTC)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_window)


def _cmd_window(args: argparse.Namespace) -> None:
    if args.start:
        start = datetime.fromisoformat(args.start)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
    else:
        start = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

    result = window(args.expression, start, hours=args.hours, label=args.label)
    print(str(result))
    if result.runs:
        for run in result.runs:
            print(f"  {run.isoformat()}")
    else:
        print("  (no runs in this window)")
