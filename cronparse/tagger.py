"""Tag cron expressions with semantic labels based on their schedule patterns."""

from typing import List, Dict
from cronparse.parser import CronExpression, parse

# Tags that can be applied to a cron expression
TAG_FREQUENT = "frequent"       # runs more than once per hour
TAG_HOURLY = "hourly"           # runs once per hour
TAG_DAILY = "daily"             # runs once per day
TAG_WEEKLY = "weekly"           # restricted to specific weekdays
TAG_MONTHLY = "monthly"         # restricted to specific days of month
TAG_BUSINESS_HOURS = "business-hours"  # runs only during 9-17
TAG_OVERNIGHT = "overnight"     # runs between 0-6
TAG_WILDCARD = "wildcard"       # all fields are wildcards


def _is_wildcard_field(values: List[int], full_range: List[int]) -> bool:
    return sorted(values) == sorted(full_range)


def tag(expr: CronExpression) -> List[str]:
    """Return a list of semantic tags for the given CronExpression."""
    tags: List[str] = []

    all_minutes = list(range(60))
    all_hours = list(range(24))
    all_doms = list(range(1, 32))
    all_dows = list(range(0, 7))

    minute_wild = _is_wildcard_field(expr.minute, all_minutes)
    hour_wild = _is_wildcard_field(expr.hour, all_hours)
    dom_wild = _is_wildcard_field(expr.dom, all_doms)
    dow_wild = _is_wildcard_field(expr.dow, all_dows)

    if minute_wild and hour_wild and dom_wild and dow_wild:
        tags.append(TAG_WILDCARD)

    if not minute_wild and len(expr.minute) > 1 and hour_wild:
        tags.append(TAG_FREQUENT)
    elif minute_wild and not hour_wild:
        tags.append(TAG_FREQUENT)

    if len(expr.minute) == 1 and len(expr.hour) == 1 and dom_wild and dow_wild:
        tags.append(TAG_DAILY)
    elif len(expr.minute) == 1 and hour_wild and dom_wild and dow_wild:
        tags.append(TAG_HOURLY)

    if not dow_wild:
        tags.append(TAG_WEEKLY)

    if not dom_wild and dow_wild:
        tags.append(TAG_MONTHLY)

    if not hour_wild:
        business = [h for h in expr.hour if 9 <= h <= 17]
        if business and all(9 <= h <= 17 for h in expr.hour):
            tags.append(TAG_BUSINESS_HOURS)

        overnight = [h for h in expr.hour if h <= 6]
        if overnight and all(h <= 6 for h in expr.hour):
            tags.append(TAG_OVERNIGHT)

    return tags


def tag_from_string(expression: str) -> List[str]:
    """Parse a cron string and return its semantic tags."""
    return tag(parse(expression))


def describe_tags(tags: List[str]) -> Dict[str, str]:
    """Return human-readable descriptions for a list of tags."""
    descriptions = {
        TAG_FREQUENT: "Runs multiple times per hour or every minute of certain hours",
        TAG_HOURLY: "Runs once every hour at a fixed minute",
        TAG_DAILY: "Runs once per day at a fixed time",
        TAG_WEEKLY: "Restricted to specific days of the week",
        TAG_MONTHLY: "Restricted to specific days of the month",
        TAG_BUSINESS_HOURS: "Runs only during business hours (9am-5pm)",
        TAG_OVERNIGHT: "Runs during overnight hours (midnight-6am)",
        TAG_WILDCARD: "All fields are wildcards; runs every minute",
    }
    return {t: descriptions[t] for t in tags if t in descriptions}
