"""CLI subcommand for the trimmer module."""

from __future__ import annotations

import argparse

from .trimmer import trim, trim_many


def add_trimmer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'trim' subcommand."""
    parser = subparsers.add_parser(
        "trim",
        help="Trim redundant values from cron expressions",
    )
    parser.add_argument("expression", nargs="+", help="Cron expression(s) to trim")
    parser.add_argument(
        "--labels",
        nargs="*",
        metavar="LABEL",
        help="Optional labels for each expression",
    )
    parser.add_argument(
        "--modified-only",
        action="store_true",
        help="Only print expressions that were modified",
    )
    parser.set_defaults(func=_cmd_trim)


def _cmd_trim(args: argparse.Namespace) -> None:
    """Handle the 'trim' subcommand."""
    labels = args.labels
    if labels and len(labels) != len(args.expression):
        print(
            f"Error: got {len(args.expression)} expression(s) but "
            f"{len(labels)} label(s)."
        )
        return

    results = trim_many(args.expression, labels)

    for result in results:
        if args.modified_only and not result.was_modified:
            continue
        prefix = f"[{result.label}] " if result.label else ""
        print(f"{prefix}{result}")
        for change in result.changes:
            print(f"  - {change}")
