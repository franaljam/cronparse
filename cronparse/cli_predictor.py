"""CLI subcommand: predict — show when a cron expression fires in a time window."""

import argparse
from datetime import datetime, timezone, timedelta

from .predictor import predict


def add_predictor_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "predict",
        help="Show occurrences of a cron expression within a time window",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--start",
        default=None,
        help="Window start as ISO datetime (default: now)",
    )
    p.add_argument(
        "--hours",
        type=float,
        default=24.0,
        help="Window length in hours (default: 24)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_predict)


def _parse_start(start_str: str) -> datetime | None:
    """Parse an ISO datetime string into an aware datetime.

    Returns the parsed datetime with UTC applied if no timezone is present,
    or None (after printing an error) if parsing fails.
    """
    try:
        start = datetime.fromisoformat(start_str)
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        return start
    except ValueError as exc:
        print(f"Error: invalid --start datetime: {exc}")
        return None


def _cmd_predict(args: argparse.Namespace) -> None:
    now = datetime.now(tz=timezone.utc)
    if args.start:
        start = _parse_start(args.start)
        if start is None:
            return
    else:
        start = now

    end = start + timedelta(hours=args.hours)

    try:
        result = predict(args.expression, start, end, label=args.label)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}")
        return

    print(str(result))
    if result.fires:
        for occ in result.occurrences:
            print(f"  {occ.isoformat()}")
