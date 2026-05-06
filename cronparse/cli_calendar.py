"""CLI subcommand: calendar — display a weekly firing grid."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from cronparse.parser import parse
from cronparse.alias_integration import parse_with_alias
from cronparse.calendar import build_calendar


def add_calendar_subcommand(subparsers: argparse.Action) -> None:
    """Register the 'calendar' subcommand."""
    p = subparsers.add_parser(
        "calendar",
        help="Show a weekly calendar view of cron firing times.",
    )
    p.add_argument("expression", help="Cron expression or alias (e.g. @daily)")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to display (default: 7)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_calendar)


def _cmd_calendar(args: argparse.Namespace) -> None:
    """Execute the calendar subcommand."""
    try:
        expr_str, expr = parse_with_alias(args.expression)
    except Exception:
        expr_str = args.expression
        expr = parse(args.expression)

    start = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    view = build_calendar(
        expr,
        start=start,
        days=args.days,
        expression_str=expr_str,
        label=args.label,
    )

    header = f"Calendar for '{expr_str}'"
    if args.label:
        header += f" [{args.label}]"
    header += f" — {args.days} day(s) from {start.strftime('%Y-%m-%d %H:%M')} UTC"
    print(header)
    print(f"Total firing hours: {view.firing_count}")
    print()

    for day, cells in view.by_day().items():
        firing_hours = [c.dt.strftime("%H:00") for c in cells if c.fires]
        if firing_hours:
            hours_str = ", ".join(firing_hours)
        else:
            hours_str = "(none)"
        print(f"  {day}: {hours_str}")
