from PySide6.QtCore import QObject, QRunnable, Signal

from ..balance_client import BalanceError, fetch_balance
from ..i18n import Translator

ERROR_KEYS = {
    "unauthorized": "error.unauthorized",
    "rate_limited": "error.rate_limited",
    "timeout": "error.timeout",
    "network": "error.network",
    "server": "error.server",
    "invalid_response": "error.invalid_response",
    "unknown": "error.unknown",
}


def error_reason(tr: Translator, kind: str, detail: str = "") -> str:
    key = ERROR_KEYS.get(kind, "error.unknown")
    if kind == "server" and detail:
        return tr.t(key, status=detail)
    return tr.t(key)


class KeyTestWorker(QRunnable):
    class Signals(QObject):
        ok = Signal(object)
        fail = Signal(str, str)

    def __init__(self, key: str, api: dict):
        super().__init__()
        self.key = key
        self.api = api
        self.signals = self.Signals()

    def run(self):
        try:
            balance = fetch_balance(
                self.key,
                base_url=self.api.get("base_url", "https://api.deepseek.com"),
                timeout=int(self.api.get("timeout_sec", 10)),
                proxy=self.api.get("proxy") or None,
            )
            self.signals.ok.emit(balance)
        except BalanceError as exc:
            self.signals.fail.emit(exc.kind, str(exc.status or ""))
        except Exception:  # noqa: BLE001
            self.signals.fail.emit("unknown", "")
