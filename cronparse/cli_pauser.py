"""CLI subcommand: pause — simulate skipping upcoming cron runs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .pauser import pause


def add_pauser_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'pause' subcommand."""
    p = subparsers.add_parser(
        "pause",
        help="Simulate pausing a cron schedule by skipping upcoming runs.",
    )
    p.add_argument("expression", help="Cron expression, e.g. '*/5 * * * *'")
    p.add_argument(
        "--skip",
        type=int,
        default=1,
        metavar="N",
        help="Number of upcoming runs to skip (default: 1).",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional label for the expression.",
    )
    p.add_argument(
        "--anchor",
        default=None,
        metavar="ISO_DATETIME",
        help="Reference datetime in ISO format (default: now UTC).",
    )
    p.set_defaults(func=_cmd_pause)


def _cmd_pause(args: argparse.Namespace) -> None:
    if args.anchor:
        anchor = datetime.fromisoformat(args.anchor).replace(tzinfo=timezone.utc)
    else:
        anchor = datetime.now(tz=timezone.utc)

    result = pause(
        args.expression,
        anchor=anchor,
        skip=args.skip,
        label=args.label,
    )

    print(str(result))
    if result.skipped:
        print("Skipped runs:")
        for i, run in enumerate(result.skipped, 1):
            print(f"  {i}. {run.isoformat()}")
    if result.resumed_at:
        print(f"Resumes at: {result.resumed_at.isoformat()}")
    else:
        print("No resumed run found within schedule.")
