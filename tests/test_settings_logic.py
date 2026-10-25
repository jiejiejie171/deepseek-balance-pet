from deepseek_pet.config import Config
from deepseek_pet.ui.settings_dialog import apply_account, clear_custom_key


class FakeStore:
    def __init__(self, key=None):
        self.key = key

    def set_api_key(self, key):
        self.key = key

    def get_api_key(self):
        return self.key

    def clear(self):
        self.key = None


def test_apply_custom_key(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    store = FakeStore()
    apply_account(cfg, store, "custom", "sk-test-123456")
    assert cfg.get("key_source") == "custom"
    assert store.get_api_key() == "sk-test-123456"


def test_apply_empty_custom_without_key_falls_back(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("key_source", "custom")
    store = FakeStore(None)
    apply_account(cfg, store, "custom", "")
    assert cfg.get("key_source") == "auto"


def test_clear_custom_key(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("key_source", "custom")
    store = FakeStore("sk-test-123456")
    clear_custom_key(cfg, store)
    assert store.get_api_key() is None
    assert cfg.get("key_source") == "auto"
