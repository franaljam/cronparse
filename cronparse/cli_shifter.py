"""CLI sub-command: shift — shift cron minute field by a fixed offset."""
from __future__ import annotations

import argparse

from cronparse.shifter import shift, shift_many


def add_shifter_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *shift* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "shift",
        help="Shift the minute field of one or more cron expressions by a fixed offset.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expression(s) to shift.",
    )
    p.add_argument(
        "--offset",
        type=int,
        default=0,
        metavar="MINUTES",
        help="Number of minutes to shift (may be negative). Default: 0.",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        default=None,
        metavar="LABEL",
        help="Optional labels for each expression (must match count).",
    )
    p.add_argument(
        "--modified-only",
        action="store_true",
        default=False,
        help="Only print expressions that were actually changed.",
    )
    p.set_defaults(func=_cmd_shift)


def _cmd_shift(args: argparse.Namespace) -> None:
    results = shift_many(
        args.expressions,
        args.offset,
        labels=args.labels,
    )
    for result in results:
        if args.modified_only and not result.was_modified:
            continue
        print(result.summary())
