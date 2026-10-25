from deepseek_pet.config import Config
from deepseek_pet.ui.first_run import complete_first_run


class FakeStore:
    def __init__(self, key=None):
        self.key = key

    def set_api_key(self, key):
        self.key = key

    def get_api_key(self):
        return self.key


def test_complete_with_custom_key(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    store = FakeStore()
    complete_first_run(cfg, store, "custom", "sk-1234567890")
    assert cfg.get("first_run_done") is True
    assert cfg.get("key_source") == "custom"
    assert store.get_api_key() == "sk-1234567890"


def test_complete_skip(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    store = FakeStore()
    complete_first_run(cfg, store, "skip", "")
    assert cfg.get("first_run_done") is True
    assert cfg.get("key_source") == "auto"


def test_complete_custom_without_stored_key_falls_back(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    store = FakeStore()
    complete_first_run(cfg, store, "custom", "")
    assert cfg.get("key_source") == "auto"
