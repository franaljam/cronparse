"""CLI subcommand for zip_runs."""
from datetime import datetime, timezone


def add_zipper_subcommand(subparsers) -> None:
    p = subparsers.add_parser("zip", help="Zip next runs of multiple cron expressions")
    p.add_argument("expressions", nargs="+", help="Cron expressions to zip")
    p.add_argument("-n", type=int, default=5, help="Number of run pairs to show")
    p.add_argument(
        "--labels",
        nargs="+",
        default=None,
        help="Labels for each expression (must match count)",
    )
    p.set_defaults(func=_cmd_zip)


def _cmd_zip(args) -> None:
    from .zipper import zip_runs

    anchor = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
    result = zip_runs(
        expressions=args.expressions,
        anchor=anchor,
        n=args.n,
        labels=args.labels,
    )

    for entry in result.entries:
        run_parts = "  ".join(
            f"{label}: {dt.strftime('%Y-%m-%d %H:%M')}" for label, dt in entry.runs
        )
        print(f"[{entry.index:>2}] {run_parts}")
