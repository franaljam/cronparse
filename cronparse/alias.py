"""Cron expression alias resolver — maps common @-style shortcuts to standard cron expressions."""

from typing import Dict, Optional

# Standard cron alias mappings
ALIASES: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
    "@workday": "0 9 * * 1-5",
    "@weekend": "0 10 * * 6,0",
}


class AliasError(ValueError):
    """Raised when an alias cannot be resolved."""


def is_alias(expression: str) -> bool:
    """Return True if the expression is a recognised @-alias."""
    return expression.strip().lower() in ALIASES


def resolve(expression: str) -> str:
    """Resolve an @-alias to its canonical cron expression.

    Returns the expression unchanged if it is not an alias.

    Raises:
        AliasError: if the token starts with '@' but is not a known alias.
    """
    token = expression.strip().lower()
    if token.startswith("@"):
        if token not in ALIASES:
            raise AliasError(
                f"Unknown alias '{expression}'. "
                f"Known aliases: {', '.join(sorted(ALIASES))}"
            )
        return ALIASES[token]
    return expression


def list_aliases() -> Dict[str, str]:
    """Return a copy of the full alias mapping."""
    return dict(ALIASES)


def describe_alias(alias: str) -> Optional[str]:
    """Return the cron string for a given alias, or None if not found."""
    return ALIASES.get(alias.strip().lower())
