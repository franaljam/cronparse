"""CLI helpers for the export sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .parser import parse
from .exporter import export_json, export_csv, export_text


FORMATS = ("json", "csv", "text")


def add_export_subcommand(subparsers) -> None:
    """Register the *export* sub-command onto an existing subparsers action."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "export",
        help="Export next run times in json/csv/text format",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "-f",
        "--format",
        choices=FORMATS,
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming runs to show (default: 5)",
    )
    p.add_argument(
        "--label",
        default=None,
        help="Optional human-readable label for the schedule",
    )
    p.add_argument(
        "--tz",
        default=None,
        metavar="TIMEZONE",
        help="Timezone name, e.g. Europe/London",
    )
    p.set_defaults(func=_cmd_export)


def _cmd_export(args: argparse.Namespace) -> int:
    """Handler for the *export* sub-command."""
    tz = None
    if args.tz:
        from .timezone import get_timezone
        try:
            tz = get_timezone(args.tz)
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    try:
        expr = parse(args.expression)
    except Exception as exc:  # noqa: BLE001
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    fmt: str = args.format
    n: int = args.count
    label: Optional[str] = args.label

    if fmt == "json":
        output = export_json(expr, n=n, tz=tz, label=label)
    elif fmt == "csv":
        output = export_csv(expr, n=n, tz=tz, label=label)
    else:
        output = export_text(expr, n=n, tz=tz, label=label)

    print(output)
    return 0
