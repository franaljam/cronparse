"""CLI subcommands for cron expression comparison and overlap detection."""

import argparse
from datetime import datetime, timezone

from cronparse.comparator import find_overlap, frequency, rank_by_frequency


def add_comparator_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register 'frequency', 'overlap', and 'rank' subcommands."""
    _add_frequency(subparsers)
    _add_overlap(subparsers)
    _add_rank(subparsers)


def _add_frequency(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "frequency", help="Show estimated run frequency for a cron expression"
    )
    p.add_argument("expression", help="Cron expression (quoted)")
    p.set_defaults(func=_cmd_frequency)


def _add_overlap(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "overlap", help="Find times when two cron expressions fire simultaneously"
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "--window",
        type=int,
        default=1440,
        help="Look-ahead window in minutes (default: 1440)",
    )
    p.set_defaults(func=_cmd_overlap)


def _add_rank(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rank", help="Rank multiple cron expressions by run frequency"
    )
    p.add_argument("expressions", nargs="+", help="Cron expressions to rank")
    p.set_defaults(func=_cmd_rank)


def _cmd_frequency(args: argparse.Namespace) -> None:
    info = frequency(args.expression)
    print(str(info))


def _cmd_overlap(args: argparse.Namespace) -> None:
    start = datetime.now(tz=timezone.utc)
    result = find_overlap(args.expr_a, args.expr_b, start=start, window=args.window)
    print(str(result))
    if result.has_overlap():
        for t in result.shared_times[:5]:
            print(f"  {t.isoformat()}")
        if len(result.shared_times) > 5:
            print(f"  ... and {len(result.shared_times) - 5} more")


def _cmd_rank(args: argparse.Namespace) -> None:
    ranked = rank_by_frequency(args.expressions)
    print("Ranked by frequency (most frequent first):")
    for i, info in enumerate(ranked, start=1):
        print(f"  {i}. {info}")
