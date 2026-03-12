import pytest
from datetime import date, datetime, time, timedelta

# Update import path to match your project structure:
from solution import TimeWindow, BusyInterval, Slot, suggest_slots, InfeasibleSchedule


# ---------- Helpers ----------

def combine(d: date, t: time) -> datetime:
    return datetime.combine(d, t)


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def in_window(win: TimeWindow, t: time) -> bool:
    return win.start <= t < win.end


def assert_slots_basic_constraints(
    slots,
    day,
    working_hours,
    busy_intervals,
    duration,
    n,
    buffer,
    candidate_window,
):
    # Return type / length
    assert isinstance(slots, list)
    assert len(slots) <= n

    # Deterministic ordering: start_time ascending
    assert slots == sorted(slots, key=lambda s: s.start_time)

    # Each slot start must be within working_hours and candidate_window (if any)
    for s in slots:
        assert in_window(working_hours, s.start_time)
        if candidate_window is not None:
            assert in_window(candidate_window, s.start_time)

    # Each slot must fit fully inside working_hours and candidate_window
    for s in slots:
        start_dt = combine(day, s.start_time)
        end_dt = start_dt + duration

        wh_end = combine(day, working_hours.end)
        assert end_dt <= wh_end

        if candidate_window is not None:
            cw_end = combine(day, candidate_window.end)
            assert end_dt <= cw_end

    # No overlap with busy intervals, considering buffer:
    # busy interval is expanded to [start-buffer, end+buffer)
    for s in slots:
        slot_start = combine(day, s.start_time)
        slot_end = slot_start + duration

        for b in busy_intervals:
            b_start = combine(day, b.start) - buffer
            b_end = combine(day, b.end) + buffer
            assert not overlaps(slot_start, slot_end, b_start, b_end)


#################################################################################
# My Lab 9 Tests
#################################################################################
def test_ac4_print_summary(capsys):

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    busy = [
        BusyInterval(time(9, 20), time(9, 30))
    ]

    duration = timedelta(minutes=10)

    suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy,
        duration=duration,
        n=5
    )

    captured = capsys.readouterr()

    assert "Appointment Slot Summary" in captured.out
    assert "Day:" in captured.out
    assert "Slot Granularity" in captured.out
    assert "Time Format: 24-hour" in captured.out
    assert "Available Slots:" in captured.out

def test_ac6_combo_in_duration_busy_buffer(capsys):

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    busy = [
        BusyInterval(time(9, 10), time(9, 50))
    ]

    duration = timedelta(minutes=10)

    result = suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy,
        duration=duration,
        buffer=timedelta(minutes=10),
        n=5
    )

    captured = capsys.readouterr()

    assert result == []

    assert (
        "The combination of the duration, busy intervals and the buffer time prevents a slot to be available within the provided working hours."
        in captured.out
    )

def test_ac7_combo_in_duration_busy(capsys):

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    busy = [
        BusyInterval(time(9, 0), time(9, 50))
    ]

    duration = timedelta(minutes=15)

    result = suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy,
        duration=duration,
        n=5
    )

    captured = capsys.readouterr()

    assert result == []

    assert (
        "The combination of the duration and busy intervals prevents a slot to be available within the provided working hours."
        in captured.out
    )

def test_ac8_combo_in_duration_busy_candidate(capsys):

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(17, 0)
    )

    busy = [
        BusyInterval(time(10, 0), time(11, 0))
    ]

    duration = timedelta(minutes=30)

    candidate_window = TimeWindow(
        start=time(10, 15),
        end=time(10, 45)
    )

    result = suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy,
        duration=duration,
        candidate_window=candidate_window,
        n=5
    )

    captured = capsys.readouterr()

    assert result == []

    assert (
        "The combination of the duration, busy intervals and the candidate window prevents a slot to be available within the provided working hours"
        in captured.out
    )

def test_ec2_identical_inputs_produce_same_output():

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(11, 0)
    )

    busy = [
        BusyInterval(time(9, 30), time(10, 0))
    ]

    duration = timedelta(minutes=15)

    result1 = suggest_slots(
        day,
        working_hours,
        busy,
        duration,
        n=5
    )

    result2 = suggest_slots(
        day,
        working_hours,
        busy,
        duration,
        n=5
    )

    assert result1 == result2

def test_ec5_consecutive_slots_merge(capsys):

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(9, 10)
    )

    duration = timedelta(minutes=1)

    suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=[],
        duration=duration,
        n=20
    )

    captured = capsys.readouterr()

    # merged window should appear in output
    assert "09:00 - 09:09" in captured.out

def test_ec9_duration_larger_than_working_hours():

    day = date(2026, 3, 10)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    duration = timedelta(hours=2)

    with pytest.raises(InfeasibleSchedule) as exc_info:

        suggest_slots(
            day=day,
            working_hours=working_hours,
            busy_intervals=[],
            duration=duration,
            n=5
        )

    assert str(exc_info.value) == "Meeting duration exceeds available working hours."


#################################################################################
# Lab 8 Pre-Given Tests 
#################################################################################

def test_a1_no_busy_simple_slots():
    """
    Like original "single med exact times": here, no busy events.
    Expect earliest slots within working hours (we only assert constraints + non-empty).
    """
    day = date(2026, 2, 24)
    working = TimeWindow(time(9, 0), time(12, 0))
    busy = []
    duration = timedelta(minutes=30)

    out = suggest_slots(
        day=day,
        working_hours=working,
        busy_intervals=busy,
        duration=duration,
        n=3,
        buffer=timedelta(0),
        candidate_window=None
    )

    assert_slots_basic_constraints(out, day, working, busy, duration, 3, timedelta(0), None)
    # Should at least return 1 slot if implementation uses a reasonable slot step
    assert len(out) > 0
    # Earliest slot should be at or after working start
    assert out[0].start_time >= time(9, 0)


def test_a2_deterministic_same_inputs_same_outputs():
    """
    Like original tie/determinism check: same inputs must return identical outputs.
    """
    day = date(2026, 2, 24)
    working = TimeWindow(time(9, 0), time(17, 0))
    busy = [
        BusyInterval(time(10, 0), time(10, 30)),
        BusyInterval(time(13, 0), time(14, 0)),
    ]
    duration = timedelta(minutes=30)
    buffer = timedelta(minutes=0)

    out1 = suggest_slots(day, working, busy, duration, n=10, buffer=buffer, candidate_window=None)
    out2 = suggest_slots(day, working, busy, duration, n=10, buffer=buffer, candidate_window=None)

    assert [s.start_time for s in out1] == [s.start_time for s in out2]
    assert_slots_basic_constraints(out1, day, working, busy, duration, 10, buffer, None)


def test_a3_overlapping_and_unsorted_busy_intervals_handled():
    """
    Busy intervals may be unsorted/overlapping; suggestions must still avoid conflicts.
    """
    day = date(2026, 2, 24)
    working = TimeWindow(time(9, 0), time(12, 0))
    busy = [
        BusyInterval(time(10, 30), time(11, 0)),
        BusyInterval(time(10, 0), time(10, 45)),   # overlaps with above
        BusyInterval(time(9, 30), time(9, 45)),    # unsorted relative order
    ]
    duration = timedelta(minutes=15)

    out = suggest_slots(day, working, busy, duration, n=8, buffer=timedelta(0), candidate_window=None)
    assert_slots_basic_constraints(out, day, working, busy, duration, 8, timedelta(0), None)


def test_a4_candidate_window_respected():
    """
    Like original allowed_window respected: here we add an extra candidate window restriction.
    """
    day = date(2026, 2, 24)
    working = TimeWindow(time(9, 0), time(17, 0))
    candidate = TimeWindow(time(13, 0), time(15, 0))
    busy = []
    duration = timedelta(minutes=30)

    out = suggest_slots(day, working, busy, duration, n=5, buffer=timedelta(0), candidate_window=candidate)
    assert_slots_basic_constraints(out, day, working, busy, duration, 5, timedelta(0), candidate)

    # Every slot must start within candidate window
    assert all(candidate.start <= s.start_time < candidate.end for s in out)


def test_a5_buffer_eliminates_small_gaps():
    """
    Like original rate-limit constraint: here buffer is the key extra constraint.
    With buffer, some slots that would otherwise fit should be invalid.
    """
    day = date(2026, 2, 24)
    working = TimeWindow(time(9, 0), time(11, 0))
    # Two busy intervals leaving a 20-minute gap between them
    busy = [
        BusyInterval(time(9, 30), time(9, 50)),
        BusyInterval(time(10, 10), time(10, 30)),
    ]
    duration = timedelta(minutes=20)

    # Without buffer: the gap 9:50–10:10 is exactly 20 minutes -> potentially valid
    out_no_buffer = suggest_slots(day, working, busy, duration, n=10, buffer=timedelta(0), candidate_window=None)
    assert_slots_basic_constraints(out_no_buffer, day, working, busy, duration, 10, timedelta(0), None)

    # With 5-min buffer: effective busy expands, gap shrinks -> should reduce or remove those slots
    buf = timedelta(minutes=5)
    out_with_buffer = suggest_slots(day, working, busy, duration, n=10, buffer=buf, candidate_window=None)
    assert_slots_basic_constraints(out_with_buffer, day, working, busy, duration, 10, buf, None)

    # Buffer should not increase number of available slots (monotonicity)
    assert len(out_with_buffer) <= len(out_no_buffer)


#################################################################################
# My Lab 8 Tests
#################################################################################
def test_ac6_returns_less_than_n_when_not_enough_slots():
    """
    (Edited - Changed made during implementation)

    Constraint 6. The system respects the N provided, only returning N appointment slots,  
    or less if the available slots are less than N.

    AC6:
    Given the user enters a number N in the system,
    When the system returns the list of slots,
    Then the list should only contain N appointment slots, or less if the available slots are less than N.
    Linked Constraint ID: C6
    """

    day = date(2026, 3, 6)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    # Busy blocks leaving only one possible slot
    busy_intervals = [
        BusyInterval(start=time(9, 10), end=time(10, 0))
    ]

    duration = timedelta(minutes=10)

    n = 5  # User requests 5 slots, but fewer are available

    slots = suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy_intervals,
        duration=duration,
        n=n
    )

    # Only one slot should exist: 09:00–09:10
    assert len(slots) < n
    assert len(slots) == 1
    assert slots[0].start_time == time(9, 0)
    
def test_ac8_zero_duration_raises_value_error():
    """
    (NEW - Made during the implementation)
    Constraint 8: Duration must be greater than 0.

    AC8:
    Given the user enters a duration time that is 0
    When the system processes the duration time
    Then the system should return an error.
    Linked Constraint ID: C8
    """
    day = date(2026, 3, 1)
    working = TimeWindow(time(9, 0), time(17, 0))
    busy = []

    with pytest.raises(ValueError):
        suggest_slots(
            day,
            working,
            busy,
            duration=timedelta(minutes=0),
            n=5
        )

def test_ac9_negative_buffer_raises_value_error():
    """
    (NEW - Made during the implementation)
    Constraint 9: Buffer must be greater than or equal to 0.

    AC9:
    Given the user enters a buffer time that is negative
    When the system processes the buffer time
    Then the system should return an error.
    Linked Constraint ID: C9
    """
    day = date(2026, 3, 1)
    working = TimeWindow(time(9, 0), time(17, 0))
    busy = []

    with pytest.raises(ValueError):
        suggest_slots(
            day,
            working,
            busy,
            duration=timedelta(minutes=30),
            n=5,
            buffer=timedelta(minutes=-5)
        )

def test_ac10_negative_n_raises_value_error():
    """
    (NEW - Made during the implementation)
    Constraint 10: Buffer must be greater than or equal to 0.

    AC10:
    Given the user enters an N that is negative
    When the system processes N
    Then the system should return an error.
    Linked Constraint ID: C10
    """
    day = date(2026, 3, 1)
    working = TimeWindow(time(9, 0), time(17, 0))
    busy = []

    with pytest.raises(ValueError):
        suggest_slots(
            day,
            working,
            busy,
            duration=timedelta(minutes=30),
            n=-1
        )

def test_ac11_slot_granularity():
    """
    (NEW - Made during the implementation)
    Constraint 11: Slot granularity is 1 minute.

    AC11:
    Given the user enters working hours, list of busy intervals, and duration,
    When the system returns the list of slots,
    Then the list should contain slots that have a granularity of 1 minute.
    Linked Constraint ID: C11
    """

    day = date(2026, 3, 6)

    working_hours = TimeWindow(
        start=time(9, 0),
        end=time(10, 0)
    )

    busy_intervals = [
        BusyInterval(start=time(9, 0), end=time(9, 10))
    ]

    duration = timedelta(minutes=10)

    n = 5

    slots = suggest_slots(
        day=day,
        working_hours=working_hours,
        busy_intervals=busy_intervals,
        duration=duration,
        n=n
    )

    expected_times = [
        time(9, 10),
        time(9, 11),
        time(9, 12),
        time(9, 13),
        time(9, 14),
    ]

    assert [s.start_time for s in slots] == expected_times

def test_ac12_candidate_window_conflicts_with_working_hours():
    """
    (NEW - Made during the implementation)

    Constraint 12: Candidate window must occur within working hours.

    AC12:
    Given the user enters working hours, list of busy intervals, duration, and candidate window
    When the system discovers that the candidate window does not occur within the working hours,
    Then throw an error.
    Linked Constraint ID: C12
    """
    day = date(2026, 3, 1)

    working = TimeWindow(time(9, 0), time(12, 0))

    candidate = TimeWindow(
        time(13, 0),
        time(15, 0)
    )

    busy = []

    with pytest.raises(InfeasibleSchedule):
        suggest_slots(
            day,
            working,
            busy,
            duration=timedelta(minutes=30),
            n=5,
            candidate_window=candidate
        )

def test_ec1_duration_one_minute():
    day = date(2026, 3, 1)
    working = TimeWindow(time(9, 0), time(9, 10))
    busy = []

    slots = suggest_slots(
        day,
        working,
        busy,
        duration=timedelta(minutes=1),
        n=5
    )

    assert len(slots) == 5
    assert slots[0].start_time == time(9, 0)

def test_ec2_n_zero_returns_empty_list():
    day = date(2026, 3, 1)
    working = TimeWindow(time(9, 0), time(17, 0))
    busy = []

    slots = suggest_slots(
        day,
        working,
        busy,
        duration=timedelta(minutes=30),
        n=0
    )

    assert slots == []