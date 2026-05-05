"""Output formatters for cron schedule inspection results."""

from datetime import datetime
from typing import List, Optional

from cronparse.timezone import localize


def format_next_runs(
    runs: List[datetime],
    tz_name: Optional[str] = None,
    fmt: str = "%Y-%m-%d %H:%M:%S %Z",
) -> List[str]:
    """Format a list of upcoming run datetimes as readable strings.

    Args:
        runs: List of datetime objects (aware or naive).
        tz_name: Optional IANA timezone to convert datetimes into.
        fmt: strftime format string for output.

    Returns:
        A list of formatted datetime strings.
    """
    result = []
    for dt in runs:
        if tz_name:
            dt = localize(dt, tz_name)
        result.append(dt.strftime(fmt))
    return result


def format_schedule_table(
    expression: str,
    description: str,
    runs: List[datetime],
    tz_name: Optional[str] = None,
) -> str:
    """Render a human-readable schedule summary table.

    Args:
        expression: The raw cron expression string.
        description: Human-readable description of the schedule.
        runs: Upcoming run datetimes.
        tz_name: Optional timezone for display.

    Returns:
        A formatted multi-line string.
    """
    lines = [
        f"Cron Expression : {expression}",
        f"Description     : {description}",
        f"Timezone        : {tz_name or 'local/naive'}",
        "-" * 40,
        "Upcoming Runs:",
    ]
    formatted = format_next_runs(runs, tz_name=tz_name)
    for i, run_str in enumerate(formatted, start=1):
        lines.append(f"  {i:>2}. {run_str}")
    return "\n".join(lines)


def format_single_run(dt: datetime, tz_name: Optional[str] = None) -> str:
    """Format a single datetime for display.

    Args:
        dt: A datetime object.
        tz_name: Optional IANA timezone for conversion.

    Returns:
        A formatted string.
    """
    if tz_name:
        dt = localize(dt, tz_name)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
