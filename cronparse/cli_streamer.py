"""CLI subcommand for streaming cron run output."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .streamer import StreamConfig, stream


def add_streamer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'stream' subcommand."""
    p = subparsers.add_parser(
        "stream",
        help="Stream upcoming cron run times to stdout",
    )
    p.add_argument("expression", help="Cron expression (quoted)")
    p.add_argument(
        "-n", "--count", type=int, default=10, help="Number of runs to emit (default: 10)"
    )
    p.add_argument(
        "--end",
        type=str,
        default=None,
        help="Stop streaming after this ISO datetime (e.g. 2024-12-31T23:59)",
    )
    p.add_argument("--timezone", type=str, default=None, help="Timezone name for output")
    p.add_argument("--label", type=str, default=None, help="Label to prefix each output line")
    p.set_defaults(func=_cmd_stream)


def _cmd_stream(args: argparse.Namespace) -> None:
    """Execute the stream subcommand."""
    end_dt = None
    if args.end:
        end_dt = datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)

    config = StreamConfig(
        expression=args.expression,
        start=datetime.now(tz=timezone.utc),
        max_count=args.count,
        end=end_dt,
        timezone=args.timezone,
        label=args.label,
    )

    for result in stream(config):
        print(result)
