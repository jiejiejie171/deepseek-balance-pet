from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import requests

SYMBOLS = {"CNY": "¥", "USD": "$"}


@dataclass(frozen=True)
class Balance:
    currency: str
    total: Decimal
    granted: Decimal | None = None
    topped_up: Decimal | None = None
    is_available: bool = True
    infos: tuple[dict, ...] = ()


class BalanceError(Exception):
    def __init__(self, kind: str, status: int | None = None):
        super().__init__(kind)
        self.kind = kind
        self.status = status


def _decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def parse_balance(payload: dict) -> Balance:
    infos = payload.get("balance_infos") if isinstance(payload, dict) else None
    if not isinstance(infos, list) or not infos:
        raise BalanceError("invalid_response")
    chosen = next(
        (item for item in infos if str(item.get("currency", "")).upper() == "CNY"),
        infos[0],
    )
    total = _decimal(chosen.get("total_balance"))
    if total is None:
        raise BalanceError("invalid_response")
    return Balance(
        currency=str(chosen.get("currency") or "CNY").upper(),
        total=total,
        granted=_decimal(chosen.get("granted_balance")),
        topped_up=_decimal(chosen.get("topped_up_balance")),
        is_available=bool(payload.get("is_available", True)),
        infos=tuple(infos),
    )


def format_amount(currency: str, amount: Decimal) -> str:
    symbol = SYMBOLS.get(currency.upper())
    if symbol:
        return f"{symbol}{amount:.2f}"
    return f"{currency.upper()} {amount:.2f}"


def fetch_balance(
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    timeout: int = 10,
    proxy: str | None = None,
    session=None,
) -> Balance:
    client = session or requests.Session()
    url = base_url.rstrip("/") + "/user/balance"
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=timeout,
            proxies=proxies,
        )
    except requests.Timeout as exc:
        raise BalanceError("timeout") from exc
    except requests.RequestException as exc:
        raise BalanceError("network") from exc

    if response.status_code in (401, 403):
        raise BalanceError("unauthorized", response.status_code)
    if response.status_code == 429:
        raise BalanceError("rate_limited", 429)
    if response.status_code >= 500:
        raise BalanceError("server", response.status_code)
    if response.status_code != 200:
        raise BalanceError("unknown", response.status_code)
    try:
        payload = response.json()
    except ValueError as exc:
        raise BalanceError("invalid_response") from exc
    return parse_balance(payload)
