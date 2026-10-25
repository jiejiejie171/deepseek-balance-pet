from decimal import Decimal

from deepseek_pet import cli
from deepseek_pet.balance_client import Balance
from deepseek_pet.config import Config
from deepseek_pet.secrets_store import SecretStore


def test_check_no_key(tmp_path, monkeypatch, capsys):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    monkeypatch.setattr(cli, "resolve_key", lambda *a, **k: None)
    assert cli.run_check(cfg, store) == 2
    assert "API" in capsys.readouterr().out


def test_check_success(tmp_path, monkeypatch, capsys):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    info = type("Info", (), {"key": "sk-test", "source": "custom", "masked": "sk-****test"})()
    monkeypatch.setattr(cli, "resolve_key", lambda *a, **k: info)
    monkeypatch.setattr(
        cli,
        "fetch_balance",
        lambda *a, **k: Balance("CNY", Decimal("1.23"), None, None, True),
    )
    assert cli.run_check(cfg, store) == 0
    assert "CNY" in capsys.readouterr().out
