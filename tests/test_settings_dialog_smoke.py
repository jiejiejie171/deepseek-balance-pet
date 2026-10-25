import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from deepseek_pet.config import Config
from deepseek_pet.i18n import Translator
from deepseek_pet.ui.settings_dialog import CompactSettings


class FakeStore:
    def __init__(self, key="sk-test-12345678"):
        self.key = key

    def get_api_key(self):
        return self.key


def test_dialog_builds(tmp_path):
    app = QApplication.instance() or QApplication([])
    cfg = Config.load(path=tmp_path / "config.json")
    dialog = CompactSettings(cfg, Translator("zh"), FakeStore())
    assert dialog.size_slider.value() == 360

    sizes = []
    dialog.preview_size_changed.connect(sizes.append)
    dialog.size_slider.setValue(400)
    assert sizes[-1] == 400

    opacities = []
    dialog.preview_opacity_changed.connect(opacities.append)
    dialog.opacity_slider.setValue(80)
    assert opacities[-1] == 0.8

    dialog.close()
    app.quit()
