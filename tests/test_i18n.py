from deepseek_pet.i18n import STRINGS, Translator, detect_language


def test_translation_keys_match():
    assert set(STRINGS["zh"]) == set(STRINGS["en"])


def test_detect_language():
    assert detect_language("zh_CN") == "zh"
    assert detect_language("zh-TW") == "zh"
    assert detect_language("en_US") == "en"
    assert detect_language("ja_JP") == "en"


def test_translator_formats_and_falls_back():
    tr = Translator("zh")
    assert tr.t("status.minutes_ago", n=3) == "3 分钟前更新"
    assert Translator("en").t("app.no_dsh") == "No DSH required · Standalone"
    assert Translator("en").t("missing.key") == "missing.key"
