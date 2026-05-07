"""Suggest cron expressions based on a natural-language-style intent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import parse
from cronparse.humanizer import humanize

# Mapping of intent keywords to (expression, description) pairs
_INTENT_MAP: List[tuple[str, str, str]] = [
    ("every minute", "* * * * *", "Runs every minute"),
    ("every hour", "0 * * * *", "Runs at the start of every hour"),
    ("every day", "0 0 * * *", "Runs once a day at midnight"),
    ("daily", "0 0 * * *", "Runs once a day at midnight"),
    ("every weekday", "0 9 * * 1-5", "Runs at 9 AM on weekdays"),
    ("weekday", "0 9 * * 1-5", "Runs at 9 AM on weekdays"),
    ("every weekend", "0 10 * * 6,0", "Runs at 10 AM on weekends"),
    ("weekend", "0 10 * * 6,0", "Runs at 10 AM on weekends"),
    ("every week", "0 0 * * 0", "Runs once a week on Sunday at midnight"),
    ("weekly", "0 0 * * 0", "Runs once a week on Sunday at midnight"),
    ("every month", "0 0 1 * *", "Runs on the first day of every month"),
    ("monthly", "0 0 1 * *", "Runs on the first day of every month"),
    ("every year", "0 0 1 1 *", "Runs once a year on January 1st"),
    ("yearly", "0 0 1 1 *", "Runs once a year on January 1st"),
    ("every 5 minutes", "*/5 * * * *", "Runs every 5 minutes"),
    ("every 10 minutes", "*/10 * * * *", "Runs every 10 minutes"),
    ("every 15 minutes", "*/15 * * * *", "Runs every 15 minutes"),
    ("every 30 minutes", "*/30 * * * *", "Runs every 30 minutes"),
    ("twice a day", "0 0,12 * * *", "Runs at midnight and noon"),
    ("noon", "0 12 * * *", "Runs every day at noon"),
    ("midnight", "0 0 * * *", "Runs every day at midnight"),
]


@dataclass
class Recommendation:
    intent: str
    expression: str
    description: str
    human: str

    def __str__(self) -> str:
        return f"{self.expression!r} — {self.human}"


@dataclass
class RecommendationResult:
    query: str
    recommendations: List[Recommendation] = field(default_factory=list)

    @property
    def best(self) -> Optional[Recommendation]:
        return self.recommendations[0] if self.recommendations else None

    def __len__(self) -> int:
        return len(self.recommendations)

    def __str__(self) -> str:
        if not self.recommendations:
            return f"No recommendations found for {self.query!r}"
        lines = [f"Recommendations for {self.query!r}:"]
        for r in self.recommendations:
            lines.append(f"  {r}")
        return "\n".join(lines)


def recommend(query: str, max_results: int = 5) -> RecommendationResult:
    """Return cron expression recommendations matching the given query."""
    q = query.lower().strip()
    seen: set[str] = set()
    recs: List[Recommendation] = []

    for intent, expr, desc in _INTENT_MAP:
        if intent in q and expr not in seen:
            parsed = parse(expr)
            recs.append(Recommendation(
                intent=intent,
                expression=expr,
                description=desc,
                human=humanize(parsed),
            ))
            seen.add(expr)
        if len(recs) >= max_results:
            break

    return RecommendationResult(query=query, recommendations=recs)
