from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..balance_client import format_amount
from ..config import Config
from ..i18n import Translator
from ..key_source import resolve_key
from ..secrets_store import SecretStore
from .key_test import KeyTestWorker, error_reason

PANEL_QSS = """
QFrame#panel {
    background: rgba(255, 255, 255, 0.97);
    border: 1px solid rgba(32, 49, 112, 0.35);
    border-radius: 10px;
}
QLabel { color: #203170; font-size: 12px; }
QLabel#hint { color: rgba(32, 49, 112, 0.62); font-size: 10px; }
QCheckBox { color: #203170; font-size: 12px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QCheckBox::indicator:unchecked {
    border: 1px solid rgba(32, 49, 112, 0.45);
    border-radius: 3px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    border: 1px solid #203170;
    border-radius: 3px;
    background: #203170;
}
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(32, 49, 112, 0.16);
    border-radius: 2px;
}
QSlider::sub-page:horizontal { background: #203170; border-radius: 2px; }
QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
    background: #203170;
}
QSpinBox, QComboBox {
    background: rgba(32, 49, 112, 0.07);
    border: 1px solid rgba(32, 49, 112, 0.25);
    border-radius: 6px;
    padding: 2px 6px;
    color: #203170;
    font-size: 12px;
}
QPushButton {
    background: rgba(32, 49, 112, 0.08);
    border: 1px solid rgba(32, 49, 112, 0.25);
    border-radius: 6px;
    color: #203170;
    font-size: 12px;
    padding: 3px 8px;
}
QPushButton:hover { background: rgba(32, 49, 112, 0.16); }
QPushButton#ver {
    background: transparent;
    border: none;
    color: rgba(32, 49, 112, 0.5);
    font-size: 9px;
    padding: 0;
}
QPushButton#ver:hover { color: rgba(32, 49, 112, 0.85); }
QPushButton#close {
    background: transparent;
    border: none;
    color: #203170;
    font-size: 16px;
    padding: 0;
}
QPushButton#close:hover { color: #c0392b; }
QFrame#sep { background: rgba(32, 49, 112, 0.25); max-height: 1px; border: none; }
"""


def apply_account(config: Config, store, mode: str, key_text: str) -> None:
    mode = mode if mode in ("auto", "custom", "env", "claude") else "auto"
    key_text = (key_text or "").strip()
    if key_text:
        store.set_api_key(key_text)
        config.set("key_source", "custom")
        return
    if mode == "custom" and store.get_api_key() is None:
        config.set("key_source", "auto")
    else:
        config.set("key_source", mode)


def clear_custom_key(config: Config, store) -> None:
    store.clear()
    if config.get("key_source") == "custom":
        config.set("key_source", "auto")


class AccountDialog(QDialog):
    saved = Signal()

    def __init__(self, config: Config, tr: Translator, store: SecretStore, parent=None):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.store = store
        self.setWindowTitle(tr.t("account.title"))
        self.setMinimumWidth(440)

        form = QFormLayout(self)
        self.current_label = QLabel()
        self.current_label.setWordWrap(True)
        form.addRow(self.current_label)

        self.source_combo = QComboBox()
        for value, key in (
            ("auto", "key.source.auto"),
            ("custom", "key.source.custom"),
            ("env", "key.source.env"),
            ("claude", "key.source.claude"),
        ):
            self.source_combo.addItem(tr.t(key), value)
        index = self.source_combo.findData(config.get("key_source", "auto"))
        self.source_combo.setCurrentIndex(max(0, index))
        form.addRow(tr.t("key.source"), self.source_combo)

        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.Password)
        self.key_edit.setPlaceholderText(tr.t("key.placeholder"))
        self.show_button = QPushButton(tr.t("key.show"))
        self.show_button.setCheckable(True)
        self.show_button.toggled.connect(self._toggle_key_visibility)
        key_row = QHBoxLayout()
        key_row.setContentsMargins(0, 0, 0, 0)
        key_row.addWidget(self.key_edit)
        key_row.addWidget(self.show_button)
        key_widget = QWidget()
        key_widget.setLayout(key_row)
        form.addRow(tr.t("key.label"), key_widget)

        self.test_button = QPushButton(tr.t("key.test"))
        self.test_button.clicked.connect(self._test_key)
        self.test_result = QLabel("")
        self.test_result.setWordWrap(True)
        test_row = QHBoxLayout()
        test_row.setContentsMargins(0, 0, 0, 0)
        test_row.addWidget(self.test_button)
        test_row.addWidget(self.test_result, 1)
        test_widget = QWidget()
        test_widget.setLayout(test_row)
        form.addRow(test_widget)

        self.clear_button = QPushButton(tr.t("key.clear"))
        self.clear_button.clicked.connect(self._clear_key)
        form.addRow(self.clear_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr.t("common.save"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr.t("common.cancel"))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._refresh_current_label()

    def _refresh_current_label(self) -> None:
        info = resolve_key(self.config, self.store)
        if info is None:
            text = self.tr.t("key.current", source=self.tr.t("key.source.none"), masked="—")
        else:
            text = self.tr.t(
                "key.current",
                source=self.tr.t(f"key.source.{info.source}"),
                masked=info.masked,
            )
        self.current_label.setText(text)

    def _toggle_key_visibility(self, checked: bool) -> None:
        self.key_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.show_button.setText(self.tr.t("key.hide" if checked else "key.show"))

    def _test_key(self) -> None:
        key = self.key_edit.text().strip()
        if not key:
            info = resolve_key(self.config, self.store)
            key = info.key if info else ""
        if not key:
            self.test_result.setText(self.tr.t("test.need_key"))
            return
        self.test_button.setEnabled(False)
        self.test_result.setText(self.tr.t("key.testing"))
        worker = KeyTestWorker(key, self.config.get("api", {}))
        worker.signals.ok.connect(self._on_test_ok)
        worker.signals.fail.connect(self._on_test_fail)
        QThreadPool.globalInstance().start(worker)

    def _on_test_ok(self, balance) -> None:
        self.test_button.setEnabled(True)
        self.test_result.setText(
            self.tr.t("key.test_ok", amount=format_amount(balance.currency, balance.total))
        )

    def _on_test_fail(self, kind: str, detail: str) -> None:
        self.test_button.setEnabled(True)
        self.test_result.setText(
            self.tr.t("key.test_fail", reason=error_reason(self.tr, kind, detail))
        )

    def _clear_key(self) -> None:
        clear_custom_key(self.config, self.store)
        self.config.save()
        self.key_edit.clear()
        self._refresh_current_label()
        self.test_result.setText(self.tr.t("key.cleared"))

    def _save(self) -> None:
        apply_account(
            self.config,
            self.store,
            self.source_combo.currentData(),
            self.key_edit.text(),
        )
        self.config.save()
        self.saved.emit()
        self.accept()


class AdvancedDialog(QDialog):
    def __init__(self, config: Config, tr: Translator, parent=None):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.setWindowTitle(tr.t("advanced.title"))
        self.setMinimumWidth(420)

        form = QFormLayout(self)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(3, 60)
        self.timeout_spin.setSuffix(f" {tr.t('common.seconds')}")
        self.timeout_spin.setValue(int(config.get("api.timeout_sec", 10)))
        form.addRow(tr.t("behavior.timeout"), self.timeout_spin)

        self.proxy_edit = QLineEdit(str(config.get("api.proxy", "")))
        form.addRow(tr.t("behavior.proxy"), self.proxy_edit)

        self.base_url_edit = QLineEdit(
            str(config.get("api.base_url", "https://api.deepseek.com"))
        )
        form.addRow(tr.t("behavior.base_url"), self.base_url_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText(tr.t("common.save"))
        buttons.button(QDialogButtonBox.Cancel).setText(tr.t("common.cancel"))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _save(self) -> None:
        self.config.set("api.timeout_sec", self.timeout_spin.value())
        self.config.set("api.proxy", self.proxy_edit.text().strip())
        base_url = self.base_url_edit.text().strip() or "https://api.deepseek.com"
        self.config.set("api.base_url", base_url.rstrip("/"))
        self.config.save()
        self.accept()


class CompactSettings(QDialog):
    preview_size_changed = Signal(int)
    preview_opacity_changed = Signal(float)
    startup_changed = Signal(bool)
    refresh_requested = Signal()

    def __init__(
        self,
        config: Config,
        tr: Translator,
        store: SecretStore,
        window=None,
        parent=None,
    ):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.store = store
        self.window = window
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(320)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setStyleSheet(PANEL_QSS)
        outer.addWidget(panel)
        self._layout = QVBoxLayout(panel)
        self._layout.setContentsMargins(12, 10, 12, 6)
        self._layout.setSpacing(4)

        header = QWidget()
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(4)
        title = QLabel(tr.t("settings.title"))
        title.setStyleSheet("font-size: 13px; font-weight: 600;")
        close_button = QPushButton("×")
        close_button.setObjectName("close")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        header_row.addWidget(title)
        header_row.addStretch(1)
        header_row.addWidget(close_button)
        self._layout.addWidget(header)

        self._build_rows()
        self.adjustSize()

    # -- layout helpers -------------------------------------------------
    def _add_row(self, label_text: str, widgets, stretch_index=None) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(QLabel(label_text))
        if stretch_index is None:
            layout.addStretch(1)
        for index, widget in enumerate(widgets):
            if index == stretch_index:
                layout.addWidget(widget, 1)
            else:
                layout.addWidget(widget)
        self._layout.addWidget(row)
        return row

    def _add_toggle(self, label_text: str, checked: bool, callback) -> QCheckBox:
        check = QCheckBox()
        check.setChecked(checked)
        check.toggled.connect(callback)
        self._add_row(label_text, [check])
        return check

    def _add_separator(self) -> None:
        line = QFrame()
        line.setObjectName("sep")
        line.setFixedHeight(1)
        self._layout.addWidget(line)

    def _add_hint(self, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("hint")
        label.setWordWrap(True)
        self._layout.addWidget(label)

    # -- rows -----------------------------------------------------------
    def _build_rows(self) -> None:
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(240, 600)
        self.size_slider.setValue(int(self.config.get("pet_size", 360)))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(240, 600)
        self.size_spin.setValue(int(self.config.get("pet_size", 360)))
        self.size_spin.setFixedWidth(76)
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self._size_changed)
        self._add_row(self.tr.t("appearance.size"), [self.size_slider, self.size_spin], 0)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(60, 100)
        self.opacity_slider.setValue(int(float(self.config.get("opacity", 1.0)) * 100))
        self.opacity_value = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_value.setFixedWidth(38)
        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_value.setText(f"{value}%")
        )
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        self._add_row(
            self.tr.t("appearance.opacity"),
            [self.opacity_slider, self.opacity_value],
            0,
        )

        self._add_toggle(
            self.tr.t("appearance.bubble"),
            bool(self.config.get("show_bubble", True)),
            lambda checked: self._set_config("show_bubble", checked),
        )
        self._add_toggle(
            self.tr.t("behavior.sound"),
            bool(self.config.get("ui.sound_enabled", True)),
            lambda checked: self._set_ui("sound_enabled", checked),
        )
        self._add_toggle(
            self.tr.t("appearance.idle_animation"),
            bool(self.config.get("ui.idle_animation", True)),
            lambda checked: self._set_ui("idle_animation", checked),
        )
        self._add_toggle(
            self.tr.t("appearance.animation"),
            bool(self.config.get("ui.number_animation", True)),
            lambda checked: self._set_ui("number_animation", checked),
        )
        self._add_toggle(
            self.tr.t("appearance.reduce_motion"),
            bool(self.config.get("ui.reduce_motion", False)),
            lambda checked: self._set_ui("reduce_motion", checked),
        )

        self.autohide_spin = QSpinBox()
        self.autohide_spin.setRange(0, 120)
        self.autohide_spin.setSuffix(f" {self.tr.t('common.seconds')}")
        self.autohide_spin.setValue(int(self.config.get("ui.bubble_autohide_sec", 10)))
        self.autohide_spin.valueChanged.connect(
            lambda value: self._set_ui("bubble_autohide_sec", value)
        )
        self._add_row(self.tr.t("appearance.autohide"), [self.autohide_spin])

        self.peak_style_combo = QComboBox()
        for value, key in (
            ("default", "peak.style.default"),
            ("liangwen", "peak.style.liangwen"),
            ("qiangqiang", "peak.style.qiangqiang"),
            ("mini", "peak.style.mini"),
        ):
            self.peak_style_combo.addItem(self.tr.t(key), value)
        index = self.peak_style_combo.findData(self.config.get("ui.peak_style", "mini"))
        self.peak_style_combo.setCurrentIndex(max(0, index))
        self.peak_style_combo.currentIndexChanged.connect(self._peak_style_changed)
        self._add_row(self.tr.t("peak.style"), [self.peak_style_combo])

        self._add_separator()

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(30, 600)
        self.interval_spin.setSuffix(f" {self.tr.t('common.seconds')}")
        self.interval_spin.setValue(int(self.config.get("refresh_interval_sec", 60)))
        self.interval_spin.valueChanged.connect(
            lambda value: self._set_interval(value)
        )
        self._add_row(self.tr.t("behavior.interval"), [self.interval_spin])

        self._add_toggle(
            self.tr.t("behavior.startup"),
            bool(self.config.get("startup", False)),
            self._startup_changed,
        )
        self._add_toggle(
            self.tr.t("behavior.top"),
            bool(self.config.get("always_on_top", True)),
            lambda checked: self._set_config("always_on_top", checked),
        )

        self.language_combo = QComboBox()
        for value, key in (
            ("auto", "behavior.language.auto"),
            ("zh", "behavior.language.zh"),
            ("en", "behavior.language.en"),
        ):
            self.language_combo.addItem(self.tr.t(key), value)
        index = self.language_combo.findData(self.config.get("language", "auto"))
        self.language_combo.setCurrentIndex(max(0, index))
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        self._add_row(self.tr.t("behavior.language"), [self.language_combo])
        self._add_hint(self.tr.t("behavior.language_restart"))

        self.advanced_button = QPushButton(self.tr.t("advanced.manage"))
        self.advanced_button.clicked.connect(self._open_advanced)
        self._add_row(self.tr.t("advanced.title"), [self.advanced_button])

        self._add_separator()

        self.account_button = QPushButton(self.tr.t("key.manage"))
        self.account_button.clicked.connect(self._open_account)
        self._add_row(self.tr.t("account.title"), [self.account_button])
        self.account_current = QLabel()
        self.account_current.setObjectName("hint")
        self.account_current.setWordWrap(True)
        self._layout.addWidget(self.account_current)
        self._refresh_account_label()

        self.reset_button = QPushButton(self.tr.t("appearance.reset_position"))
        self.reset_button.clicked.connect(self._reset_position)
        self._add_row(self.tr.t("appearance.position"), [self.reset_button])

        version = QPushButton(f"v{__version__}")
        version.setObjectName("ver")
        version.setFlat(True)
        version.setCursor(Qt.PointingHandCursor)
        version.clicked.connect(self._show_about)
        version_row = QHBoxLayout()
        version_row.addStretch(1)
        version_row.addWidget(version)
        version_row.addStretch(1)
        self._layout.addLayout(version_row)

    # -- handlers -------------------------------------------------------
    def _size_changed(self, value: int) -> None:
        self.config.set("pet_size", int(value))
        self.config.save()
        self.preview_size_changed.emit(int(value))

    def _opacity_changed(self, value: int) -> None:
        self.config.set("opacity", value / 100.0)
        self.config.save()
        self.preview_opacity_changed.emit(value / 100.0)

    def _set_ui(self, key: str, value) -> None:
        self.config.set(f"ui.{key}", value)
        self.config.save()
        self._apply()

    def _set_config(self, key: str, value) -> None:
        self.config.set(key, value)
        self.config.save()
        self._apply()

    def _set_interval(self, value: int) -> None:
        self.config.set("refresh_interval_sec", int(value))
        self.config.save()
        self._apply()

    def _startup_changed(self, checked: bool) -> None:
        self.config.set("startup", bool(checked))
        self.config.save()
        self.startup_changed.emit(bool(checked))
        self._apply()

    def _peak_style_changed(self, _index: int = 0) -> None:
        self.config.set("ui.peak_style", self.peak_style_combo.currentData())
        self.config.save()
        if self.window is not None:
            self.window.update()

    def _language_changed(self, _index: int = 0) -> None:
        self.config.set("language", self.language_combo.currentData())
        self.config.save()

    def _apply(self) -> None:
        if self.window is not None:
            self.window.apply_config()

    def _reset_position(self) -> None:
        if self.window is not None:
            self.window.reset_position()

    def _refresh_account_label(self) -> None:
        info = resolve_key(self.config, self.store)
        if info is None:
            text = self.tr.t("key.current", source=self.tr.t("key.source.none"), masked="—")
        else:
            text = self.tr.t(
                "key.current",
                source=self.tr.t(f"key.source.{info.source}"),
                masked=info.masked,
            )
        self.account_current.setText(text)

    def _open_account(self) -> None:
        self.hide()
        parent = self.window if self.window is not None else None
        dialog = AccountDialog(self.config, self.tr, self.store, parent)
        if dialog.exec():
            self._refresh_account_label()
            self.refresh_requested.emit()
        self.show()

    def _open_advanced(self) -> None:
        self.hide()
        parent = self.window if self.window is not None else None
        dialog = AdvancedDialog(self.config, self.tr, parent)
        if dialog.exec():
            self.refresh_requested.emit()
            self._apply()
        self.show()

    def _show_about(self) -> None:
        self.hide()
        QMessageBox.about(
            self.window if self.window is not None else self,
            self.tr.t("app.title"),
            f"{self.tr.t('app.no_dsh')}\n\n"
            f"{self.tr.t('about.version', version=__version__)}\n"
            f"{self.tr.t('about.license')}",
        )
        self.show()

    def show_near(self, anchor: QWidget) -> None:
        self.adjustSize()
        screen = QApplication.screenAt(anchor.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else self.screen().availableGeometry()
        x = anchor.geometry().right() - self.width() + 1
        y = anchor.geometry().top() + 8
        if y + self.height() > available.bottom():
            y = max(available.top(), anchor.geometry().top() - self.height() - 8)
        x = max(available.left(), min(x, available.right() - self.width() + 1))
        self.move(x, y)
