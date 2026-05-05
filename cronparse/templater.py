"""Cron expression template library with named, reusable patterns."""

from typing import Dict, List, Optional
from cronparse.parser import parse, CronExpression

# Built-in named templates
_TEMPLATES: Dict[str, Dict] = {
    "every_minute": {
        "expression": "* * * * *",
        "description": "Runs every minute",
        "tags": ["frequent", "debug"],
    },
    "every_hour": {
        "expression": "0 * * * *",
        "description": "Runs at the start of every hour",
        "tags": ["hourly"],
    },
    "daily_midnight": {
        "expression": "0 0 * * *",
        "description": "Runs once a day at midnight",
        "tags": ["daily"],
    },
    "daily_noon": {
        "expression": "0 12 * * *",
        "description": "Runs once a day at noon",
        "tags": ["daily"],
    },
    "weekdays_9am": {
        "expression": "0 9 * * 1-5",
        "description": "Runs at 9 AM on weekdays",
        "tags": ["business", "weekday"],
    },
    "weekly_sunday": {
        "expression": "0 0 * * 0",
        "description": "Runs at midnight every Sunday",
        "tags": ["weekly"],
    },
    "monthly_first": {
        "expression": "0 0 1 * *",
        "description": "Runs at midnight on the 1st of each month",
        "tags": ["monthly"],
    },
    "every_15_minutes": {
        "expression": "*/15 * * * *",
        "description": "Runs every 15 minutes",
        "tags": ["frequent"],
    },
    "every_6_hours": {
        "expression": "0 */6 * * *",
        "description": "Runs every 6 hours",
        "tags": ["periodic"],
    },
}


class TemplateError(Exception):
    """Raised when a template operation fails."""


def list_templates(tag: Optional[str] = None) -> List[str]:
    """Return all template names, optionally filtered by tag."""
    if tag is None:
        return list(_TEMPLATES.keys())
    return [name for name, meta in _TEMPLATES.items() if tag in meta.get("tags", [])]


def get_template(name: str) -> Dict:
    """Return the metadata dict for a named template."""
    if name not in _TEMPLATES:
        raise TemplateError(f"Unknown template: '{name}'. Use list_templates() to see available templates.")
    return dict(_TEMPLATES[name])


def resolve_template(name: str) -> CronExpression:
    """Parse and return the CronExpression for a named template."""
    meta = get_template(name)
    return parse(meta["expression"])


def describe_template(name: str) -> str:
    """Return a human-readable description of a named template."""
    meta = get_template(name)
    return f"{name}: {meta['description']} ({meta['expression']})"


def register_template(name: str, expression: str, description: str = "", tags: Optional[List[str]] = None) -> None:
    """Register a custom template by name."""
    if not name or not name.isidentifier():
        raise TemplateError(f"Template name must be a valid identifier, got: '{name}'")
    # Validate the expression is parseable
    parse(expression)
    _TEMPLATES[name] = {
        "expression": expression,
        "description": description,
        "tags": tags or [],
    }
