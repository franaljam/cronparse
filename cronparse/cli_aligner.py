"""CLI subcommand: align."""
from __future__ import annotations

import argparse
from datetime import datetime

from .aligner import align


def add_aligner_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "align",
        help="Align multiple cron expressions to a reference time",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expressions to align",
    )
    p.add_argument(
        "--at",
        dest="at",
        default=None,
        metavar="DATETIME",
        help="Reference datetime (ISO format, default: now)",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        default=None,
        metavar="LABEL",
        help="Optional labels for each expression",
    )
    p.set_defaults(func=_cmd_align)


def _cmd_align(args: argparse.Namespace) -> None:
    if args.at:
        reference = datetime.fromisoformat(args.at)
    else:
        reference = datetime.now().replace(second=0, microsecond=0)

    result = align(args.expressions, reference, labels=args.labels)

    print(f"Reference : {reference.strftime('%Y-%m-%d %H:%M')}")
    print(f"Aligned   : {result.count} expression(s)")
    print()
    for entry in result.entries:
        print(f"  {entry}")
    print()
    print(result.summary())
