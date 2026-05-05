"""Command-line interface for cronparse."""

import argparse
import sys
from datetime import datetime, timezone

from .parser import parse
from .humanizer import humanize
from .scheduler import next_runs
from .formatter import format_next_runs, format_schedule_table
from .validator import validate
from .differ import diff


def _cmd_humanize(args: argparse.Namespace) -> None:
    expr = parse(args.expression)
    print(humanize(expr))


def _cmd_next(args: argparse.Namespace) -> None:
    expr = parse(args.expression)
    now = datetime.now(tz=timezone.utc)
    tz_name = args.timezone or "UTC"
    runs = next_runs(expr, n=args.count, start=now)
    lines = format_next_runs(runs, tz=tz_name, fmt=args.format)
    for line in lines:
        print(line)


def _cmd_validate(args: argparse.Namespace) -> None:
    result = validate(args.expression)
    if result:
        print(f"Valid: {args.expression!r}")
    else:
        print(f"Invalid: {args.expression!r}", file=sys.stderr)
        for msg in result.error_messages:
            print(f"  - {msg}", file=sys.stderr)
        sys.exit(1)


def _cmd_diff(args: argparse.Namespace) -> None:
    result = diff(args.expression_a, args.expression_b)
    print(result.summary())


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="cronparse",
        description="Human-readable cron expression parser and scheduler inspector.",
    )
    sub = root.add_subparsers(dest="command", required=True)

    p_human = sub.add_parser("humanize", help="Describe a cron expression in plain English.")
    p_human.add_argument("expression", help="Cron expression, e.g. '0 9 * * 1-5'")
    p_human.set_defaults(func=_cmd_humanize)

    p_next = sub.add_parser("next", help="Show next scheduled run times.")
    p_next.add_argument("expression", help="Cron expression")
    p_next.add_argument("-n", "--count", type=int, default=5, help="Number of runs (default: 5)")
    p_next.add_argument("-z", "--timezone", default="UTC", help="Timezone name (default: UTC)")
    p_next.add_argument("-f", "--format", default="%Y-%m-%d %H:%M:%S %Z", help="Datetime format")
    p_next.set_defaults(func=_cmd_next)

    p_val = sub.add_parser("validate", help="Validate a cron expression.")
    p_val.add_argument("expression", help="Cron expression to validate")
    p_val.set_defaults(func=_cmd_validate)

    p_diff = sub.add_parser("diff", help="Compare two cron expressions.")
    p_diff.add_argument("expression_a", help="First cron expression")
    p_diff.add_argument("expression_b", help="Second cron expression")
    p_diff.set_defaults(func=_cmd_diff)

    return root


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
