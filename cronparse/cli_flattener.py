"""CLI subcommand: flatten — show every intra-day firing time for a cron expression."""

import argparse
from .flattener import flatten


def add_flattener_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "flatten",
        help="List every (hour, minute) firing time within a single day",
    )
    parser.add_argument("expression", help="Cron expression to flatten")
    parser.add_argument(
        "--label", default=None, help="Optional label for the expression"
    )
    parser.add_argument(
        "--format",
        choices=["short", "long"],
        default="short",
        dest="fmt",
        help="Output format: 'short' (HH:MM) or 'long' (hour=H, minute=M)",
    )
    parser.set_defaults(func=_cmd_flatten)


def _cmd_flatten(args: argparse.Namespace) -> None:
    result = flatten(args.expression, label=args.label)

    header = str(result)
    print(header)
    print(f"  Fires {result.count} time(s) per day:")

    for hour, minute in result.times:
        if args.fmt == "long":
            print(f"  hour={hour:02d}, minute={minute:02d}")
        else:
            print(f"  {hour:02d}:{minute:02d}")
