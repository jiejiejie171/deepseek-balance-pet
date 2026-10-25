import logging

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from .balance_client import Balance, BalanceError, fetch_balance
from .config import Config
from .key_source import resolve_key
from .logging_setup import redact
from .secrets_store import SecretStore

log = logging.getLogger("deepseek_pet")


class _Signals(QObject):
    ok = Signal(object)
    err = Signal(str, str)


class _Worker(QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.signals = _Signals()

    def run(self):
        try:
            self.signals.ok.emit(self.func())
        except BalanceError as exc:
            self.signals.err.emit(exc.kind, str(exc.status or ""))
        except Exception as exc:
            log.exception("unexpected balance error")
            self.signals.err.emit("unknown", redact(str(exc)))


class BalanceService(QObject):
    updated = Signal(object)
    failed = Signal(str, str)

    def __init__(self, config: Config, store: SecretStore, parent=None):
        super().__init__(parent)
        self.config = config
        self.store = store
        self._busy = False

    def refresh(self, fake: Balance | None = None) -> None:
        if fake is not None:
            self.updated.emit(fake)
            return
        if self._busy:
            return
        info = resolve_key(self.config, self.store)
        if info is None:
            self.failed.emit("no_key", "")
            return
        api = self.config.get("api", {})
        self._busy = True
        worker = _Worker(
            lambda: fetch_balance(
                info.key,
                base_url=api.get("base_url", "https://api.deepseek.com"),
                timeout=int(api.get("timeout_sec", 10)),
                proxy=api.get("proxy") or None,
            )
        )
        worker.signals.ok.connect(self._on_ok)
        worker.signals.err.connect(self._on_err)
        QThreadPool.globalInstance().start(worker)

    def _on_ok(self, balance) -> None:
        self._busy = False
        self.updated.emit(balance)

    def _on_err(self, kind: str, detail: str) -> None:
        self._busy = False
        self.failed.emit(kind, detail)
