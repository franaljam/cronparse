"""CLI subcommand for the cron expression scorer."""

import argparse

from .scorer import score, score_many


def add_scorer_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'score' subcommand."""
    parser = subparsers.add_parser(
        "score",
        help="Score the complexity of one or more cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        help="Cron expression(s) to score.",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        help="Optional labels for each expression (must match count).",
    )
    parser.add_argument(
        "--breakdown",
        action="store_true",
        help="Show per-field score breakdown.",
    )
    parser.set_defaults(func=_cmd_score)


def _cmd_score(args: argparse.Namespace) -> None:
    """Execute the score subcommand."""
    labels = args.labels if args.labels else None

    if len(args.expressions) == 1:
        result = score(args.expressions[0], label=(labels[0] if labels else None))
        if args.breakdown:
            print(result.summary())
        else:
            print(result)
        return

    results = score_many(args.expressions, labels=labels)
    for result in results:
        if args.breakdown:
            print(result.summary())
            print()
        else:
            print(result)
