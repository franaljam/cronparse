"""Slot-based cron expression partitioner.

Divides a day into equal time slots and reports which slots a cron
expression fires in.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from cronparse.parser import parse
from cronparse.scheduler import next_runs

import datetime


@dataclass
class SlotEntry:
    slot_index: int
    slot_start: datetime.time
    slot_end: datetime.time
    fires: bool
    fire_count: int

    def __str__(self) -> str:
        status = "FIRES" if self.fires else "quiet"
        return (
            f"Slot {self.slot_index:>3}: "
            f"{self.slot_start.strftime('%H:%M')}-"
            f"{self.slot_end.strftime('%H:%M')} [{status}, {self.fire_count} run(s)]"
        )


@dataclass
class SlotResult:
    expression: str
    label: Optional[str]
    slot_count: int
    slots: List[SlotEntry] = field(default_factory=list)

    @property
    def active_slots(self) -> List[SlotEntry]:
        return [s for s in self.slots if s.fires]

    @property
    def quiet_slots(self) -> List[SlotEntry]:
        return [s for s in self.slots if not s.fires]

    def summary(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Slots      : {self.slot_count}\n"
            f"Active     : {len(self.active_slots)}/{self.slot_count}\n"
            f"Quiet      : {len(self.quiet_slots)}/{self.slot_count}"
        )

    def __str__(self) -> str:
        return self.summary()


def slot(
    expression: str,
    slot_count: int = 24,
    *,
    label: Optional[str] = None,
    reference_date: Optional[datetime.date] = None,
) -> SlotResult:
    """Partition a day into *slot_count* equal slots and classify each."""
    if slot_count < 1:
        raise ValueError("slot_count must be >= 1")

    ref = reference_date or datetime.date.today()
    day_start = datetime.datetime(ref.year, ref.month, ref.day, 0, 0)
    day_end = day_start + datetime.timedelta(days=1)

    minutes_per_slot = 1440 // slot_count

    # Collect all fire times for the day
    expr = parse(expression)
    runs = next_runs(expr, n=1440, start=day_start)
    run_set = set(r.replace(second=0, microsecond=0) for r in runs if r < day_end)

    slots: List[SlotEntry] = []
    for i in range(slot_count):
        start_dt = day_start + datetime.timedelta(minutes=i * minutes_per_slot)
        end_dt = start_dt + datetime.timedelta(minutes=minutes_per_slot)
        fires_in_slot = [
            r for r in run_set if start_dt <= r < end_dt
        ]
        slots.append(
            SlotEntry(
                slot_index=i + 1,
                slot_start=start_dt.time(),
                slot_end=end_dt.time(),
                fires=bool(fires_in_slot),
                fire_count=len(fires_in_slot),
            )
        )

    return SlotResult(
        expression=expression,
        label=label,
        slot_count=slot_count,
        slots=slots,
    )
