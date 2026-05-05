"""Human-readable descriptions for parsed cron expressions."""

from cronparse.parser import CronExpression


def _describe_field(values: list[int], field: str, unit: str, total: int) -> str:
    """Return a human-readable description for a single cron field."""
    if len(values) == total:
        return f"every {unit}"

    if len(values) == 1:
        return f"at {unit} {values[0]}"

    # Check if values form a step sequence
    if len(values) > 1:
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        if len(set(diffs)) == 1:
            step = diffs[0]
            if step == 1:
                return f"from {unit} {values[0]} through {values[-1]}"
            return f"every {step} {unit}s"

    return f"at {unit}s " + ", ".join(str(v) for v in values)


def _describe_weekday(values: list[int]) -> str:
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if len(values) == 7:
        return "every day of the week"
    if len(values) == 1:
        return f"on {day_names[values[0]]}"
    names = [day_names[v] for v in values]
    return "on " + ", ".join(names)


def _describe_month(values: list[int]) -> str:
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if len(values) == 12:
        return "every month"
    if len(values) == 1:
        return f"in {month_names[values[0]]}"
    names = [month_names[v] for v in values]
    return "in " + ", ".join(names)


def humanize(expr: CronExpression) -> str:
    """Return a human-readable description of a CronExpression."""
    parts = []

    minute_desc = _describe_field(expr.minute, "minute", "minute", 60)
    hour_desc = _describe_field(expr.hour, "hour", "hour", 24)
    dom_desc = _describe_field(expr.day_of_month, "day", "day", 31)
    month_desc = _describe_month(expr.month)
    dow_desc = _describe_weekday(expr.day_of_week)

    if minute_desc == "every minute" and hour_desc == "every hour":
        parts.append("every minute")
    elif minute_desc == "every minute":
        parts.append(f"every minute {hour_desc}")
    else:
        parts.append(f"{minute_desc} past {hour_desc}")

    if dom_desc != "every day":
        parts.append(dom_desc)

    if month_desc != "every month":
        parts.append(month_desc)

    if dow_desc != "every day of the week":
        parts.append(dow_desc)

    return ", ".join(parts)
