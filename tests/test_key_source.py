import json

from deepseek_pet.config import Config
from deepseek_pet.key_source import KeyInfo, mask_key, read_claude_code_key, resolve_key


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


def test_read_claude_code_key(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-1234"}}), encoding="utf-8")
    assert read_claude_code_key(p) == "sk-claude-1234"


def test_priority_custom_over_env_over_claude(tmp_path):
    cfg = make_config(tmp_path)
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    claude = tmp_path / "claude.json"
    claude.write_text(
        json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-0000"}}), encoding="utf-8"
    )

    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, claude_settings=claude)
    assert info == KeyInfo("sk-custom-0000", "custom")

    info = resolve_key(cfg, FakeStore(None), env=env, claude_settings=claude)
    assert info.source == "env"

    info = resolve_key(cfg, FakeStore(None), env={}, claude_settings=claude)
    assert info.source == "claude"


def test_forced_source(tmp_path):
    cfg = make_config(tmp_path, "claude")
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    claude = tmp_path / "claude.json"
    claude.write_text(
        json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-0000"}}), encoding="utf-8"
    )
    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, claude_settings=claude)
    assert info.source == "claude"


def test_no_key(tmp_path):
    cfg = make_config(tmp_path)
    assert resolve_key(cfg, FakeStore(None), env={}, claude_settings=tmp_path / "nope.json") is None
