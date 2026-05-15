"""CLI sub-command: sample — randomly sample firing times from a cron expression."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .sampler import sample


def add_sampler_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "sample",
        help="Randomly sample firing times from a cron expression within a time window.",
    )
    p.add_argument("expression", help="Cron expression to sample")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Window size in hours from now (default: 24)",
    )
    p.add_argument(
        "--n",
        type=int,
        default=5,
        metavar="N",
        help="Number of samples to draw (default: 5)",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_sample)


def _cmd_sample(args: argparse.Namespace) -> None:
    now = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    from datetime import timedelta

    end = now + timedelta(hours=args.hours)
    result = sample(
        args.expression,
        start=now,
        end=end,
        n=args.n,
        seed=args.seed,
        label=args.label,
    )
    print(str(result))
    if result.runs:
        for i, dt in enumerate(result.runs, 1):
            print(f"  {i:>3}. {dt.isoformat()}")
    else:
        print("  (no firing times found in window)")
