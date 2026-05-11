"""CLI subcommand: slot — partition a day into time slots."""
from __future__ import annotations

import argparse
import datetime

from cronparse.slotter import slot


def add_slotter_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "slot",
        help="Partition a day into time slots and show which fire",
    )
    p.add_argument("expression", help="Cron expression")
    p.add_argument(
        "--slots",
        type=int,
        default=24,
        metavar="N",
        help="Number of equal time slots (default: 24)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.add_argument(
        "--date",
        default=None,
        metavar="YYYY-MM-DD",
        help="Reference date (default: today)",
    )
    p.add_argument(
        "--active-only",
        action="store_true",
        help="Only show slots where the expression fires",
    )
    p.set_defaults(func=_cmd_slot)


def _cmd_slot(args: argparse.Namespace) -> None:
    ref: datetime.date | None = None
    if args.date:
        ref = datetime.date.fromisoformat(args.date)

    result = slot(
        args.expression,
        slot_count=args.slots,
        label=args.label,
        reference_date=ref,
    )

    print(result.summary())
    print()

    entries = result.active_slots if args.active_only else result.slots
    for entry in entries:
        print(f"  {entry}")
