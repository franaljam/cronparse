"""CLI subcommand for ranking cron expressions."""

import argparse
from cronparse.ranker import rank


def add_ranker_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "rank",
        help="Rank cron expressions by frequency and specificity",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to rank",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        help="Optional labels corresponding to each expression",
    )
    p.add_argument(
        "--reverse",
        action="store_true",
        help="Show least frequent first",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Include runs/day and specificity details",
    )
    p.set_defaults(func=_cmd_rank)


def _cmd_rank(args: argparse.Namespace) -> None:
    labels = args.labels if args.labels else None
    try:
        entries = rank(args.expressions, labels=labels, reverse=args.reverse)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    for entry in entries:
        if args.verbose:
            print(str(entry))
        else:
            display = entry.label or entry.expression
            print(f"[{entry.rank}] {display}")
