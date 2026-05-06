"""Group multiple cron expressions by shared schedule characteristics."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from cronparse.parser import CronExpression, parse
from cronparse.tagger import tag


@dataclass
class GroupEntry:
    expression: str
    label: Optional[str]
    parsed: CronExpression

    def __str__(self) -> str:
        name = self.label or self.expression
        return f"GroupEntry({name})"


@dataclass
class ExpressionGroup:
    key: str
    entries: List[GroupEntry] = field(default_factory=list)

    @property
    def expressions(self) -> List[str]:
        return [e.expression for e in self.entries]

    @property
    def labels(self) -> List[Optional[str]]:
        return [e.label for e in self.entries]

    def __len__(self) -> int:
        return len(self.entries)

    def __str__(self) -> str:
        return f"ExpressionGroup(key={self.key!r}, count={len(self)})"


def group_by_tag(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
) -> Dict[str, ExpressionGroup]:
    """Group expressions by their primary tag (e.g. 'frequent', 'daily')."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError(
            f"labels length {len(labels)} does not match expressions length {len(expressions)}"
        )

    groups: Dict[str, ExpressionGroup] = {}

    for i, expr_str in enumerate(expressions):
        label = labels[i] if labels is not None else None
        parsed = parse(expr_str)
        tags = tag(parsed)
        key = tags[0] if tags else "other"

        if key not in groups:
            groups[key] = ExpressionGroup(key=key)

        groups[key].entries.append(
            GroupEntry(expression=expr_str, label=label, parsed=parsed)
        )

    return groups


def group_by_hour_pattern(
    expressions: List[str],
    labels: Optional[List[Optional[str]]] = None,
) -> Dict[str, ExpressionGroup]:
    """Group expressions by their hour field pattern (wildcard vs specific)."""
    if labels is not None and len(labels) != len(expressions):
        raise ValueError(
            f"labels length {len(labels)} does not match expressions length {len(expressions)}"
        )

    groups: Dict[str, ExpressionGroup] = {}

    for i, expr_str in enumerate(expressions):
        label = labels[i] if labels is not None else None
        parsed = parse(expr_str)
        hours = parsed.hour.values
        key = "every-hour" if len(hours) == 24 else f"hours:{','.join(str(h) for h in sorted(hours))}"

        if key not in groups:
            groups[key] = ExpressionGroup(key=key)

        groups[key].entries.append(
            GroupEntry(expression=expr_str, label=label, parsed=parsed)
        )

    return groups
