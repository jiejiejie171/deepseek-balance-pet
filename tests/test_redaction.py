import logging

from deepseek_pet.logging_setup import RedactingFilter, redact


def test_redact_removes_secret():
    text = "request failed key=sk-abcdefghijklmnop1234"
    cleaned = redact(text)
    assert "abcdefghijklmnop1234" not in cleaned
    assert "sk-" in cleaned


def test_filter_rewrites_record():
    record = logging.LogRecord(
        "x", logging.ERROR, __file__, 1, "bad %s", ("sk-1234567890abcd",), None
    )
    RedactingFilter().filter(record)
    assert "1234567890abcd" not in record.getMessage()
