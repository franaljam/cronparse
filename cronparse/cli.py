"""Main CLI entry point for cronparse."""

import argparse
import sys

from cronparse.humanizer import humanize
from cronparse.parser import parse
from cronparse.scheduler import next_runs
from cronparse.validator import validate
from cronparse.differ import diff
from cronparse.cli_exporter import add_export_subcommand
from cronparse.cli_summarizer import add_summarize_subcommand
from cronparse.cli_comparator import add_comparator_subcommands


def _cmd_humanize(args: argparse.Namespace) -> None:
    expr = parse(args.expression)
    print(humanize(expr))


def _cmd_next(args: argparse.Namespace) -> None:
    from datetime import datetime, timezone
    expr = parse(args.expression)
    start = datetime.now(tz=timezone.utc)
    runs = next_runs(expr, start, n=args.count)
    for r in runs:
        print(r.isoformat())


def _cmd_validate(args: argparse.Namespace) -> None:
    result = validate(args.expression)
    if result:
        print("Valid cron expression.")
    else:
        print("Invalid cron expression:")
        for msg in result.error_messages:
            print(f"  - {msg}")
        sys.exit(1)


def _cmd_diff(args: argparse.Namespace) -> None:
    result = diff(args.expr_a, args.expr_b)
    print(result.summary())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronparse",
        description="Human-readable cron expression parser and scheduler inspector",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # humanize
    p_hum = subparsers.add_parser("humanize", help="Describe a cron expression in plain English")
    p_hum.add_argument("expression", help="Cron expression")
    p_hum.set_defaults(func=_cmd_humanize)

    # next
    p_next = subparsers.add_parser("next", help="Show next scheduled run times")
    p_next.add_argument("expression", help="Cron expression")
    p_next.add_argument("--count", type=int, default=5, help="Number of runs to show")
    p_next.set_defaults(func=_cmd_next)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a cron expression")
    p_val.add_argument("expression", help="Cron expression")
    p_val.set_defaults(func=_cmd_validate)

    # diff
    p_diff = subparsers.add_parser("diff", help="Diff two cron expressions")
    p_diff.add_argument("expr_a", help="First cron expression")
    p_diff.add_argument("expr_b", help="Second cron expression")
    p_diff.set_defaults(func=_cmd_diff)

    add_export_subcommand(subparsers)
    add_summarize_subcommand(subparsers)
    add_comparator_subcommands(subparsers)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
