import getpass
import sys
from decimal import Decimal
from pathlib import Path

from PySide6.QtCore import QLocale, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from . import __version__
from .balance_client import Balance
from .balance_service import BalanceService
from .config import Config
from .i18n import Translator, detect_language
from .logging_setup import setup_logging
from .secrets_store import SecretStore
from .startup import set_startup
from .ui.first_run import FirstRunDialog
from .ui.pet_window import PetWindow
from .ui.settings_dialog import CompactSettings
from .ui.tray import make_tray

ASSETS = Path(__file__).resolve().parent / "assets"


def _language(config: Config) -> str:
    lang = config.get("language", "auto")
    if lang == "auto":
        lang = detect_language(QLocale.system().name())
    return lang


def _acquire_single_instance(name: str):
    from PySide6.QtNetwork import QLocalServer, QLocalSocket

    socket = QLocalSocket()
    socket.connectToServer(name)
    if socket.waitForConnected(200):
        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(200)
        return None
    QLocalServer.removeServer(name)
    server = QLocalServer()
    if not server.listen(name):
        return None
    return server


def _show_about(tr: Translator) -> None:
    QMessageBox.about(
        None,
        tr.t("app.title"),
        f"{tr.t('app.no_dsh')}\n\n{tr.t('about.version', version=__version__)}\n"
        f"{tr.t('about.license')}",
    )


def run_app(args, config: Config, store: SecretStore) -> int:
    if args.self_test:
        missing = [
            path
            for path in (ASSETS / "DSniang02.png", ASSETS / "DSniang1.png")
            if not path.exists()
        ]
        if missing:
            print("Missing assets: " + ", ".join(str(path) for path in missing))
            return 1
        QApplication(sys.argv[:1])
        print("self-test ok")
        return 0

    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("DeepSeekPet")
    setup_logging(Path(config.path.parent))
    tr = Translator(_language(config))

    interactive = args.fake_balance is None and args.screenshot is None
    server = None
    if interactive:
        server = _acquire_single_instance(f"DeepSeekPet-{getpass.getuser()}")
        if server is None:
            return 0

    if not config.get("first_run_done") and interactive:
        FirstRunDialog(config, tr, store).exec()
        tr = Translator(_language(config))

    service = BalanceService(config, store)
    window = PetWindow(config, tr, service)

    def open_settings() -> None:
        existing = getattr(window, "_settings_panel", None)
        if existing is not None and existing.isVisible():
            existing.close()
            return
        panel = CompactSettings(config, tr, store, window)
        panel.preview_size_changed.connect(window.preview_size)
        panel.preview_opacity_changed.connect(window.preview_opacity)
        panel.startup_changed.connect(on_startup_toggled)
        panel.refresh_requested.connect(service.refresh)
        window._settings_panel = panel
        panel.show_near(window)
        panel.show()

    def on_startup_toggled(checked: bool) -> None:
        try:
            set_startup(checked)
        except OSError:
            pass

    window.settings_requested.connect(open_settings)
    window.startup_toggled.connect(on_startup_toggled)
    window.hide_requested.connect(
        lambda: (window.hide(), QTimer.singleShot(3600_000, window.show))
    )
    window.about_requested.connect(lambda: _show_about(tr))
    window.quit_requested.connect(app.quit)

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = make_tray(window, tr)
        tray.show()

    if server is not None:
        server.newConnection.connect(lambda: (window.show(), window.raise_()))
        app._server = server  # keep the server alive for the app lifetime

    if args.fake_balance is not None:
        service.refresh(fake=Balance("CNY", args.fake_balance))
    elif interactive:
        service.refresh()

    if args.screenshot is not None:
        from PySide6.QtTest import QTest

        if args.fake_balance is None:
            service.refresh(fake=Balance("CNY", Decimal("123.45")))
        window.show_bubble()
        app.processEvents()
        QTest.qWait(1300)
        target = Path(args.screenshot)
        target.parent.mkdir(parents=True, exist_ok=True)
        window.grab().save(str(target))
        if tray is not None:
            tray.hide()
        return 0

    window.show()
    return app.exec()
