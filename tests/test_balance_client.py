from decimal import Decimal

import pytest
import requests

from deepseek_pet.balance_client import (
    BalanceError,
    fetch_balance,
    format_amount,
    parse_balance,
)


def test_parse_prefers_cny():
    payload = {
        "is_available": True,
        "balance_infos": [
            {
                "currency": "USD",
                "total_balance": "1.00",
                "granted_balance": "0",
                "topped_up_balance": "1.00",
            },
            {
                "currency": "CNY",
                "total_balance": "12.34",
                "granted_balance": "2.00",
                "topped_up_balance": "10.34",
            },
        ],
    }
    balance = parse_balance(payload)
    assert balance.currency == "CNY"
    assert balance.total == Decimal("12.34")
    assert format_amount(balance.currency, balance.total) == "¥12.34"


def test_parse_falls_back_to_first():
    balance = parse_balance({"balance_infos": [{"currency": "USD", "total_balance": "5.5"}]})
    assert balance.currency == "USD"
    assert format_amount("USD", balance.total) == "$5.50"


def test_parse_empty_raises():
    with pytest.raises(BalanceError) as exc:
        parse_balance({"balance_infos": []})
    assert exc.value.kind == "invalid_response"


class FakeResponse:
    def __init__(self, status_code, payload=None, json_error=False):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("not json")
        return self.payload


class FakeSession:
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.last_kwargs = None

    def get(self, url, **kwargs):
        self.last_kwargs = kwargs
        if self.exc:
            raise self.exc
        return self.response


def test_fetch_success_and_proxy():
    session = FakeSession(
        FakeResponse(200, {"balance_infos": [{"currency": "CNY", "total_balance": "8.88"}]})
    )
    balance = fetch_balance("sk-x", proxy="http://127.0.0.1:7897", session=session)
    assert balance.total == Decimal("8.88")
    assert session.last_kwargs["proxies"]["https"] == "http://127.0.0.1:7897"


@pytest.mark.parametrize(
    ("response", "kind"),
    [
        (FakeResponse(401), "unauthorized"),
        (FakeResponse(429), "rate_limited"),
        (FakeResponse(500), "server"),
    ],
)
def test_fetch_status_errors(response, kind):
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(response))
    assert exc.value.kind == kind


def test_fetch_timeout():
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(exc=requests.Timeout()))
    assert exc.value.kind == "timeout"


def test_fetch_network():
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(exc=requests.ConnectionError()))
    assert exc.value.kind == "network"
