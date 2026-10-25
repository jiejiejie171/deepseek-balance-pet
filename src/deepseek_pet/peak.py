"""DeepSeek peak / off-peak pricing window (Beijing time).

Rules copied from the upstream DSH whale widget (MIT):
- Peak: Monday-Friday, 09:00-12:00 and 14:00-18:00 Beijing time.
- Off-peak: everything else, including weekends and Chinese statutory holidays.
- Weekend valley applies from 2026-08-23; holiday valley from 2026-09-19.
- Holidays that fall on adjusted working weekends are already weekends, so they
  do not need a separate entry.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

BEIJING = timezone(timedelta(hours=8))
PEAK_HOURS = ((9, 12), (14, 18))
WEEKEND_VALLEY_FROM = datetime(2026, 8, 23, 0, 0, tzinfo=BEIJING)
HOLIDAY_VALLEY_FROM = datetime(2026, 9, 19, 0, 0, tzinfo=BEIJING)

# 2026 statutory holidays (dates that are days off). Update this list every year
# after the State Council publishes the next year's schedule.
HOLIDAY_VALLEY = frozenset(
    {
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
        "2026-02-15",
        "2026-02-16",
        "2026-02-17",
        "2026-02-18",
        "2026-02-19",
        "2026-02-20",
        "2026-02-21",
        "2026-02-22",
        "2026-02-23",
        "2026-04-04",
        "2026-04-05",
        "2026-04-06",
        "2026-05-01",
        "2026-05-02",
        "2026-05-03",
        "2026-05-04",
        "2026-05-05",
        "2026-06-19",
        "2026-06-20",
        "2026-06-21",
        "2026-09-25",
        "2026-09-26",
        "2026-09-27",
        "2026-10-01",
        "2026-10-02",
        "2026-10-03",
        "2026-10-04",
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
    }
)


@dataclass(frozen=True)
class PeakState:
    is_peak: bool
    is_holiday: bool
    is_weekend: bool
    next_change: datetime
    remaining: timedelta


def _to_beijing(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(BEIJING)
    if now.tzinfo is None:
        return now.replace(tzinfo=BEIJING)
    return now.astimezone(BEIJING)


def _flags_at(moment: datetime) -> tuple[bool, bool, bool]:
    moment = moment.astimezone(BEIJING)
    is_holiday = (
        moment >= HOLIDAY_VALLEY_FROM and moment.date().isoformat() in HOLIDAY_VALLEY
    )
    is_weekend = moment >= WEEKEND_VALLEY_FROM and moment.weekday() >= 5
    in_hours = any(start <= moment.hour < end for start, end in PEAK_HOURS)
    return (in_hours and not is_holiday and not is_weekend, is_holiday, is_weekend)


def _next_change(now: datetime, current_peak: bool) -> datetime:
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for day_offset in range(16):
        day = day_start + timedelta(days=day_offset)
        for hour in (0, 9, 12, 14, 18):
            candidate = day.replace(hour=hour)
            if candidate <= now:
                continue
            if _flags_at(candidate)[0] != current_peak:
                return candidate
    return now + timedelta(days=1)


def peak_state(now: datetime | None = None) -> PeakState:
    moment = _to_beijing(now)
    is_peak, is_holiday, is_weekend = _flags_at(moment)
    next_change = _next_change(moment, is_peak)
    return PeakState(
        is_peak=is_peak,
        is_holiday=is_holiday,
        is_weekend=is_weekend,
        next_change=next_change,
        remaining=next_change - moment,
    )


def format_countdown(delta: timedelta) -> str:
    total = max(0, int(delta.total_seconds()))
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
