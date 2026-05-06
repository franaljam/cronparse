"""CLI subcommand for snapshot: capture and diff cron expressions."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from cronparse.snapshot import take_snapshot, diff_snapshots


def add_snapshot_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register 'snapshot' and 'snapshot-diff' subcommands onto *subparsers*."""
    snap_parser = subparsers.add_parser(
        "snapshot",
        help="Capture a cron expression as a timestamped snapshot.",
    )
    snap_parser.add_argument("expression", help="Cron expression to snapshot.")
    snap_parser.add_argument("--label", default=None, help="Optional label for the snapshot.")
    snap_parser.set_defaults(func=_cmd_snapshot)

    diff_parser = subparsers.add_parser(
        "snapshot-diff",
        help="Show which fields changed between two cron expressions.",
    )
    diff_parser.add_argument("before", help="Original cron expression.")
    diff_parser.add_argument("after", help="Updated cron expression.")
    diff_parser.add_argument("--label-before", default=None, dest="label_before")
    diff_parser.add_argument("--label-after", default=None, dest="label_after")
    diff_parser.set_defaults(func=_cmd_snapshot_diff)


def _cmd_snapshot(args: argparse.Namespace) -> None:
    """Handle the 'snapshot' subcommand."""
    now = datetime.now(tz=timezone.utc)
    snap = take_snapshot(args.expression, label=args.label, captured_at=now)
    print(str(snap))
    print(f"Fields: {snap.fields}")


def _cmd_snapshot_diff(args: argparse.Namespace) -> None:
    """Handle the 'snapshot-diff' subcommand."""
    now = datetime.now(tz=timezone.utc)
    before = take_snapshot(args.before, label=args.label_before, captured_at=now)
    after = take_snapshot(args.after, label=args.label_after, captured_at=now)
    delta = diff_snapshots(before, after)

    print(f"Before : {before}")
    print(f"After  : {after}")
    print()
    print(delta.summary())
    if delta.has_changes:
        print(f"Changed fields: {', '.join(delta.changed_fields)}")
