from deepseek_pet.config import DEFAULTS, Config, config_dir, normalize


def test_defaults(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    assert cfg.get("refresh_interval_sec") == 60
    assert cfg.get("pet_size") == 360
    assert cfg.get("key_source") == "auto"
    assert cfg.path.exists()


def test_normalize_clamps_and_keeps_unknown():
    data = normalize(
        {
            "refresh_interval_sec": 9999,
            "pet_size": 10,
            "opacity": 9,
            "language": "xx",
            "key_source": "weird",
            "api": {"timeout_sec": 0, "unknown": 1},
            "custom_future_key": "keep-me",
        }
    )
    assert data["refresh_interval_sec"] == 600
    assert data["pet_size"] == 240
    assert data["opacity"] == 1.0
    assert data["language"] == "auto"
    assert data["key_source"] == "auto"
    assert data["api"]["timeout_sec"] == 3
    assert data["api"]["unknown"] == 1
    assert data["custom_future_key"] == "keep-me"


def test_corrupt_file_backed_up(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    cfg = Config.load(path=path)
    assert cfg.get("refresh_interval_sec") == 60
    assert (tmp_path / "config.json.bak").exists()


def test_dotted_get_set_and_save(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("position.x", 123)
    cfg.set("api.proxy", "http://127.0.0.1:7897")
    cfg.save()
    again = Config.load(path=tmp_path / "config.json")
    assert again.get("position.x") == 123
    assert again.get("api.proxy") == "http://127.0.0.1:7897"


def test_portable_dir(tmp_path):
    (tmp_path / "portable.txt").write_text("", encoding="utf-8")
    d = config_dir(portable=None, appdata=tmp_path / "appdata", exe_dir=tmp_path)
    assert d == tmp_path / "data"


def test_reset_to_defaults(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("refresh_interval_sec", 30)
    cfg.reset_to_defaults()
    assert cfg.get("refresh_interval_sec") == DEFAULTS["refresh_interval_sec"]


def test_ui_defaults_and_clamp():
    data = normalize({"ui": {"bubble_autohide_sec": 9999, "idle_animation": False}})
    assert data["ui"]["bubble_autohide_sec"] == 120
    assert data["ui"]["idle_animation"] is False
    assert data["ui"]["number_animation"] is True
    assert data["ui"]["peak_style"] == "mini"


def test_default_autohide_is_ten_seconds(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    assert cfg.get("ui.bubble_autohide_sec") == 10
    assert cfg.get("ui.sound_enabled") is True
