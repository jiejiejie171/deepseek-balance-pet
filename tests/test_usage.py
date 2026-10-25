from datetime import datetime
from decimal import Decimal

from deepseek_pet.balance_client import Balance
from deepseek_pet.config import Config
from deepseek_pet.peak import BEIJING
from deepseek_pet.usage import UsageTracker


def balance(total: str) -> Balance:
    return Balance("CNY", Decimal(total))


def at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, day, hour, minute, tzinfo=BEIJING)


def test_first_observation_starts_at_zero(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    tracker = UsageTracker(cfg, now=at(26, 9))
    tracker.update(balance("10.00"), now=at(26, 10))
    assert tracker.spent == Decimal(0)
    assert tracker.state.last_total == Decimal("10.00")


def test_decrease_accumulates(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    tracker = UsageTracker(cfg, now=at(26, 9))
    tracker.update(balance("10.00"), now=at(26, 10))
    tracker.update(balance("8.50"), now=at(26, 10, 1))
    tracker.update(balance("8.00"), now=at(26, 10, 2))
    assert tracker.spent == Decimal("1.50") + Decimal("0.50")


def test_increase_does_not_erase_spent(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    tracker = UsageTracker(cfg, now=at(26, 9))
    tracker.update(balance("10.00"), now=at(26, 10))
    tracker.update(balance("8.00"), now=at(26, 10, 1))
    tracker.update(balance("20.00"), now=at(26, 10, 2))
    assert tracker.spent == Decimal("2.00")
    tracker.update(balance("19.00"), now=at(26, 10, 3))
    assert tracker.spent == Decimal("3.00")


def test_persists_within_same_day(tmp_path):
    path = tmp_path / "config.json"
    cfg = Config.load(path=path)
    tracker = UsageTracker(cfg, now=at(26, 9))
    tracker.update(balance("10.00"), now=at(26, 10))
    tracker.update(balance("7.25"), now=at(26, 10, 1))

    reloaded = Config.load(path=path)
    again = UsageTracker(reloaded, now=at(26, 11))
    assert again.spent == Decimal("2.75")


def test_new_day_resets(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    tracker = UsageTracker(cfg, now=at(26, 9))
    tracker.update(balance("10.00"), now=at(26, 10))
    tracker.update(balance("8.00"), now=at(26, 10, 1))
    assert tracker.spent == Decimal("2.00")

    tracker.update(balance("7.00"), now=at(27, 9))
    assert tracker.spent == Decimal(0)
    assert tracker.state.date == "2026-10-27"
