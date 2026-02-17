from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import Qt, Signal
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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr
from ..models import AppSettings, REMINDER_TONES, TrackerState


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


class MainWindow(QMainWindow):
    save_requested = Signal(AppSettings)
    pause_toggle_requested = Signal()

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.status_tab = QWidget()
        self.settings_tab = QWidget()
        self.stats_tab = QWidget()

        self.tabs.addTab(self.status_tab, "")
        self.tabs.addTab(self.settings_tab, "")
        self.tabs.addTab(self.stats_tab, "")

        self._build_status_tab()
        self._build_settings_tab()
        self._build_stats_tab()
        self.retranslate()

    def _build_status_tab(self) -> None:
        self.state_label = QLabel()
        self.pause_btn = QPushButton()
        self.pause_btn.clicked.connect(self.pause_toggle_requested.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.state_label)
        layout.addWidget(self.pause_btn)
        layout.addStretch(1)
        self.status_tab.setLayout(layout)

    def _build_settings_tab(self) -> None:
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

        self.save_btn = QPushButton()
        self.save_btn.clicked.connect(self._emit_save)

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

        root = QVBoxLayout()
        root.addLayout(form)
        root.addWidget(self.save_btn)
        root.addStretch(1)
        self.settings_tab.setLayout(root)

    def _build_stats_tab(self) -> None:
        self.active_today = QLabel()
        self.idle_today = QLabel()
        self.break_today = QLabel()
        self.snooze_today = QLabel()
        self.skip_today = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.active_today)
        layout.addWidget(self.idle_today)
        layout.addWidget(self.break_today)
        layout.addWidget(self.snooze_today)
        layout.addWidget(self.skip_today)
        layout.addStretch(1)
        self.stats_tab.setLayout(layout)

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
        self.setWindowTitle(tr(lang, "app_title"))
        self.tabs.setTabText(0, tr(lang, "tab_status"))
        self.tabs.setTabText(1, tr(lang, "tab_settings"))
        self.tabs.setTabText(2, tr(lang, "tab_stats"))
        self.pause_btn.setText(tr(lang, "menu_pause"))

        self.language_label.setText(tr(lang, "settings_language"))
        self.autostart_label.setText(tr(lang, "settings_autostart"))
        self.idle_label.setText(tr(lang, "settings_idle"))
        self.break_label.setText(tr(lang, "settings_break"))
        self.tone_label.setText(tr(lang, "settings_tone"))
        self.soft_label.setText(tr(lang, "settings_soft"))
        self.hard_label.setText(tr(lang, "settings_hard"))
        self.reset_label.setText(tr(lang, "settings_reset"))
        self.save_btn.setText(tr(lang, "settings_save"))
        for idx, tone in enumerate(REMINDER_TONES):
            self.tone_combo.setItemText(idx, tr(lang, "tone_" + tone))

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

    def update_stats(self, stats: dict[str, int]) -> None:
        lang = self.settings.language
        self.active_today.setText(f"{tr(lang, 'today_active')}: {stats['active_sec']}s")
        self.idle_today.setText(f"{tr(lang, 'today_idle')}: {stats['idle_sec']}s")
        self.break_today.setText(f"{tr(lang, 'today_break')}: {stats['break_sec']}s")
        self.snooze_today.setText(f"{tr(lang, 'today_snooze')}: {stats['snoozes']}")
        self.skip_today.setText(f"{tr(lang, 'today_skip')}: {stats['skips']}")

    def show_status_tab(self) -> None:
        self.tabs.setCurrentIndex(0)
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def show_settings_tab(self) -> None:
        self.tabs.setCurrentIndex(1)
        self.show_status_tab()

    def show_stats_tab(self) -> None:
        self.tabs.setCurrentIndex(2)
        self.show_status_tab()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()
        self.hide()

    def _emit_save(self) -> None:
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
        self.save_requested.emit(next_settings)
        QMessageBox.information(self, "ControlWork", tr(self.settings.language, "saved_ok"))


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
