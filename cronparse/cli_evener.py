"""CLI subcommand: even — analyse distribution evenness of cron expressions."""

from __future__ import annotations

import argparse
from typing import List, Optional

from cronparse.evener import even


def add_evener_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "even",
        help="Analyse how evenly a cron expression distributes its runs.",
    )
    parser.add_argument("expressions", nargs="+", help="Cron expression(s) to analyse")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        dest="period_hours",
        help="Period length in hours (default: 24)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="Variance threshold below which distribution is considered even (default: 1.0)",
    )
    parser.add_argument(
        "--labels",
        nargs="*",
        default=None,
        help="Optional labels for each expression",
    )
    parser.set_defaults(func=_cmd_even)


def _cmd_even(args: argparse.Namespace) -> None:
    labels: Optional[List[str]] = args.labels
    for i, expr in enumerate(args.expressions):
        label = labels[i] if labels and i < len(labels) else None
        try:
            result = even(
                expr,
                period_hours=args.period_hours,
                label=label,
                threshold=args.threshold,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {expr!r}: {exc}")
            continue

        tag = f"{result.label}: " if result.label else ""
        status = "EVEN" if result.is_even else "UNEVEN"
        print(
            f"{tag}{result.expression!r} — {status} "
            f"({result.run_count} runs/{result.period_hours}h, "
            f"variance={result.variance:.2f})"
        )
