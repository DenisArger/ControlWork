from __future__ import annotations

import time
from dataclasses import replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..i18n import (
    IrregularVerb,
    ThemedQuote,
    format_thematic_quote_author,
    random_irregular_verb,
    random_thematic_quote,
    tr,
)
from ..models import AppSettings, REMINDER_TONES, TrackerState


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class FirstRunDialog(QDialog):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.setModal(True)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["ru", "en"])
        self.lang_combo.setCurrentText(settings.language)

        self.soft_edit = QLineEdit(",".join(str(v) for v in settings.soft_points_min))
        self.hard_edit = QLineEdit(",".join(str(v) for v in settings.hard_points_min))

        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 180)
        self.break_spin.setValue(settings.break_duration_min)

        self.tone_combo = QComboBox()
        for tone in REMINDER_TONES:
            self.tone_combo.addItem(tone, tone)
        tone_idx = self.tone_combo.findData(settings.reminder_tone)
        if tone_idx >= 0:
            self.tone_combo.setCurrentIndex(tone_idx)

        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(30, 3600)
        self.idle_spin.setValue(settings.idle_threshold_sec)

        self.autostart_check = QCheckBox()
        self.autostart_check.setChecked(settings.autostart_enabled)

        form = QFormLayout()
        form.addRow("language", self.lang_combo)
        form.addRow("soft", self.soft_edit)
        form.addRow("hard", self.hard_edit)
        form.addRow("break(min)", self.break_spin)
        form.addRow("tone", self.tone_combo)
        form.addRow("idle(sec)", self.idle_spin)
        form.addRow("autostart", self.autostart_check)

        apply_btn = QPushButton("apply")
        apply_btn.clicked.connect(self._on_apply)

        root = QVBoxLayout()
        root.addLayout(form)
        root.addWidget(apply_btn)
        self.setLayout(root)
        self._retranslate(settings.language)

    def _retranslate(self, language: str) -> None:
        self.setWindowTitle(tr(language, "first_run_title"))
        for idx, tone in enumerate(REMINDER_TONES):
            self.tone_combo.setItemText(idx, tr(language, "tone_" + tone))

    def _on_apply(self) -> None:
        soft_points = _parse_points(self.soft_edit.text())
        hard_points = _parse_points(self.hard_edit.text())
        if not soft_points or not hard_points:
            QMessageBox.warning(self, "Error", tr(self.settings.language, "parse_error"))
            return
        self.settings.language = self.lang_combo.currentText()  # type: ignore[assignment]
        self.settings.soft_points_min = soft_points
        self.settings.hard_points_min = hard_points
        self.settings.break_duration_min = self.break_spin.value()
        self.settings.reminder_tone = str(self.tone_combo.currentData() or "friendly")
        self.settings.idle_threshold_sec = self.idle_spin.value()
        self.settings.autostart_enabled = self.autostart_check.isChecked()
        self.settings.normalize()
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setModal(True)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["ru", "en"])

        self.autostart_checkbox = QCheckBox()
        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(30, 3600)

        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 180)

        self.tone_combo = QComboBox()
        for tone in REMINDER_TONES:
            self.tone_combo.addItem(tone, tone)

        self.soft_edit = QLineEdit()
        self.hard_edit = QLineEdit()
        self.reset_edit = QLineEdit()

        form = QFormLayout()
        self.language_label = QLabel()
        self.autostart_label = QLabel()
        self.idle_label = QLabel()
        self.break_label = QLabel()
        self.tone_label = QLabel()
        self.soft_label = QLabel()
        self.hard_label = QLabel()
        self.reset_label = QLabel()

        form.addRow(self.language_label, self.language_combo)
        form.addRow(self.autostart_label, self.autostart_checkbox)
        form.addRow(self.idle_label, self.idle_spin)
        form.addRow(self.break_label, self.break_spin)
        form.addRow(self.tone_label, self.tone_combo)
        form.addRow(self.soft_label, self.soft_edit)
        form.addRow(self.hard_label, self.hard_edit)
        form.addRow(self.reset_label, self.reset_edit)

        self.cancel_btn = QPushButton()
        self.save_btn = QPushButton()
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)

        buttons = QHBoxLayout()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.save_btn)

        root = QVBoxLayout()
        root.addLayout(form)
        root.addLayout(buttons)
        self.setLayout(root)

        self.set_settings(settings)
        self.retranslate()

    def set_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self.language_combo.setCurrentText(settings.language)
        self.autostart_checkbox.setChecked(settings.autostart_enabled)
        self.idle_spin.setValue(settings.idle_threshold_sec)
        self.break_spin.setValue(settings.break_duration_min)
        tone_idx = self.tone_combo.findData(settings.reminder_tone)
        if tone_idx >= 0:
            self.tone_combo.setCurrentIndex(tone_idx)
        self.soft_edit.setText(",".join(str(v) for v in settings.soft_points_min))
        self.hard_edit.setText(",".join(str(v) for v in settings.hard_points_min))
        self.reset_edit.setText(settings.workday_reset_time)

    def retranslate(self) -> None:
        lang = self.settings.language
        self.setWindowTitle(tr(lang, "menu_settings"))
        self.language_label.setText(tr(lang, "settings_language"))
        self.autostart_label.setText(tr(lang, "settings_autostart"))
        self.idle_label.setText(tr(lang, "settings_idle"))
        self.break_label.setText(tr(lang, "settings_break"))
        self.tone_label.setText(tr(lang, "settings_tone"))
        self.soft_label.setText(tr(lang, "settings_soft"))
        self.hard_label.setText(tr(lang, "settings_hard"))
        self.reset_label.setText(tr(lang, "settings_reset"))
        self.cancel_btn.setText(tr(lang, "btn_cancel"))
        self.save_btn.setText(tr(lang, "settings_save"))
        for idx, tone in enumerate(REMINDER_TONES):
            self.tone_combo.setItemText(idx, tr(lang, "tone_" + tone))

    def _on_save(self) -> None:
        soft_points = _parse_points(self.soft_edit.text())
        hard_points = _parse_points(self.hard_edit.text())
        if not soft_points or not hard_points:
            QMessageBox.warning(self, "Error", tr(self.settings.language, "parse_error"))
            return

        next_settings = replace(
            self.settings,
            language=self.language_combo.currentText(),
            autostart_enabled=self.autostart_checkbox.isChecked(),
            idle_threshold_sec=self.idle_spin.value(),
            break_duration_min=self.break_spin.value(),
            reminder_tone=str(self.tone_combo.currentData() or "friendly"),
            soft_points_min=soft_points,
            hard_points_min=hard_points,
            workday_reset_time=self.reset_edit.text().strip() or "04:00",
        )
        next_settings.normalize()
        self.settings = next_settings
        self.accept()


class MainWindow(QMainWindow):
    pause_toggle_requested = Signal()

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._size_with_learning_block = (248, 182)
        self._size_without_learning_block = (210, 120)
        self._min_height_with_learning_block = 170
        self._max_height_with_learning_block = 260
        self.settings = settings
        self._hide_to_tray_enabled = True
        self._learning_block_visible = True
        self._last_learning_slot: int | None = None
        self._current_quote: ThemedQuote | None = None
        self._current_verb: IrregularVerb | None = None
        self._last_work_seconds = 0
        self._last_until_break_seconds: int | None = None
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setFixedSize(*self._size_with_learning_block)

        body = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        timers_layout = QVBoxLayout()
        timers_layout.setContentsMargins(0, 0, 0, 0)
        timers_layout.setSpacing(0)

        self.state_label = QLabel()
        self.work_time_label = QLabel()
        self.until_break_label = QLabel()
        self.toggle_learning_btn = QPushButton()
        self.quote_label = ClickableLabel()
        self.pause_btn = QPushButton()
        self.toggle_learning_btn.setFixedHeight(19)
        self.pause_btn.setFixedHeight(21)
        self.pause_btn.clicked.connect(self.pause_toggle_requested.emit)
        self.toggle_learning_btn.clicked.connect(self._toggle_learning_block)
        self.quote_label.clicked.connect(self._on_quote_click)
        self.quote_label.setWordWrap(True)
        self.quote_label.setCursor(Qt.PointingHandCursor)

        self.state_label.setStyleSheet("font-size: 12px; font-weight: 600;")
        self.work_time_label.setStyleSheet("font-size: 12px;")
        self.until_break_label.setStyleSheet("font-size: 12px;")
        self.quote_label.setStyleSheet(
            "font-size: 11px; color: #243447; background: #eef3f7; border: 1px solid #d0d8e0; border-radius: 5px; padding: 4px;"
        )
        self.toggle_learning_btn.setStyleSheet(
            "font-size: 11px; border: 1px solid #b7c3cf; border-radius: 5px; padding: 0px 6px;"
        )
        self.pause_btn.setStyleSheet(
            "font-size: 12px; border: 1px solid #9aa7b6; border-radius: 6px; padding: 1px 8px;"
        )

        self.state_label.setMargin(0)
        self.work_time_label.setMargin(0)
        self.until_break_label.setMargin(0)

        layout.addWidget(self.state_label)
        timers_layout.addWidget(self.work_time_label)
        timers_layout.addWidget(self.until_break_label)
        layout.addLayout(timers_layout)
        layout.addWidget(self.toggle_learning_btn)
        layout.addWidget(self.quote_label)
        layout.addWidget(self.pause_btn)

        body.setLayout(layout)
        self.setCentralWidget(body)

        self.retranslate()
        self._apply_learning_block_visibility()
        self.refresh_learning_block(force=True)

    def set_settings(self, settings: AppSettings) -> None:
        self.settings = settings

    def set_hide_to_tray_enabled(self, enabled: bool) -> None:
        self._hide_to_tray_enabled = enabled

    def retranslate(self) -> None:
        lang = self.settings.language
        self.setWindowTitle(tr(lang, "app_title"))
        self.pause_btn.setText(tr(lang, "menu_pause"))
        self.toggle_learning_btn.setText(
            tr(lang, "btn_hide_quotes") if self._learning_block_visible else tr(lang, "btn_show_quotes")
        )
        self.update_timers(self._last_work_seconds, self._last_until_break_seconds)
        self.refresh_learning_block(force=True)

    def update_state(self, state: TrackerState) -> None:
        key_map = {
            TrackerState.ACTIVE: "state_active",
            TrackerState.IDLE: "state_idle",
            TrackerState.BREAK: "state_break",
            TrackerState.PAUSED: "state_paused",
        }
        state_text = tr(self.settings.language, key_map[state])
        self.state_label.setText(f"{tr(self.settings.language, 'status_title')}: {state_text}")
        self.pause_btn.setText(
            tr(self.settings.language, "menu_resume")
            if state == TrackerState.PAUSED
            else tr(self.settings.language, "menu_pause")
        )

    def update_timers(self, work_seconds: int, until_break_seconds: int | None) -> None:
        self._last_work_seconds = max(0, int(work_seconds))
        self._last_until_break_seconds = None if until_break_seconds is None else max(0, int(until_break_seconds))

        lang = self.settings.language
        self.work_time_label.setText(
            f"{tr(lang, 'status_work_time')}: {_format_duration(self._last_work_seconds)}"
        )
        if self._last_until_break_seconds is None:
            until_text = tr(lang, "status_no_break")
        else:
            until_text = _format_duration(self._last_until_break_seconds)
        self.until_break_label.setText(f"{tr(lang, 'status_until_break')}: {until_text}")

    def show_status_tab(self) -> None:
        self._present_window()

    def _present_window(self) -> None:
        self._move_to_anchor()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _move_to_anchor(self) -> None:
        self.move(20, 60)

    def refresh_learning_block(self, force: bool = False) -> None:
        slot = int(time.time() // 30)
        if not force and self._last_learning_slot == slot:
            return
        self._last_learning_slot = slot
        show_quote = slot % 2 == 0

        if show_quote:
            self._current_quote = random_thematic_quote(self.settings.language, self._current_quote)
            topic = tr(self.settings.language, f"quote_topic_{self._current_quote.topic}")
            author = format_thematic_quote_author(self._current_quote)
            self.quote_label.setText(f"{topic}: «{self._current_quote.text}»\n- {author}")
            self._update_learning_block_height()
            return

        self._current_verb = random_irregular_verb(self.settings.language, self._current_verb)
        verb_topic = tr(self.settings.language, "quote_topic_irregular")
        self.quote_label.setText(
            f"{verb_topic}: {self._current_verb.base} - {self._current_verb.past} - {self._current_verb.past_participle}\n"
            f"{self._current_verb.translation}"
        )
        self._update_learning_block_height()

    def _on_quote_click(self) -> None:
        self._last_learning_slot = None
        self.refresh_learning_block(force=True)

    def _toggle_learning_block(self) -> None:
        self._learning_block_visible = not self._learning_block_visible
        self._apply_learning_block_visibility()
        self.retranslate()

    def _apply_learning_block_visibility(self) -> None:
        self.quote_label.setVisible(self._learning_block_visible)
        if self._learning_block_visible:
            self.setFixedWidth(self._size_with_learning_block[0])
            self._update_learning_block_height()
        else:
            self.setFixedSize(*self._size_without_learning_block)

    def _update_learning_block_height(self) -> None:
        if not self._learning_block_visible:
            return

        base_height_without_quote = self._size_without_learning_block[1]
        content_width = max(120, self._size_with_learning_block[0] - 20)
        metrics = QFontMetrics(self.quote_label.font())
        text_rect = metrics.boundingRect(0, 0, content_width, 2000, Qt.TextWordWrap, self.quote_label.text())
        quote_height = text_rect.height() + 14

        target_height = base_height_without_quote + quote_height
        target_height = max(self._min_height_with_learning_block, target_height)
        target_height = min(self._max_height_with_learning_block, target_height)
        self.setFixedHeight(target_height)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._hide_to_tray_enabled:
            event.ignore()
            self.hide()
            return
        event.accept()


def _parse_points(raw: str) -> list[int]:
    values: list[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            value = int(chunk)
        except ValueError:
            return []
        if value > 0:
            values.append(value)
    values = sorted(set(values))
    return values


def _format_duration(seconds: int) -> str:
    total = max(0, int(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
