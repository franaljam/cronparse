"""CLI subcommand for tagging cron expressions with semantic labels."""

import argparse
from cronparse.tagger import tag_from_string, describe_tags


def add_tagger_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'tag' subcommand onto the given subparsers."""
    parser = subparsers.add_parser(
        "tag",
        help="Tag a cron expression with semantic labels",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to tag (e.g. '0 9 * * 1-5')",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        default=False,
        help="Include human-readable descriptions for each tag",
    )
    parser.set_defaults(func=_cmd_tag)


def _cmd_tag(args: argparse.Namespace) -> None:
    """Handle the 'tag' subcommand."""
    try:
        tags = tag_from_string(args.expression)
    except Exception as exc:
        print(f"Error: {exc}")
        return

    if not tags:
        print(f"No tags found for: {args.expression}")
        return

    if args.describe:
        descriptions = describe_tags(tags)
        print(f"Tags for '{args.expression}':")
        for tag_name, desc in descriptions.items():
            print(f"  [{tag_name}] {desc}")
    else:
        print(f"Tags for '{args.expression}': {', '.join(tags)}")
