## Student Name: Rocco Fernando Gadista
## Student ID: 219714732

"""
Task A: Appointment Timeslot Recommender (Stub)

In this lab, you will design and implement an Appointment Slot Recommender using an LLM assistant
as your primary programming collaborator.

You are asked to implement a Python module that recommends available meeting slots within a
defined working window.

The system must:
  • Accept working hours (start and end time).
  • Accept a list of existing busy intervals.
  • Accept a required meeting duration.
  • Accept an optional buffer time between meetings.
  • Optionally restrict suggestions to a candidate time window.
  • Return chronologically ordered appointment slots that satisfy all constraints.

The system must ensure that:
  • Suggested slots fall within working hours.
  • Suggested slots do not overlap busy intervals.
  • Buffer time is respected when evaluating availability.
  • Output ordering is deterministic under identical inputs.

The module must preserve the following invariants:
  • Returned slots must be at least as long as the required duration.
  • No returned slot may violate buffer constraints.
  • The returned list must reflect the current system state.

The system must correctly handle non-trivial scenarios such as:
  • Adjacent busy intervals.
  • Very small gaps between meetings.
  • Buffers eliminating otherwise valid availability.
  • Overlapping or unsorted busy intervals.
  • A meeting duration longer than any available gap.
  • No availability within the working window.

Output:
  The output consists of the next N valid appointment suggestions in chronological order.
  Behavior must be deterministic under ties (if any).

See the lab handout for full requirements.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, time
from typing import List, Optional, Tuple


# ---------------- Data Models ----------------

@dataclass(frozen=True)
class TimeWindow:
    """
    A daily time window.
    Assumption (unless stated otherwise in handout): non-wrapping window where start < end.
    """
    start: time
    end: time


@dataclass(frozen=True)
class BusyInterval:
    """
    A busy interval on the given day.
    Invariant: start < end
    """
    start: time
    end: time


@dataclass(frozen=True)
class Slot:
    """
    A recommended appointment slot.

    start_time is a time-of-day within the working window.
    Deterministic ordering: sort by start_time ascending.
    """
    start_time: time


class InfeasibleSchedule(Exception):
    """Raised when no valid slots can be produced (if required by handout)."""
    pass

# ---------------- Helper Functions ----------------

def combine(day: date, t: time) -> datetime:
    return datetime.combine(day, t)


def merge_busy_intervals(busy: List[BusyInterval], day: date) -> List[tuple]:
    """
    Merge overlapping busy intervals.
    Returns list of (start_datetime, end_datetime).
    """

    if not busy:
        return []

    intervals = sorted(
        [(combine(day, b.start), combine(day, b.end)) for b in busy],
        key=lambda x: x[0]
    )

    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end:  # overlap
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))
    return merged

# ---------------- Core Function ----------------

def suggest_slots(
    day: date,
    working_hours: TimeWindow,
    busy_intervals: List[BusyInterval],
    duration: timedelta,
    n: int,
    buffer: timedelta = timedelta(0),
    candidate_window: Optional[TimeWindow] = None
) -> List[Slot]:
    """
    Suggest up to the next n valid appointment slots (start times) for the given day.

    Args:
        day: the calendar day for which to suggest slots.
        working_hours: the allowed working window for meetings (start < end).
        busy_intervals: list of busy time intervals (may be overlapping / unsorted).
        duration: required meeting length (must be > 0).
        n: maximum number of slot suggestions to return (n >= 0).
        buffer: optional buffer time required between meetings (buffer >= 0).
        candidate_window: optional extra restriction on suggestions (must lie within this window too).

    Returns:
        A list of Slot objects, sorted by start_time ascending, deterministic under identical inputs.
        If no suitable time slots are available, return an empty list.

    Notes:
        - Suggested slots must fall within working_hours (and candidate_window if provided).
        - Suggested slots must not overlap busy_intervals, considering buffer time.
        - You are free to choose internal representation; inputs use time-of-day.
        - See lab handout for required slot granularity (e.g., 5-min/15-min steps), if any.
    """

    ##################################################################
    # TODO: Implement as per lab handout requirements and constraints.
    ##################################################################

    if duration <= timedelta(0):
        raise ValueError("Duration must be positive")

    if buffer < timedelta(0):
        raise ValueError("Buffer must be non-negative")
    
    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return []

    work_start = combine(day, working_hours.start)
    work_end = combine(day, working_hours.end)

    if work_start >= work_end:
        raise ValueError("Invalid working hours")

    # Apply candidate window
    if candidate_window:
        cand_start = combine(day, candidate_window.start)
        cand_end = combine(day, candidate_window.end)

        effective_start = max(work_start, cand_start)
        effective_end = min(work_end, cand_end)

        if effective_start >= effective_end:
            raise InfeasibleSchedule("Candidate window conflicts with working hours")
    else:
        effective_start = work_start
        effective_end = work_end

    # Merge busy intervals
    merged_busy = merge_busy_intervals(busy_intervals, day)

    # Apply buffer BEFORE and AFTER meetings
    buffered_busy = [(start - buffer, end + buffer) for start, end in merged_busy]

    slots: List[Slot] = []

    current = effective_start

    step = timedelta(minutes=1)

    while current + duration <= effective_end and len(slots) < n:

        meeting_end = current + duration

        overlap = False

        for busy_start, busy_end in buffered_busy:
            if not (meeting_end <= busy_start or current >= busy_end):
                overlap = True
                break

        if not overlap:
            slots.append(Slot(start_time=current.time()))

        current += step

    return slots

    # raise NotImplementedError("suggest_slots has not been implemented yet")