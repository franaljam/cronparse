"""CLI subcommand for the shrinker module."""

import argparse
from cronparse.shrinker import shrink


def add_shrinker_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'shrink' subcommand."""
    parser = subparsers.add_parser(
        "shrink",
        help="Reduce a cron expression to its minimal equivalent form",
    )
    parser.add_argument("expression", help="Cron expression to shrink")
    parser.add_argument("--label", default=None, help="Optional label for the expression")
    parser.add_argument(
        "--modified-only",
        action="store_true",
        default=False,
        help="Only print output if the expression was modified",
    )
    parser.set_defaults(func=_cmd_shrink)


def _cmd_shrink(args: argparse.Namespace) -> None:
    """Execute the shrink command."""
    result = shrink(args.expression, label=args.label)
    if args.modified_only and not result.was_modified:
        return
    print(result.summary)
    if result.was_modified:
        print(f"  Original : {result.original}")
        print(f"  Shrunk   : {result.expression}")
        print(f"  Changed  : {', '.join(result.changed_fields)}")
    else:
        print(f"  Expression: {result.expression}")
