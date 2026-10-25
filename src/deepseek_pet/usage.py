from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .balance_client import Balance
from .config import Config
from .peak import BEIJING


def _decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


@dataclass
class UsageState:
    date: str
    spent: Decimal
    last_total: Decimal | None


class UsageTracker:
    """Track today's spend from observed DeepSeek balance decreases.

    This mirrors the upstream whale widget's simple ledger: a balance drop is
    added to today's spend; a top-up (balance increase) is ignored so it does
    not erase already-recorded usage. The date rolls over in Beijing time.
    """

    def __init__(self, config: Config, now: datetime | None = None):
        self.config = config
        self.state = self._load(now or datetime.now(BEIJING))

    def _load(self, moment: datetime) -> UsageState:
        today = moment.astimezone(BEIJING).date().isoformat()
        data = self.config.get("usage")
        if isinstance(data, dict) and data.get("date") == today:
            return UsageState(
                date=today,
                spent=_decimal(data.get("spent")) or Decimal(0),
                last_total=_decimal(data.get("last_total")),
            )
        return UsageState(date=today, spent=Decimal(0), last_total=None)

    @property
    def spent(self) -> Decimal:
        return self.state.spent

    def update(self, balance: Balance, now: datetime | None = None) -> UsageState:
        moment = now or datetime.now(BEIJING)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=BEIJING)
        else:
            moment = moment.astimezone(BEIJING)
        today = moment.date().isoformat()
        if self.state.date != today:
            self.state = UsageState(today, Decimal(0), balance.total)
            self._save()
            return self.state
        if self.state.last_total is not None:
            delta = self.state.last_total - balance.total
            if delta > 0:
                self.state.spent += delta
        self.state.last_total = balance.total
        self._save()
        return self.state

    def _save(self) -> None:
        self.config.set(
            "usage",
            {
                "date": self.state.date,
                "spent": str(self.state.spent),
                "last_total": (
                    str(self.state.last_total)
                    if self.state.last_total is not None
                    else None
                ),
            },
        )
        self.config.save()
