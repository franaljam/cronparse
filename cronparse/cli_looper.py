"""CLI subcommand for loop/cycle analysis."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from cronparse.looper import loop


def add_looper_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'loop' subcommand."""
    p = subparsers.add_parser(
        "loop",
        help="Detect repeating cycles in a cron expression",
    )
    p.add_argument("expression", help="Cron expression to analyse")
    p.add_argument(
        "--n",
        type=int,
        default=10,
        metavar="N",
        help="Number of upcoming runs to sample (default: 10)",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional label for the expression",
    )
    p.set_defaults(func=_cmd_loop)


def _cmd_loop(args: argparse.Namespace) -> None:
    """Execute the loop subcommand."""
    start = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    result = loop(args.expression, start, n=args.n, label=args.label)

    print(result.summary)
    if result.has_cycle:
        c = result.cycle
        print(f"  Period : {c.period_minutes} minute(s)")
        print(f"  First  : {c.first.isoformat()}")
        print(f"  Last   : {c.last.isoformat()}")
        print(f"  Count  : {c.occurrences}")
    else:
        print("  No consistent cycle detected in the sampled runs.")
