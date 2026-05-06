"""CLI sub-command for normalizing cron expressions."""

from __future__ import annotations

import argparse

from .normalizer import normalize, are_equivalent


def add_normalizer_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register *normalize* and *equivalent* sub-commands on *subparsers*."""
    norm_p = subparsers.add_parser(
        "normalize",
        help="Convert a cron expression to its canonical form.",
    )
    norm_p.add_argument("expression", help="Cron expression or alias to normalize.")
    norm_p.set_defaults(func=_cmd_normalize)

    eq_p = subparsers.add_parser(
        "equivalent",
        help="Check whether two cron expressions are schedule-equivalent.",
    )
    eq_p.add_argument("expression_a", help="First cron expression or alias.")
    eq_p.add_argument("expression_b", help="Second cron expression or alias.")
    eq_p.set_defaults(func=_cmd_equivalent)


def _cmd_normalize(args: argparse.Namespace) -> None:
    result = normalize(args.expression)
    print(f"Original : {result.original}")
    if result.was_alias:
        print(f"Resolved : {result.expression.minute} (alias expanded)")
    print(f"Canonical: {result.canonical}")


def _cmd_equivalent(args: argparse.Namespace) -> None:
    equiv = are_equivalent(args.expression_a, args.expression_b)
    a_canon = normalize(args.expression_a).canonical
    b_canon = normalize(args.expression_b).canonical
    print(f"A canonical: {a_canon}")
    print(f"B canonical: {b_canon}")
    print(f"Equivalent : {'yes' if equiv else 'no'}")
