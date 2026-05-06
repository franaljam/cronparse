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


def _cmd_predict(args: argparse.Namespace) -> None:
    now = datetime.now(tz=timezone.utc)
    if args.start:
        try:
            start = datetime.fromisoformat(args.start)
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
        except ValueError as exc:
            print(f"Error: invalid --start datetime: {exc}")
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
