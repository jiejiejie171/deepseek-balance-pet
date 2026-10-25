import json

from deepseek_pet.config import Config
from deepseek_pet.key_source import KeyInfo, mask_key, read_local_tool_key, resolve_key


class FakeStore:
    def __init__(self, key=None):
        self.key = key

    def get_api_key(self):
        return self.key


def make_config(tmp_path, mode="auto"):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("key_source", mode)
    return cfg


def test_mask_key():
    assert mask_key("sk-1234567890abcdef") == "sk-****cdef"
    assert mask_key("short") == "****"


def test_read_local_tool_key(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-local-1234"}}), encoding="utf-8")
    assert read_local_tool_key(p) == "sk-local-1234"


def test_priority_custom_over_env_over_local(tmp_path):
    cfg = make_config(tmp_path)
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    local = tmp_path / "local.json"
    local.write_text(
        json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-local-0000"}}), encoding="utf-8"
    )

    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, local_settings=local)
    assert info == KeyInfo("sk-custom-0000", "custom")

    info = resolve_key(cfg, FakeStore(None), env=env, local_settings=local)
    assert info.source == "env"

    info = resolve_key(cfg, FakeStore(None), env={}, local_settings=local)
    assert info.source == "local"


def test_forced_source(tmp_path):
    cfg = make_config(tmp_path, "local")
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    local = tmp_path / "local.json"
    local.write_text(
        json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-local-0000"}}), encoding="utf-8"
    )
    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, local_settings=local)
    assert info.source == "local"


def test_no_key(tmp_path):
    cfg = make_config(tmp_path)
    assert resolve_key(cfg, FakeStore(None), env={}, local_settings=tmp_path / "nope.json") is None
