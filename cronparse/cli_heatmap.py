"""CLI sub-command: heatmap — show hour×weekday firing frequency."""

from __future__ import annotations

import argparse
import datetime

from cronparse.heatmap import build_heatmap

_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def add_heatmap_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("heatmap", help="Show firing frequency heatmap")
    p.add_argument("expression", help="Cron expression")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to sample (default: 7)",
    )
    p.add_argument("--label", default=None, help="Optional label for the expression")
    p.set_defaults(func=_cmd_heatmap)


def _cmd_heatmap(args: argparse.Namespace) -> None:
    result = build_heatmap(
        args.expression,
        sample_days=args.days,
        label=args.label,
    )

    print(result.summary())
    print()

    # Header row
    header = "     " + " ".join(f"{h:3d}" for h in range(24))
    print(header)

    for wd, day in enumerate(_DAYS):
        row_vals = result.grid[wd]
        cells = " ".join(_shade(v) for v in row_vals)
        print(f"{day}  {cells}")

    print()
    peak = result.peak()
    print(
        f"Peak: {_DAYS[peak.weekday]} {peak.hour:02d}:xx — {peak.count} fire(s)"
    )


def _shade(count: int) -> str:
    """Return a 3-char cell representing the count."""
    if count == 0:
        return "  ."
    if count < 10:
        return f"  {count}"
    if count < 100:
        return f" {count}"
    return f"{count}"
