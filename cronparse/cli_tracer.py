"""CLI subcommand: trace — show field-level match details for upcoming runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Optional

from .tracer import trace


def add_tracer_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *trace* subcommand on *subparsers*."""
    p = subparsers.add_parser(
        "trace",
        help="Show field-level match details for the next N runs of a cron expression.",
    )
    p.add_argument("expression", help="Cron expression (quote if it contains spaces).")
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of runs to trace (default: 5).",
    )
    p.add_argument(
        "--label",
        default=None,
        metavar="LABEL",
        help="Optional label to attach to the trace.",
    )
    p.set_defaults(func=_cmd_trace)


def _cmd_trace(args: argparse.Namespace) -> None:
    """Execute the trace subcommand."""
    start = datetime.now(tz=timezone.utc)
    result = trace(
        expression=args.expression,
        start=start,
        n=args.count,
        label=args.label,
    )
    print(result.summary())
