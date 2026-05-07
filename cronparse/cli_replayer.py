"""CLI subcommand: replay — show past runs of a cron expression within a time window."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from .replayer import replay


def add_replayer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "replay",
        help="Show past scheduled runs within a time window",
    )
    p.add_argument("expression", help="Cron expression to replay")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="How many hours back to replay (default: 24)",
    )
    p.add_argument(
        "--end",
        default=None,
        metavar="DATETIME",
        help="End datetime ISO format (default: now)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_replay)


def _cmd_replay(args: argparse.Namespace) -> None:
    end = (
        datetime.fromisoformat(args.end)
        if args.end
        else datetime.utcnow().replace(second=0, microsecond=0)
    )
    start = end - timedelta(hours=args.hours)
    result = replay(args.expression, start, end, label=args.label)
    print(str(result))
    for run in result.runs:
        print(f"  {run.isoformat()}")
