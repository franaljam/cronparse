"""CLI subcommand for the offsetter module."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .offsetter import offset


def add_offsetter_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'offset' subcommand."""
    p = subparsers.add_parser(
        "offset",
        help="Shift next run times by a fixed number of minutes",
    )
    p.add_argument("expression", help="Cron expression (quote if needed)")
    p.add_argument(
        "offset_minutes",
        type=int,
        help="Minutes to shift (positive or negative)",
    )
    p.add_argument(
        "--n",
        type=int,
        default=5,
        dest="n",
        help="Number of runs to show (default: 5)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_offset)


def _cmd_offset(args: argparse.Namespace) -> None:
    start = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    result = offset(
        args.expression,
        args.offset_minutes,
        start=start,
        n=args.n,
        label=args.label,
    )
    sign = "+" if result.offset_minutes >= 0 else ""
    print(
        f"Expression : {result.expression}"
        + (f" [{result.label}]" if result.label else "")
    )
    print(f"Offset     : {sign}{result.offset_minutes} minute(s)")
    print(f"Runs       : {result.count}")
    print()
    for orig, shifted in zip(result.original_runs, result.offset_runs):
        print(f"  {orig.strftime('%Y-%m-%d %H:%M')}  ->  {shifted.strftime('%Y-%m-%d %H:%M')}")
