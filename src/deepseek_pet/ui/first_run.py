from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ..balance_client import format_amount
from ..config import Config
from ..i18n import Translator
from ..key_source import resolve_key
from ..secrets_store import SecretStore
from .key_test import KeyTestWorker, error_reason


def complete_first_run(config: Config, store, mode: str, key_text: str) -> None:
    key_text = (key_text or "").strip()
    if mode == "custom" and key_text:
        store.set_api_key(key_text)
        config.set("key_source", "custom")
    elif mode in ("custom", "env", "local"):
        if mode == "custom" and store.get_api_key() is None:
            config.set("key_source", "auto")
        else:
            config.set("key_source", mode)
    else:
        config.set("key_source", "auto")
    config.set("first_run_done", True)
    config.save()


class FirstRunDialog(QDialog):
    def __init__(self, config: Config, tr: Translator, store: SecretStore, parent=None):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.store = store
        self.detected = resolve_key(config, store)
        self.setWindowTitle(tr.t("first.title"))
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        title = QLabel(tr.t("first.title"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        no_dsh = QLabel(tr.t("app.no_dsh"))
        no_dsh.setStyleSheet(
            "background: #eaf4ff; color: #0e4c92; font-weight: bold; "
            "padding: 8px; border-radius: 6px;"
        )
        layout.addWidget(no_dsh)

        explanation = QLabel(tr.t("first.no_dsh"))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self.detected_label = QLabel()
        self.detected_label.setWordWrap(True)
        if self.detected:
            self.detected_label.setText(
                tr.t(
                    "first.detected",
                    source=tr.t(f"key.source.{self.detected.source}"),
                    masked=self.detected.masked,
                )
            )
        else:
            self.detected_label.setText(tr.t("key.source.none"))
        layout.addWidget(self.detected_label)

        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.Password)
        self.key_edit.setPlaceholderText(tr.t("key.placeholder"))
        layout.addWidget(self.key_edit)

        self.test_button = QPushButton(tr.t("key.test"))
        self.test_button.clicked.connect(self._test_key)
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        test_row = QHBoxLayout()
        test_row.addWidget(self.test_button)
        test_row.addWidget(self.result_label, 1)
        layout.addLayout(test_row)

        buttons = QHBoxLayout()
        if self.detected:
            use_detected = QPushButton(tr.t("first.use_detected"))
            use_detected.clicked.connect(self._use_detected)
            buttons.addWidget(use_detected)
        enter = QPushButton(tr.t("first.enter_key"))
        enter.clicked.connect(self._use_entered)
        buttons.addWidget(enter)
        skip = QPushButton(tr.t("first.skip"))
        skip.clicked.connect(self._skip)
        buttons.addWidget(skip)
        layout.addLayout(buttons)
        self.key_edit.returnPressed.connect(self._use_entered)

    def _current_key(self) -> str:
        text = self.key_edit.text().strip()
        if text:
            return text
        return self.detected.key if self.detected else ""

    def _test_key(self) -> None:
        key = self._current_key()
        if not key:
            self.result_label.setText(self.tr.t("test.need_key"))
            return
        self.test_button.setEnabled(False)
        self.result_label.setText(self.tr.t("key.testing"))
        worker = KeyTestWorker(key, self.config.get("api", {}))
        worker.signals.ok.connect(self._on_test_ok)
        worker.signals.fail.connect(self._on_test_fail)
        QThreadPool.globalInstance().start(worker)

    def _on_test_ok(self, balance) -> None:
        self.test_button.setEnabled(True)
        self.result_label.setText(
            self.tr.t("key.test_ok", amount=format_amount(balance.currency, balance.total))
        )

    def _on_test_fail(self, kind: str, detail: str) -> None:
        self.test_button.setEnabled(True)
        self.result_label.setText(
            self.tr.t("key.test_fail", reason=error_reason(self.tr, kind, detail))
        )

    def _use_detected(self) -> None:
        if self.detected:
            complete_first_run(self.config, self.store, self.detected.source, "")
            self.accept()

    def _use_entered(self) -> None:
        key = self.key_edit.text().strip()
        if not key:
            self.result_label.setText(self.tr.t("test.need_key"))
            return
        complete_first_run(self.config, self.store, "custom", key)
        self.accept()

    def _skip(self) -> None:
        complete_first_run(self.config, self.store, "skip", "")
        self.accept()
