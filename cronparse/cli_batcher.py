"""CLI subcommand: batch — group cron runs into fixed-size time windows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .batcher import batch


def add_batcher_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'batch' subcommand."""
    p = subparsers.add_parser(
        "batch",
        help="Group scheduled runs into fixed-size time windows",
    )
    p.add_argument("expression", help="Cron expression")
    p.add_argument(
        "--windows",
        type=int,
        default=6,
        metavar="N",
        help="Number of time windows (default: 6)",
    )
    p.add_argument(
        "--minutes",
        type=int,
        default=60,
        metavar="M",
        help="Duration of each window in minutes (default: 60)",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional label for the expression",
    )
    p.add_argument(
        "--show-empty",
        action="store_true",
        default=False,
        help="Include empty windows in output",
    )
    p.set_defaults(func=_cmd_batch)


def _cmd_batch(args: argparse.Namespace) -> None:
    """Execute the batch subcommand."""
    start = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    result = batch(
        args.expression,
        start=start,
        num_windows=args.windows,
        batch_minutes=args.minutes,
        label=args.label,
    )

    print(result.summary())
    print()

    for window in result.windows:
        if window.is_empty and not args.show_empty:
            continue
        status = f"{window.count} run(s)" if not window.is_empty else "(empty)"
        print(f"  [{window.index:>2}] {window.start.strftime('%H:%M')} – "
              f"{window.end.strftime('%H:%M')}  {status}")
