"""CLI sub-command: annotate — display per-field annotations for a cron expression."""

from __future__ import annotations

import argparse
from typing import Optional

from cronparse.annotator import annotate, AnnotatedExpression


def add_annotate_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *annotate* sub-command onto *subparsers*."""
    parser = subparsers.add_parser(
        "annotate",
        help="Show per-field annotations for a cron expression.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to annotate (quote it: '*/5 * * * *').",
    )
    parser.add_argument(
        "--field",
        choices=["minute", "hour", "day", "month", "weekday"],
        default=None,
        help="Show annotation for a single field only.",
    )
    parser.add_argument(
        "--values",
        action="store_true",
        default=False,
        help="Also print the resolved integer values for each field.",
    )
    parser.set_defaults(func=_cmd_annotate)


def _cmd_annotate(args: argparse.Namespace) -> None:
    """Execute the *annotate* sub-command."""
    result: AnnotatedExpression = annotate(args.expression)

    if args.field:
        _print_single_field(result, args.field, show_values=args.values)
    else:
        _print_all_fields(result, show_values=args.values)


def _print_single_field(
    result: AnnotatedExpression,
    field_name: str,
    show_values: bool = False,
) -> None:
    ann = result.annotations[field_name]
    print(f"{ann.field_name}: {ann.raw!r}")
    print(f"  note   : {ann.note}")
    if show_values:
        print(f"  values : {ann.values}")


def _print_all_fields(
    result: AnnotatedExpression,
    show_values: bool = False,
) -> None:
    print(f"Expression : {result.expression}")
    print(f"Human      : {result.human}")
    print()
    for ann in result.annotations.values():
        print(f"  {ann.field_name:<8} {ann.raw!r:<12} {ann.note}")
        if show_values:
            print(f"           values: {ann.values}")
