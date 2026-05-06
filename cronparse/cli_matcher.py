"""CLI subcommand for matching datetimes against cron expressions."""

import argparse
from datetime import datetime

from .matcher import match


def add_matcher_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'match' subcommand."""
    parser = subparsers.add_parser(
        "match",
        help="Check if a cron expression matches a given datetime",
    )
    parser.add_argument("expression", help="Cron expression to evaluate")
    parser.add_argument(
        "--at",
        metavar="DATETIME",
        default=None,
        help="Datetime to match against (ISO format, default: now)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show per-field breakdown",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Exit with code 0 if matched, 1 if not (no output)",
    )
    parser.set_defaults(func=_cmd_match)


def _cmd_match(args: argparse.Namespace) -> None:
    dt: datetime | None = None
    if args.at:
        try:
            dt = datetime.fromisoformat(args.at)
        except ValueError as exc:
            print(f"Error: invalid datetime '{args.at}': {exc}")
            raise SystemExit(2) from exc

    result = match(args.expression, dt)

    if args.quiet:
        raise SystemExit(0 if result.matched else 1)

    if args.verbose:
        print(result.summary())
    else:
        status = "MATCH" if result.matched else "NO MATCH"
        ts = (dt or datetime.now()).isoformat(timespec="seconds")
        print(f"{status}: '{args.expression}' at {ts}")
        if not result.matched:
            for f in result.failed_fields:
                print(f"  {f}")
