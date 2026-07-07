"""Find open time slots for a staff member or doctor within business hours,
given the times they're already booked — so a cancellation's freed-up slot
is easy to spot, and so the booking forms can show what's actually open."""

from __future__ import annotations

from datetime import time

DAY_START = time(7, 0)
DAY_END = time(20, 0)
DEFAULT_SLOT_MINUTES = 30


def _time_str_to_minutes(time_str: str) -> int:
    hour, minute = (int(part) for part in time_str.split(":"))
    return hour * 60 + minute


def _minutes_to_time_str(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def find_available_slots(
    busy_ranges: list[tuple[str, int]],
    *,
    slot_minutes: int = DEFAULT_SLOT_MINUTES,
    day_start: time = DAY_START,
    day_end: time = DAY_END,
) -> list[tuple[str, str]]:
    """Return (start, end) HH:MM slots of `slot_minutes` open within business
    hours, given `busy_ranges` as (start_time "HH:MM", duration_minutes)."""
    day_start_min = day_start.hour * 60 + day_start.minute
    day_end_min = day_end.hour * 60 + day_end.minute

    busy_intervals = sorted(
        (_time_str_to_minutes(start), _time_str_to_minutes(start) + duration)
        for start, duration in busy_ranges
    )

    merged: list[tuple[int, int]] = []
    for start, end in busy_intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    free_windows: list[tuple[int, int]] = []
    cursor = day_start_min
    for start, end in merged:
        if start > cursor:
            free_windows.append((cursor, min(start, day_end_min)))
        cursor = max(cursor, end)
    if cursor < day_end_min:
        free_windows.append((cursor, day_end_min))

    slots = []
    for start, end in free_windows:
        current = start
        while current + slot_minutes <= end:
            slots.append((current, current + slot_minutes))
            current += slot_minutes

    return [(_minutes_to_time_str(s), _minutes_to_time_str(e)) for s, e in slots]


def freed_slot_label(freed_time: str, duration_minutes: int, person_name: str, format_time) -> str:
    """Build a human-readable 'this frees up HH:MM-HH:MM for NAME' message."""
    end_minutes = _time_str_to_minutes(freed_time) + duration_minutes
    end_time = _minutes_to_time_str(min(end_minutes, DAY_END.hour * 60 + DAY_END.minute))
    return f"{format_time(freed_time)}–{format_time(end_time)} for {person_name}"
