"""CLI subcommands for cron alias resolution."""

import argparse
from cronparse.alias import AliasError, list_aliases, resolve


def add_alias_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register alias-related subcommands on *subparsers*."""
    alias_parser = subparsers.add_parser(
        "alias",
        help="Resolve or list cron @-aliases",
    )
    alias_sub = alias_parser.add_subparsers(dest="alias_cmd", required=True)

    # resolve sub-command
    resolve_p = alias_sub.add_parser("resolve", help="Resolve an @-alias to a cron expression")
    resolve_p.add_argument("expression", help="Alias or cron expression")

    # list sub-command
    alias_sub.add_parser("list", help="List all known @-aliases")

    alias_parser.set_defaults(func=_cmd_alias)


def _cmd_alias(args: argparse.Namespace) -> None:
    """Dispatch alias sub-commands."""
    if args.alias_cmd == "resolve":
        _cmd_resolve(args)
    elif args.alias_cmd == "list":
        _cmd_list(args)


def _cmd_resolve(args: argparse.Namespace) -> None:
    """Resolve a single @-alias and print the result.

    Prints a human-readable message indicating whether *expression* was
    recognised as an alias.  Exits with status 1 if the alias is invalid.
    """
    try:
        result = resolve(args.expression)
        if result == args.expression:
            print(f"Not an alias — expression returned unchanged: {result}")
        else:
            print(f"{args.expression}  →  {result}")
    except AliasError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


def _cmd_list(_args: argparse.Namespace) -> None:
    """Print a formatted table of all known @-aliases and their expansions."""
    aliases = list_aliases()
    if not aliases:
        print("No aliases defined.")
        return
    width = max(len(k) for k in aliases)
    print(f"{'Alias':<{width}}  Expression")
    print("-" * (width + 14))
    for alias, expr in sorted(aliases.items()):
        print(f"{alias:<{width}}  {expr}")
