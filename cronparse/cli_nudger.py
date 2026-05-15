"""CLI sub-command: nudge — shift a cron expression by N minutes."""

from __future__ import annotations

import argparse

from .nudger import nudge


def add_nudger_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *nudge* sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "nudge",
        help="Shift the minute field of a cron expression by an offset.",
    )
    p.add_argument("expression", help="Cron expression to nudge (quote it).")
    p.add_argument(
        "offset",
        type=int,
        help="Number of minutes to shift (may be negative).",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression.")
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a one-line summary instead of the raw nudged expression.",
    )
    p.set_defaults(func=_cmd_nudge)


def _cmd_nudge(args: argparse.Namespace) -> None:
    """Execute the nudge command."""
    result = nudge(args.expression, args.offset, label=args.label)
    if args.summary:
        print(result.summary)
    else:
        print(result.expression)
