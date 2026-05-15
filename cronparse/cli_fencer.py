"""CLI subcommand: fence — restrict cron runs to a time window."""
from __future__ import annotations

import argparse
from datetime import datetime, time

from cronparse.fencer import fence


def add_fencer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "fence",
        help="Show next runs of a cron expression within a daily time fence.",
    )
    p.add_argument("expression", help="Cron expression (quoted).")
    p.add_argument(
        "--start",
        default="00:00",
        help="Fence start time HH:MM (default: 00:00).",
    )
    p.add_argument(
        "--end",
        default="23:59",
        help="Fence end time HH:MM (default: 23:59).",
    )
    p.add_argument(
        "-n",
        type=int,
        default=5,
        help="Number of runs to return (default: 5).",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression.")
    p.add_argument(
        "--anchor",
        default=None,
        help="Anchor datetime ISO format (default: now).",
    )
    p.set_defaults(func=_cmd_fence)


def _cmd_fence(args: argparse.Namespace) -> None:
    anchor = (
        datetime.fromisoformat(args.anchor) if args.anchor else datetime.utcnow()
    )
    fence_start = time.fromisoformat(args.start)
    fence_end = time.fromisoformat(args.end)

    result = fence(
        args.expression,
        anchor=anchor,
        fence_start=fence_start,
        fence_end=fence_end,
        n=args.n,
        label=args.label,
    )

    header = f"Expression : {result.expression}"
    if result.label:
        header += f"  [{result.label}]"
    print(header)
    print(f"Fence      : {result.fence_start} – {result.fence_end}")
    print(f"Runs found : {result.count()}")
    for dt in result.runs:
        print(f"  {dt.isoformat(sep=' ', timespec='minutes')}")
