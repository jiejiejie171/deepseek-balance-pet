import sys

import pytest

from deepseek_pet.secrets_store import SecretStore


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI is Windows-only")
def test_roundtrip(tmp_path):
    store = SecretStore(tmp_path / "secrets.bin")
    store.set_api_key("sk-test-1234567890")
    assert store.get_api_key() == "sk-test-1234567890"
    assert b"sk-test-1234567890" not in (tmp_path / "secrets.bin").read_bytes()


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI is Windows-only")
def test_clear(tmp_path):
    store = SecretStore(tmp_path / "secrets.bin")
    store.set_api_key("sk-test-1234567890")
    store.clear()
    assert store.get_api_key() is None


def test_missing_returns_none(tmp_path):
    assert SecretStore(tmp_path / "none.bin").get_api_key() is None
