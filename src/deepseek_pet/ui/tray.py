from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from ..i18n import Translator

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def make_tray(window, tr: Translator) -> QSystemTrayIcon:
    tray = QSystemTrayIcon(QIcon(str(ASSETS / "DSniang1.png")))
    menu = QMenu()
    menu.addAction(tr.t("tray.show"), window.show)
    menu.addAction(tr.t("tray.hide"), window.hide)
    menu.addSeparator()
    menu.addAction(tr.t("menu.refresh"), window.refresh_now)
    menu.addAction(tr.t("menu.settings"), window.settings_requested.emit)
    menu.addSeparator()
    menu.addAction(tr.t("menu.quit"), window.quit_requested.emit)
    tray.setContextMenu(menu)
    tray.setToolTip(tr.t("app.title"))

    def on_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            window.setVisible(not window.isVisible())
        elif reason == QSystemTrayIcon.DoubleClick:
            window.settings_requested.emit()

    tray.activated.connect(on_activated)
    return tray
