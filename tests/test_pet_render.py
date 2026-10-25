from decimal import Decimal

from deepseek_pet.balance_client import format_amount


def test_amount_format():
    assert format_amount("CNY", Decimal("100.5")) == "¥100.50"
    assert format_amount("USD", Decimal(0)) == "$0.00"
