"""Export cron schedules to various formats (JSON, CSV, iCal-like)."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import List, Optional

from .scheduler import next_runs
from .humanizer import humanize
from .parser import CronExpression


def export_json(
    expr: CronExpression,
    n: int = 5,
    tz=None,
    label: Optional[str] = None,
) -> str:
    """Export next *n* run times as a JSON string."""
    runs: List[datetime] = next_runs(expr, n=n, tz=tz)
    payload = {
        "expression": " ".join(
            [
                expr.raw_minute,
                expr.raw_hour,
                expr.raw_dom,
                expr.raw_month,
                expr.raw_dow,
            ]
        ),
        "human": humanize(expr),
        "label": label,
        "runs": [dt.isoformat() for dt in runs],
    }
    return json.dumps(payload, indent=2)


def export_csv(
    expr: CronExpression,
    n: int = 5,
    tz=None,
    label: Optional[str] = None,
) -> str:
    """Export next *n* run times as a CSV string."""
    runs: List[datetime] = next_runs(expr, n=n, tz=tz)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["label", "expression", "human", "run_iso"])
    expression_str = " ".join(
        [
            expr.raw_minute,
            expr.raw_hour,
            expr.raw_dom,
            expr.raw_month,
            expr.raw_dow,
        ]
    )
    human = humanize(expr)
    for dt in runs:
        writer.writerow([label or "", expression_str, human, dt.isoformat()])
    return buf.getvalue()


def export_text(
    expr: CronExpression,
    n: int = 5,
    tz=None,
    label: Optional[str] = None,
) -> str:
    """Export next *n* run times as a plain-text block."""
    runs: List[datetime] = next_runs(expr, n=n, tz=tz)
    lines = []
    if label:
        lines.append(f"Schedule: {label}")
    lines.append(f"Human   : {humanize(expr)}")
    lines.append(f"Next {n} runs:")
    for i, dt in enumerate(runs, 1):
        lines.append(f"  {i}. {dt.isoformat()}")
    return "\n".join(lines)
