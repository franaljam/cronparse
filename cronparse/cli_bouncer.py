"""CLI sub-commands for the bouncer module."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from .bouncer import bounce


def add_bouncer_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *bounce* sub-command on *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "bounce",
        help="Check whether a cron expression fires within a time window.",
    )
    p.add_argument("expression", help="Cron expression to evaluate.")
    p.add_argument(
        "--start",
        default=None,
        help="Window start as ISO-8601 datetime (default: now).",
    )
    p.add_argument(
        "--hours",
        type=float,
        default=1.0,
        help="Window length in hours (default: 1).",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression.")
    p.set_defaults(func=_cmd_bounce)


def _cmd_bounce(args: argparse.Namespace) -> None:  # noqa: D401
    """Execute the *bounce* command."""
    if args.start:
        start = datetime.fromisoformat(args.start)
    else:
        now = datetime.now()
        start = now.replace(second=0, microsecond=0)

    end = start + timedelta(hours=args.hours)

    result = bounce(args.expression, start, end, label=args.label)
    print(result)
    if result.fires:
        print(f"  First hit : {result.first_hit.isoformat()}")
        print(f"  Minutes until first hit: {result.minutes_until_first:.1f}")
    else:
        print("  No firing in the specified window.")
