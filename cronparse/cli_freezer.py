"""CLI subcommand: freeze — skip N runs then show next scheduled times."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .freezer import freeze


def add_freezer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "freeze",
        help="Skip a number of scheduled runs then show the next N.",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--skip",
        type=int,
        default=1,
        metavar="K",
        help="Number of runs to skip (default: 1)",
    )
    p.add_argument(
        "--n",
        type=int,
        default=5,
        metavar="N",
        help="Number of runs to show after resuming (default: 5)",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional label for the expression",
    )
    p.set_defaults(func=_cmd_freeze)


def _cmd_freeze(args: argparse.Namespace) -> None:
    anchor = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    result = freeze(
        args.expression,
        anchor=anchor,
        skip=args.skip,
        n=args.n,
        label=args.label,
    )
    label_str = f" [{result.label}]" if result.label else ""
    print(f"Expression{label_str}: {result.expression}")
    print(f"Skipped {result.skipped} run(s) from {anchor.isoformat()}")
    if result.resume_at:
        print(f"Resumes at: {result.resume_at.isoformat()}")
    else:
        print("No resume point found.")
    print(f"Next {result.count} run(s) after resume:")
    for i, run in enumerate(result.runs_after_resume, 1):
        print(f"  {i:>3}. {run.isoformat()}")
