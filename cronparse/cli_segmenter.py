"""CLI subcommand for segmenting cron expressions by frequency."""

from __future__ import annotations

import argparse
from cronparse.segmenter import segment, SEGMENT_LABELS


def add_segmenter_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "segment",
        help="Group cron expressions into frequency-based buckets",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expressions to segment",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        default=None,
        help="Optional labels for each expression (must match count)",
    )
    p.add_argument(
        "--bucket",
        choices=SEGMENT_LABELS,
        default=None,
        help="Show only entries in this bucket",
    )
    p.set_defaults(func=_cmd_segment)


def _cmd_segment(args: argparse.Namespace) -> None:
    result = segment(args.expressions, labels=args.labels)

    if args.bucket:
        entries = result.buckets.get(args.bucket, [])
        if not entries:
            print(f"No expressions in bucket '{args.bucket}'.")
        else:
            for e in entries:
                print(e)
    else:
        printed = False
        for seg in SEGMENT_LABELS:
            entries = result.buckets.get(seg, [])
            if entries:
                print(f"[{seg}]")
                for e in entries:
                    print(f"  {e}")
                printed = True
        if not printed:
            print("No expressions provided.")
