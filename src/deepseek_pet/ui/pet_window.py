import math
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from PySide6.QtCore import (
    Property,
    QAbstractAnimation,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QPainter,
    QPen,
    QPixmap,
    QRegion,
    QTransform,
)
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from ..balance_client import Balance, format_amount
from ..config import Config
from ..i18n import Translator
from ..peak import peak_state
from ..sound import SoundPlayer
from ..usage import UsageTracker

ASSETS = Path(__file__).resolve().parents[1] / "assets"
STATUS_KEYS = {
    "no_key": "status.no_key",
    "unauthorized": "status.invalid_key",
    "rate_limited": "status.rate_limited",
    "server": "status.server_error",
    "timeout": "status.offline",
    "network": "status.offline",
    "invalid_response": "status.error",
    "unknown": "status.error",
}
CHAR_OFFSET = (414, 415)
CHAR_SIZE = 610
ASSET_SIZE = 1026
TITLE_COLOR = "#1b2a4a"
AMOUNT_COLOR = "#0e4c92"
PEAK_COLOR = "#c0392b"
OFFPEAK_COLOR = "#2f8f62"
STATUS_COLOR = "#6b7c93"
NEXT_COLOR = "#7a8699"
ERROR_STATUS_KEYS = {
    "status.no_key",
    "status.invalid_key",
    "status.rate_limited",
    "status.server_error",
    "status.error",
}
BUBBLE_FORM_MS = 750
BUBBLE_TEXT_START = 0.75
BUBBLE_TEXT_END = 1.0
BUBBLE_STAGES = (
    # name, center x/y (normalized), start/end progress
    ("small", 0.4332, 0.6301, 0.00, 0.18),
    ("mid", 0.3445, 0.5473, 0.14, 0.36),
    ("main", 0.4425, 0.2558, 0.30, 0.78),
)


class PetWindow(QWidget):
    settings_requested = Signal()
    startup_toggled = Signal(bool)
    hide_requested = Signal()
    about_requested = Signal()
    quit_requested = Signal()

    def __init__(self, config: Config, tr: Translator, service, parent=None):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.service = service
        self._char_pixmap = QPixmap(str(ASSETS / "DSniang1.png"))
        self._char_flipped = self._char_pixmap.transformed(QTransform().scale(-1, 1))
        self._bubble_pixmap = QPixmap(str(ASSETS / "whale_bubble.png"))
        self._bubble_parts = [
            (
                QPixmap(str(ASSETS / f"bubble_{name}.png")),
                center_x,
                center_y,
                start,
                end,
            )
            for name, center_x, center_y, start, end in BUBBLE_STAGES
        ]
        self._sound = SoundPlayer(ASSETS, bool(self.config.get("ui.sound_enabled", True)))
        self._usage = UsageTracker(config)
        self._balance: Balance | None = None
        self._display_total: Decimal | None = None
        self._status_key = "status.no_key"
        self._status_args: dict = {}
        self._last_success_time: datetime | None = None
        self._bubble_visible = False
        self._bubble_hiding = False
        self._bubble_progress = 0.0
        self._bubble_anim = None
        self._face_left = True
        self._bounce = 1.0
        self._idle_phase = 0.0
        self._drag_offset = None
        self._press_pos = None
        self._settings_pressed = False
        self._moved = False

        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.config.get("always_on_top", True):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(self.config.get("pet_size", 360), self.config.get("pet_size", 360))
        self.setWindowOpacity(self.config.get("opacity", 1.0))
        self._restore_last_balance()
        self._restore_position()
        self._update_facing()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.service.refresh)
        self._timer.start(int(self.config.get("refresh_interval_sec", 60)) * 1000)
        self._tick = QTimer(self)
        self._tick.timeout.connect(self._on_second)
        self._tick.start(1000)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_position)
        self._autohide_timer = QTimer(self)
        self._autohide_timer.setSingleShot(True)
        self._autohide_timer.timeout.connect(self.hide_bubble)
        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._tick_idle)
        self._bubble_anim = QPropertyAnimation(self, b"bubbleProgress", self)
        self._bubble_anim.finished.connect(self._on_bubble_anim_finished)
        self.service.updated.connect(self._on_balance)
        self.service.failed.connect(self._on_error)
        self._update_mask()

    # -- geometry ------------------------------------------------------
    def _char_rect(self) -> QRectF:
        scale = self.width() / ASSET_SIZE
        return QRectF(
            CHAR_OFFSET[0] * scale,
            CHAR_OFFSET[1] * scale,
            CHAR_SIZE * scale,
            CHAR_SIZE * scale,
        )

    def _settings_rect(self) -> QRectF:
        size = max(28.0, self.width() * 0.085)
        return QRectF(self.width() - size - 8, 8, size, size)

    def _char_for_facing(self) -> QPixmap:
        return self._char_pixmap if self._face_left else self._char_flipped

    # -- painting ------------------------------------------------------
    def _get_bounce(self) -> float:
        return self._bounce

    def _set_bounce(self, value: float) -> None:
        self._bounce = float(value)
        self.update()

    bounceScale = Property(float, _get_bounce, _set_bounce)

    def _get_bubble_progress(self) -> float:
        return self._bubble_progress

    def _set_bubble_progress(self, value: float) -> None:
        self._bubble_progress = max(0.0, min(1.0, float(value)))
        self.update()

    bubbleProgress = Property(float, _get_bubble_progress, _set_bubble_progress)

    @staticmethod
    def _stage_progress(progress: float, start: float, end: float) -> float:
        value = (progress - start) / (end - start)
        value = max(0.0, min(1.0, value))
        return value * value * (3.0 - 2.0 * value)

    def _make_font(self, point_size: float, weight=QFont.Normal) -> QFont:
        font = QFont("Microsoft YaHei UI")
        font.setPointSizeF(point_size)
        font.setWeight(weight)
        font.setStyleStrategy(QFont.PreferAntialias)
        font.setHintingPreference(QFont.PreferFullHinting)
        return font

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_mask()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._update_facing()

    def _update_facing(self) -> None:
        center = self.frameGeometry().center()
        screen = QApplication.screenAt(center) or QApplication.primaryScreen()
        if screen is None:
            return
        face_left = center.x() >= screen.availableGeometry().center().x()
        if face_left != self._face_left:
            self._face_left = face_left
            self._update_mask()
            self.update()

    def _update_mask(self) -> None:
        char_rect = self._char_rect()
        char = self._char_for_facing().scaled(
            char_rect.size().toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        region = QRegion(char.mask()).translated(int(char_rect.x()), int(char_rect.y()))
        if self._bubble_visible and self.config.get("show_bubble", True):
            bubble = self._bubble_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            region = region.united(QRegion(bubble.mask()))
        region = region.united(QRegion(self._settings_rect().toRect()))
        self.setMask(region)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        width, height = self.width(), self.height()
        scale = self._bounce
        if self.config.get("ui.idle_animation", True):
            scale *= 1.0 + 0.0028 * math.sin(self._idle_phase)
        painter.save()
        anchor = QPointF(width / 2, height)
        painter.translate(anchor)
        painter.scale(scale, scale)
        painter.translate(-anchor)

        painter.drawPixmap(
            self._char_rect(), self._char_for_facing(), QRectF(self._char_pixmap.rect())
        )
        if self._bubble_visible and self._bubble_progress > 0:
            progress = self._bubble_progress
            for pixmap, center_x, center_y, start, end in self._bubble_parts:
                stage = self._stage_progress(progress, start, end)
                if stage <= 0:
                    continue
                painter.save()
                painter.setOpacity(stage)
                center = QPointF(width * center_x, height * center_y)
                scale = 0.20 + 0.80 * stage
                painter.translate(center)
                painter.scale(scale, scale)
                painter.translate(-center)
                painter.drawPixmap(
                    QRectF(0, 0, width, height), pixmap, QRectF(pixmap.rect())
                )
                painter.restore()
            text_alpha = self._stage_progress(
                progress, BUBBLE_TEXT_START, BUBBLE_TEXT_END
            )
            if text_alpha > 0:
                painter.save()
                painter.setOpacity(text_alpha)
                self._paint_bubble_text(painter, width, height)
                painter.restore()

        self._paint_settings_button(painter)
        painter.restore()

    def _paint_bubble_text(self, painter: QPainter, width: int, height: int) -> None:
        inner = QRectF(width * 0.113, height * 0.035, width * 0.66, height * 0.38)
        title_rect = QRectF(
            inner.x(),
            inner.y() + inner.height() * 0.02,
            inner.width(),
            inner.height() * 0.22,
        )
        amount_rect = QRectF(
            inner.x(),
            inner.y() + inner.height() * 0.25,
            inner.width(),
            inner.height() * 0.30,
        )
        peak_rect = QRectF(
            inner.x(),
            inner.y() + inner.height() * 0.56,
            inner.width(),
            inner.height() * 0.20,
        )
        status_rect = QRectF(
            inner.x(),
            inner.y() + inner.height() * 0.78,
            inner.width(),
            inner.height() * 0.18,
        )

        self._draw_text(
            painter,
            title_rect,
            self.tr.t("bubble.title"),
            self._make_font(max(9.5, width * 0.030), QFont.DemiBold),
            QColor(TITLE_COLOR),
        )
        currency = self._balance.currency if self._balance else "CNY"
        amount = (
            self.tr.t("bubble.unknown")
            if self._display_total is None
            else format_amount(currency, self._display_total)
        )
        self._draw_text(
            painter,
            amount_rect,
            amount,
            self._make_font(max(16.0, width * 0.062), QFont.DemiBold),
            QColor(AMOUNT_COLOR),
        )
        peak = peak_state()
        badge_text = self._badge_text(peak)
        badge_font = self._make_font(max(9.5, width * 0.030), QFont.Bold)
        badge_text_width = QFontMetricsF(badge_font).horizontalAdvance(badge_text)
        badge_height = max(20.0, width * 0.060)
        badge_width = max(badge_height, badge_text_width + badge_height * 0.55)
        duration_font = self._make_font(max(8.0, width * 0.024))
        duration_text = self._remaining_text(peak)
        duration_width = QFontMetricsF(duration_font).horizontalAdvance(duration_text)
        gap = width * 0.012
        group_width = badge_width + gap + duration_width
        group_left = inner.center().x() - group_width / 2
        badge_rect = QRectF(
            group_left,
            peak_rect.center().y() - badge_height / 2,
            badge_width,
            badge_height,
        )
        duration_rect = QRectF(
            group_left + badge_width + gap,
            peak_rect.y(),
            duration_width,
            peak_rect.height(),
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(PEAK_COLOR if peak.is_peak else OFFPEAK_COLOR))
        painter.drawRoundedRect(badge_rect, badge_height * 0.15, badge_height * 0.15)
        self._draw_text(painter, badge_rect, badge_text, badge_font, QColor("#ffffff"))
        self._draw_text(
            painter,
            duration_rect,
            duration_text,
            duration_font,
            QColor(NEXT_COLOR),
            Qt.AlignLeft | Qt.AlignVCenter,
        )
        self._draw_text(
            painter,
            status_rect,
            self._bottom_text(),
            self._make_font(max(8.5, width * 0.026)),
            QColor(STATUS_COLOR),
        )

    @staticmethod
    def _draw_text(
        painter,
        rect,
        text,
        font,
        color,
        alignment=Qt.AlignHCenter | Qt.AlignVCenter,
    ) -> None:
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(rect, alignment, text)

    def _paint_settings_button(self, painter: QPainter) -> None:
        rect = self._settings_rect()
        painter.setPen(QPen(QColor(32, 49, 112, 70), 1))
        painter.setBrush(QColor(255, 255, 255, 235))
        painter.drawRoundedRect(rect, rect.width() * 0.3, rect.width() * 0.3)
        center = rect.center()
        radius = rect.width() * 0.30
        painter.setPen(
            QPen(
                QColor("#203170"),
                max(1.4, rect.width() * 0.07),
                Qt.SolidLine,
                Qt.RoundCap,
            )
        )
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius * 0.66, radius * 0.66)
        for index in range(8):
            angle = math.pi / 4 * index
            start = QPointF(
                center.x() + math.cos(angle) * radius * 0.66,
                center.y() + math.sin(angle) * radius * 0.66,
            )
            end = QPointF(
                center.x() + math.cos(angle) * radius * 1.08,
                center.y() + math.sin(angle) * radius * 1.08,
            )
            painter.drawLine(start, end)
        painter.drawEllipse(center, radius * 0.26, radius * 0.26)

    # -- state ---------------------------------------------------------
    def _badge_text(self, state) -> str:
        style = self.config.get("ui.peak_style", "mini")
        if style not in ("default", "liangwen", "qiangqiang", "mini"):
            style = "mini"
        suffix = "peak" if state.is_peak else "off"
        return self.tr.t(f"peak.badge_{style}_{suffix}")

    def _remaining_text(self, state) -> str:
        total = max(0, int(state.remaining.total_seconds()))
        minutes = round(total / 300.0) * 5
        if minutes <= 0:
            return self.tr.t("time.soon")
        if minutes < 60:
            return self.tr.t("time.in", duration=self.tr.t("time.minutes", n=minutes))
        hours, mins = divmod(minutes, 60)
        if hours < 24:
            duration = (
                self.tr.t("time.hours_minutes", h=hours, m=mins)
                if mins
                else self.tr.t("time.hours", h=hours)
            )
        else:
            days, rem_hours = divmod(hours, 24)
            duration = (
                self.tr.t("time.days_hours", d=days, h=rem_hours)
                if rem_hours
                else self.tr.t("time.days", d=days)
            )
        return self.tr.t("time.in", duration=duration)

    def _restore_last_balance(self) -> None:
        last = self.config.get("last_balance")
        if not isinstance(last, dict):
            return
        try:
            total = Decimal(str(last["total"]))
        except (KeyError, TypeError, InvalidOperation):
            return
        self._balance = Balance(str(last.get("currency") or "CNY"), total)
        self._display_total = total
        self._status_key = "status.ok"
        timestamp = last.get("timestamp")
        if isinstance(timestamp, str):
            try:
                self._last_success_time = datetime.fromisoformat(timestamp)
            except ValueError:
                self._last_success_time = None

    def _status_text(self) -> str:
        return self.tr.t(self._status_key, **self._status_args)

    def _usage_text(self) -> str:
        currency = self._balance.currency if self._balance else "CNY"
        return self.tr.t(
            "usage.today", amount=format_amount(currency, self._usage.spent)
        )

    def _bottom_text(self) -> str:
        if self._status_key in ERROR_STATUS_KEYS:
            return self._status_text()
        text = self._usage_text()
        if self._status_key == "status.offline":
            return f"{text} · {self.tr.t('status.offline_short')}"
        return text

    def _on_second(self) -> None:
        if self._bubble_visible:
            self.update()

    def _on_balance(self, balance) -> None:
        now = datetime.now()
        self._last_success_time = now
        self._status_key = "status.ok"
        self._status_args = {}
        self._usage.update(balance)
        self.config.set(
            "last_balance",
            {
                "currency": balance.currency,
                "total": str(balance.total),
                "timestamp": now.isoformat(timespec="seconds"),
            },
        )
        self.config.save()
        previous = self._display_total
        self._balance = balance
        animate = (
            self.config.get("ui.number_animation", True)
            and not self.config.get("ui.reduce_motion", False)
            and previous is not None
        )
        if animate:
            self._animate_to(previous, balance)
        else:
            self._display_total = balance.total
        self.update()

    def _animate_to(self, previous: Decimal, balance: Balance) -> None:
        animation = QVariantAnimation(self)
        animation.setDuration(500)
        animation.setStartValue(float(previous))
        animation.setEndValue(float(balance.total))
        animation.valueChanged.connect(self._on_animation_value)
        animation.finished.connect(lambda: self._set_final_total(balance.total))
        animation.start(QAbstractAnimation.DeleteWhenStopped)

    def _on_animation_value(self, value) -> None:
        self._display_total = Decimal(str(round(float(value), 2)))
        self.update()

    def _set_final_total(self, total: Decimal) -> None:
        self._display_total = total
        self.update()

    def _on_error(self, kind: str, detail: str) -> None:
        self._status_key = STATUS_KEYS.get(kind, "status.error")
        self._status_args = {}
        if kind == "server" and detail:
            self._status_args = {"status": detail}
        if kind in ("timeout", "network"):
            last = self._last_success_time.strftime("%H:%M") if self._last_success_time else "—"
            self._status_args = {"time": last}
        self.update()

    # -- bubble visibility ---------------------------------------------
    def is_bubble_visible(self) -> bool:
        return self._bubble_visible

    def _start_autohide_timer(self) -> None:
        seconds = int(self.config.get("ui.bubble_autohide_sec", 10))
        if seconds > 0:
            self._autohide_timer.start(seconds * 1000)
        else:
            self._autohide_timer.stop()

    def show_bubble(self) -> None:
        if not self.config.get("show_bubble", True):
            return
        if self._bubble_visible and not self._bubble_hiding:
            self._start_autohide_timer()
            self.update()
            return
        self._bubble_anim.stop()
        self._bubble_hiding = False
        self._bubble_visible = True
        self._update_mask()
        duration = max(180, int(BUBBLE_FORM_MS * (1.0 - self._bubble_progress)))
        self._bubble_anim.setDuration(duration)
        self._bubble_anim.setStartValue(self._bubble_progress)
        self._bubble_anim.setEndValue(1.0)
        self._bubble_anim.setEasingCurve(QEasingCurve.Linear)
        self._bubble_anim.start()
        self._start_autohide_timer()

    def hide_bubble(self, animate: bool = True) -> None:
        if not self._bubble_visible:
            return
        self._autohide_timer.stop()
        self._bubble_anim.stop()
        if not animate:
            self._bubble_hiding = False
            self._bubble_visible = False
            self._bubble_progress = 0.0
            self._update_mask()
            self.update()
            return
        self._bubble_hiding = True
        self._bubble_anim.setDuration(260)
        self._bubble_anim.setStartValue(self._bubble_progress)
        self._bubble_anim.setEndValue(0.0)
        self._bubble_anim.setEasingCurve(QEasingCurve.Linear)
        self._bubble_anim.start()

    def _on_bubble_anim_finished(self) -> None:
        if self._bubble_hiding:
            self._finish_hide()

    def _finish_hide(self) -> None:
        if not self._bubble_hiding:
            return
        self._bubble_hiding = False
        self._bubble_visible = False
        self._bubble_progress = 0.0
        self._update_mask()
        self.update()

    def _set_bubble_visible(self, checked: bool) -> None:
        if checked:
            self.show_bubble()
        else:
            self.hide_bubble()

    def refresh_now(self) -> None:
        self.service.refresh()
        self.show_bubble()
        animation = QPropertyAnimation(self, b"bounceScale", self)
        animation.setDuration(220)
        animation.setStartValue(1.04)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.start(QAbstractAnimation.DeleteWhenStopped)

    # -- interaction ---------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._settings_rect().contains(event.position()):
                self._settings_pressed = True
                self._press_pos = None
                self._drag_offset = None
                return
            self._sound.play_click()
            self._press_pos = event.globalPosition().toPoint()
            self._drag_offset = self._press_pos - self.frameGeometry().topLeft()
            self._moved = False
        elif event.button() == Qt.RightButton:
            self._show_menu(event.globalPosition().toPoint())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is None or not (event.buttons() & Qt.LeftButton):
            return
        position = event.globalPosition().toPoint()
        if not self._moved:
            if (position - self._press_pos).manhattanLength() <= 4:
                return
            self._moved = True
            self._drag_offset = self._press_pos - self.frameGeometry().topLeft()
        self.move(position - self._drag_offset)
        self._save_timer.start(500)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._settings_pressed:
                self._settings_pressed = False
                if self._settings_rect().contains(event.position()):
                    self.settings_requested.emit()
                return
            if self._press_pos is None:
                return
            was_moved = self._moved
            self._drag_offset = None
            self._press_pos = None
            if not was_moved:
                self.refresh_now()
            return
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        self._show_menu(event.globalPos())

    def _show_menu(self, position) -> None:
        menu = QMenu(self)
        menu.addAction(self.tr.t("menu.refresh"), self.refresh_now)
        menu.addAction(self.tr.t("menu.settings"), self.settings_requested.emit)
        size_menu = menu.addMenu(self.tr.t("menu.size"))
        for key, size in (
            ("menu.size.small", 240),
            ("menu.size.medium", 360),
            ("menu.size.large", 500),
        ):
            action = size_menu.addAction(self.tr.t(key))
            action.triggered.connect(lambda checked=False, s=size: self.set_pet_size(s))
        menu.addSeparator()
        bubble = menu.addAction(self.tr.t("menu.bubble"))
        bubble.setCheckable(True)
        bubble.setChecked(self._bubble_visible)
        bubble.setEnabled(bool(self.config.get("show_bubble", True)))
        bubble.toggled.connect(self._set_bubble_visible)
        startup = menu.addAction(self.tr.t("menu.startup"))
        startup.setCheckable(True)
        startup.setChecked(bool(self.config.get("startup", False)))
        startup.toggled.connect(self._set_startup)
        menu.addAction(self.tr.t("menu.hide"), self.hide_requested.emit)
        menu.addAction(self.tr.t("menu.about"), self.about_requested.emit)
        menu.addSeparator()
        menu.addAction(self.tr.t("menu.quit"), self.quit_requested.emit)
        menu.exec(position)

    def _set_startup(self, checked: bool) -> None:
        self.config.set("startup", bool(checked))
        self.config.save()
        self.startup_toggled.emit(bool(checked))

    # -- live preview ---------------------------------------------------
    def preview_size(self, size: int) -> None:
        size = max(240, min(600, int(size)))
        screen = QApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        center = self.frameGeometry().center()
        self.resize(size, size)
        x = center.x() - size // 2
        y = center.y() - size // 2
        if screen is not None:
            available = screen.availableGeometry()
            x = max(available.left(), min(x, available.right() - size + 1))
            y = max(available.top(), min(y, available.bottom() - size + 1))
        self.move(x, y)
        self.update()

    def preview_opacity(self, opacity: float) -> None:
        self.setWindowOpacity(max(0.6, min(1.0, float(opacity))))

    def save_position(self) -> None:
        self._save_position()

    # -- configuration -------------------------------------------------
    def set_pet_size(self, size: int) -> None:
        size = max(240, min(600, int(size)))
        self.config.set("pet_size", size)
        self.config.save()
        self.resize(size, size)
        self.update()

    def apply_config(self) -> None:
        self.resize(
            int(self.config.get("pet_size", 360)), int(self.config.get("pet_size", 360))
        )
        self.setWindowOpacity(float(self.config.get("opacity", 1.0)))
        self._timer.setInterval(int(self.config.get("refresh_interval_sec", 60)) * 1000)
        top = bool(self.config.get("always_on_top", True))
        if bool(self.windowFlags() & Qt.WindowStaysOnTopHint) != top:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, top)
            self.show()
        self._sound.enabled = bool(self.config.get("ui.sound_enabled", True))
        if not self.config.get("show_bubble", True):
            self.hide_bubble(animate=False)
        elif self._bubble_visible:
            self._start_autohide_timer()
        self._update_idle_timer()
        self.update()

    # -- animation -----------------------------------------------------
    def _tick_idle(self) -> None:
        if not self.isVisible():
            return
        self._idle_phase = (self._idle_phase + 0.02) % (2 * math.pi)
        self.update()

    def _update_idle_timer(self) -> None:
        if not self.config.get("ui.idle_animation", True):
            self._idle_timer.stop()
        elif self.isVisible() and not self._idle_timer.isActive():
            self._idle_timer.start(16)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_idle_timer()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._idle_timer.stop()

    # -- position ------------------------------------------------------
    def _restore_position(self) -> None:
        x = self.config.get("position.x")
        y = self.config.get("position.y")
        if isinstance(x, int) and isinstance(y, int):
            from PySide6.QtCore import QRect

            rect = QRect(x, y, self.width(), self.height())
            if any(screen.availableGeometry().intersects(rect) for screen in QApplication.screens()):
                self.move(x, y)
                return
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 40, screen.bottom() - self.height() - 60)

    def _save_position(self) -> None:
        self.config.set("position.x", self.x())
        self.config.set("position.y", self.y())
        self.config.save()

    def reset_position(self) -> None:
        self.config.set("position.x", None)
        self.config.set("position.y", None)
        self.config.save()
        self._restore_position()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
