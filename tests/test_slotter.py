"""Tests for cronparse.slotter."""
import datetime
import pytest

from cronparse.slotter import slot, SlotResult, SlotEntry


REF = datetime.date(2024, 1, 15)


def test_slot_returns_slot_result():
    result = slot("* * * * *", reference_date=REF)
    assert isinstance(result, SlotResult)


def test_slot_stores_expression():
    result = slot("0 * * * *", reference_date=REF)
    assert result.expression == "0 * * * *"


def test_slot_label_none_by_default():
    result = slot("* * * * *", reference_date=REF)
    assert result.label is None


def test_slot_label_propagated():
    result = slot("* * * * *", label="all", reference_date=REF)
    assert result.label == "all"


def test_slot_default_slot_count_is_24():
    result = slot("* * * * *", reference_date=REF)
    assert result.slot_count == 24
    assert len(result.slots) == 24


def test_slot_custom_slot_count():
    result = slot("* * * * *", slot_count=12, reference_date=REF)
    assert result.slot_count == 12
    assert len(result.slots) == 12


def test_slot_entries_are_slot_entry_instances():
    result = slot("* * * * *", reference_date=REF)
    for entry in result.slots:
        assert isinstance(entry, SlotEntry)


def test_slot_index_starts_at_one():
    result = slot("* * * * *", reference_date=REF)
    assert result.slots[0].slot_index == 1


def test_slot_index_ends_at_slot_count():
    result = slot("* * * * *", slot_count=6, reference_date=REF)
    assert result.slots[-1].slot_index == 6


def test_every_minute_all_slots_fire():
    result = slot("* * * * *", reference_date=REF)
    assert all(e.fires for e in result.slots)


def test_every_minute_active_slots_equals_total():
    result = slot("* * * * *", reference_date=REF)
    assert len(result.active_slots) == result.slot_count


def test_hourly_only_one_slot_fires_per_hour():
    # 0 * * * * fires once per hour; with 24 slots each slot has 1 fire
    result = slot("0 * * * *", reference_date=REF)
    assert len(result.active_slots) == 24
    for entry in result.active_slots:
        assert entry.fire_count == 1


def test_specific_hour_only_that_slot_fires():
    # 0 9 * * * fires once at 09:00
    result = slot("0 9 * * *", reference_date=REF)
    active = result.active_slots
    assert len(active) == 1
    assert active[0].slot_start == datetime.time(9, 0)


def test_quiet_slots_count_is_complement():
    result = slot("0 9 * * *", reference_date=REF)
    assert len(result.quiet_slots) == result.slot_count - len(result.active_slots)


def test_slot_entry_str_contains_slot_index():
    result = slot("* * * * *", reference_date=REF)
    assert "1" in str(result.slots[0])


def test_slot_summary_contains_expression():
    result = slot("0 * * * *", reference_date=REF)
    assert "0 * * * *" in result.summary()


def test_slot_str_delegates_to_summary():
    result = slot("0 * * * *", reference_date=REF)
    assert str(result) == result.summary()


def test_slot_invalid_slot_count_raises():
    with pytest.raises(ValueError):
        slot("* * * * *", slot_count=0, reference_date=REF)


def test_slot_fire_count_correct_for_every_minute_48_slots():
    # 1440 minutes / 48 slots = 30 minutes per slot
    result = slot("* * * * *", slot_count=48, reference_date=REF)
    for entry in result.slots:
        assert entry.fire_count == 30
