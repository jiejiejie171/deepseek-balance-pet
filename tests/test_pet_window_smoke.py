import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QPoint, Qt, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from deepseek_pet.config import Config
from deepseek_pet.i18n import Translator
from deepseek_pet.ui.pet_window import PetWindow


class FakeService(QObject):
    updated = Signal(object)
    failed = Signal(str, str)

    def refresh(self):
        pass


def test_window_builds(tmp_path):
    app = QApplication.instance() or QApplication([])
    cfg = Config.load(path=tmp_path / "config.json")
    window = PetWindow(cfg, Translator("zh"), FakeService())
    assert window.width() == cfg.get("pet_size")
    assert window.is_bubble_visible() is False
    window.show()
    app.processEvents()

    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, QPoint(270, 270))
    assert window.is_bubble_visible() is True

    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, QPoint(270, 270))
    assert window.is_bubble_visible() is True

    opened = []
    window.settings_requested.connect(lambda: opened.append(True))
    QTest.mouseClick(
        window,
        Qt.LeftButton,
        Qt.NoModifier,
        window._settings_rect().center().toPoint(),
    )
    assert opened == [True]

    window.hide_bubble(animate=False)
    assert window.is_bubble_visible() is False

    cfg.set("ui.bubble_autohide_sec", 1)
    window.show_bubble()
    assert window.is_bubble_visible() is True
    QTest.qWait(1500)
    assert window.is_bubble_visible() is False

    cfg.set("ui.sound_enabled", False)
    window.apply_config()
    assert window._sound.enabled is False
    cfg.set("ui.sound_enabled", True)
    window.apply_config()

    window._sound.play_click()

    cfg.set("ui.peak_style", "liangwen")
    assert window._badge_text(type("State", (), {"is_peak": False})()) == "梁文谷"
    cfg.set("ui.peak_style", "mini")
    assert window._badge_text(type("State", (), {"is_peak": True})()) == "峰"

    from deepseek_pet.peak import peak_state

    remaining = window._remaining_text(peak_state())
    assert "后" in remaining or remaining == "即将"

    window.close()
    app.quit()
