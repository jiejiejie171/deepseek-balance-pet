from datetime import datetime, timedelta

from deepseek_pet.peak import BEIJING, format_countdown, peak_state


def bj(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=BEIJING)


def test_weekday_before_peak():
    state = peak_state(bj(2026, 10, 26, 8, 0))
    assert state.is_peak is False
    assert state.next_change == bj(2026, 10, 26, 9, 0)


def test_weekday_peak_start_inclusive():
    state = peak_state(bj(2026, 10, 26, 9, 0))
    assert state.is_peak is True
    assert state.next_change == bj(2026, 10, 26, 12, 0)


def test_weekday_lunch_offpeak():
    state = peak_state(bj(2026, 10, 26, 12, 0))
    assert state.is_peak is False
    assert state.next_change == bj(2026, 10, 26, 14, 0)


def test_weekday_afternoon_peak():
    state = peak_state(bj(2026, 10, 26, 15, 0))
    assert state.is_peak is True
    assert state.next_change == bj(2026, 10, 26, 18, 0)


def test_weekday_evening_to_next_morning():
    state = peak_state(bj(2026, 10, 26, 18, 0))
    assert state.is_peak is False
    assert state.next_change == bj(2026, 10, 27, 9, 0)


def test_friday_evening_skips_weekend():
    state = peak_state(bj(2026, 10, 30, 19, 0))
    assert state.is_peak is False
    assert state.is_weekend is False
    assert state.next_change == bj(2026, 11, 2, 9, 0)


def test_saturday_is_offpeak():
    state = peak_state(bj(2026, 10, 24, 10, 0))
    assert state.is_peak is False
    assert state.is_weekend is True
    assert state.next_change == bj(2026, 10, 26, 9, 0)


def test_statutory_holiday_is_offpeak():
    state = peak_state(bj(2026, 10, 1, 10, 0))
    assert state.is_peak is False
    assert state.is_holiday is True
    assert state.next_change == bj(2026, 10, 8, 9, 0)


def test_weekend_valley_effective_from():
    before = peak_state(bj(2026, 8, 22, 10, 0))
    assert before.is_peak is True
    after = peak_state(bj(2026, 8, 23, 10, 0))
    assert after.is_peak is False
    assert after.is_weekend is True


def test_format_countdown():
    assert format_countdown(timedelta(hours=1, minutes=23, seconds=45)) == "01:23:45"
    assert format_countdown(timedelta(seconds=5)) == "00:00:05"
