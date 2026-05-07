"""CLI subcommand for cron expression recommendations."""

from __future__ import annotations

import argparse

from cronparse.recommender import recommend


def add_recommender_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'recommend' subcommand."""
    p = subparsers.add_parser(
        "recommend",
        help="Suggest cron expressions from a natural-language query",
    )
    p.add_argument(
        "query",
        help="Natural-language intent, e.g. 'every hour' or 'daily'",
    )
    p.add_argument(
        "--max",
        dest="max_results",
        type=int,
        default=5,
        metavar="N",
        help="Maximum number of recommendations to show (default: 5)",
    )
    p.add_argument(
        "--best",
        action="store_true",
        help="Show only the top recommendation",
    )
    p.set_defaults(func=_cmd_recommend)


def _cmd_recommend(args: argparse.Namespace) -> None:
    result = recommend(args.query, max_results=args.max_results)

    if not result.recommendations:
        print(f"No recommendations found for {args.query!r}.")
        return

    if args.best:
        r = result.best
        print(f"Expression : {r.expression}")
        print(f"Description: {r.description}")
        print(f"Human      : {r.human}")
        return

    print(f"Recommendations for {args.query!r}:\n")
    for i, r in enumerate(result.recommendations, 1):
        print(f"  {i}. {r.expression:<20} {r.human}")
