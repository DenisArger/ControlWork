from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QDialog, QMenu, QMessageBox, QStyle, QSystemTrayIcon

from .i18n import tr
from .models import AppSettings, ReminderEvent, TrackerState
from .services.autostart import AutostartService
from .services.database import Database
from .services.idle import create_idle_provider
from .services.notification import NotificationService
from .services.reminder import ReminderController
from .services.tracker import TrackerService
from .settings import AppPaths, SettingsService
from .ui.break_overlay import BreakOverlay
from .ui.main_window import FirstRunDialog, MainWindow, SettingsDialog


class ControlWorkApplication:
    def __init__(self) -> None:
        self.qt_app = QApplication(sys.argv)
        self._shutdown_done = False

        self.paths = AppPaths()
        self.settings_service = SettingsService(self.paths)
        self.settings = self.settings_service.load()

        if self.settings_service.is_first_run:
            dialog = FirstRunDialog(self.settings)
            dialog.exec()
            self.settings_service.save(self.settings)

        self.database = Database(self.paths.db_path)
        self.autostart_service = AutostartService()
        self.autostart_service.set_enabled(self.settings.autostart_enabled)

        self.main_window = MainWindow(self.settings)
        self.main_window.set_settings(self.settings)
        self.main_window.pause_toggle_requested.connect(self._toggle_pause)

        self.break_overlay = BreakOverlay(self.settings.language, self.settings.reminder_tone)
        self.break_overlay.start_break.connect(self._on_break_start)
        self.break_overlay.snooze.connect(self._on_hard_snooze)
        self.break_overlay.skip.connect(self._on_hard_skip)

        self.reminder = ReminderController(self.settings.soft_points_min, self.settings.hard_points_min)
        self.tracker = TrackerService(
            settings=self.settings,
            idle_provider=create_idle_provider(),
            reminder=self.reminder,
            database=self.database,
        )
        self.tracker.start_session()

        self.tray_icon: QSystemTrayIcon | None = None
        self.notification = NotificationService()
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self.qt_app.style().standardIcon(QStyle.SP_ComputerIcon), self.main_window)
            self.notification = NotificationService(self.tray_icon)
            self._build_tray_menu()
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.show()
        self.main_window.set_hide_to_tray_enabled(False)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start()

        self.main_window.show()
        self.main_window.update_state(self.tracker.state)
        self.main_window.update_timers(
            self.tracker.get_cycle_active_seconds(),
            self.tracker.get_seconds_to_next_break(),
        )
        self.main_window.show_status_tab()

    def _build_tray_menu(self) -> None:
        if self.tray_icon is None:
            return
        lang = self.settings.language
        menu = QMenu()

        self.action_status = QAction(tr(lang, "menu_status"), self.main_window)
        self.action_pause = QAction(tr(lang, "menu_pause"), self.main_window)
        self.action_settings = QAction(tr(lang, "menu_settings"), self.main_window)
        self.action_exit = QAction(tr(lang, "menu_exit"), self.main_window)

        self.action_status.triggered.connect(self.main_window.show_status_tab)
        self.action_pause.triggered.connect(self._toggle_pause)
        self.action_settings.triggered.connect(self._open_settings_dialog)
        self.action_exit.triggered.connect(self._shutdown)

        menu.addAction(self.action_status)
        menu.addAction(self.action_pause)
        menu.addAction(self.action_settings)
        menu.addSeparator()
        menu.addAction(self.action_exit)

        self.tray_icon.setContextMenu(menu)

    def _retranslate_tray(self) -> None:
        if self.tray_icon is None:
            return
        lang = self.settings.language
        self.action_status.setText(tr(lang, "menu_status"))
        self.action_pause.setText(
            tr(lang, "menu_resume") if self.tracker.state == TrackerState.PAUSED else tr(lang, "menu_pause")
        )
        self.action_settings.setText(tr(lang, "menu_settings"))
        self.action_exit.setText(tr(lang, "menu_exit"))

    def _on_tick(self) -> None:
        outcome = self.tracker.tick()
        self.main_window.update_state(outcome.state)
        self.main_window.update_timers(
            self.tracker.get_cycle_active_seconds(),
            self.tracker.get_seconds_to_next_break(),
        )
        self.main_window.refresh_learning_block()

        for event in outcome.reminders:
            self._handle_reminder(event)

        if outcome.state == TrackerState.BREAK and outcome.break_remaining_sec is not None and self.break_overlay.isVisible():
            self.break_overlay.set_break_mode(outcome.break_remaining_sec, outcome.break_idle_streak_sec)

        if outcome.break_completed:
            self.break_overlay.hide()
            self.notification.notify(self._reminder_text("hard_title"), self._reminder_text("break_done"))

        self._retranslate_tray()

    def _handle_reminder(self, event: ReminderEvent) -> None:
        if event.event_type == "soft":
            self.notification.notify(
                self._reminder_text("soft_title"),
                self._reminder_text("soft_body", minutes=event.point_min),
            )
            return

        self.notification.notify(
            self._reminder_text("hard_title"),
            self._reminder_text("hard_body"),
            critical=True,
        )
        self.break_overlay.show_prompt(can_skip=self.tracker.can_skip_today())

    def _toggle_pause(self) -> None:
        if self.tracker.state == TrackerState.PAUSED:
            self.tracker.resume_session()
        elif self.tracker.state != TrackerState.BREAK:
            self.tracker.pause_session()
        self._retranslate_tray()

    def _on_break_start(self) -> None:
        self.tracker.enter_break()
        self.break_overlay.set_break_mode(self.settings.break_duration_min * 60, 0)
        self.main_window.update_timers(
            self.tracker.get_cycle_active_seconds(),
            self.tracker.get_seconds_to_next_break(),
        )

    def _on_hard_snooze(self) -> None:
        if self.tracker.request_snooze("hard"):
            self.break_overlay.hide()
        else:
            self.notification.notify(
                self._reminder_text("hard_title"),
                tr(self.settings.language, "limit_snooze"),
                critical=True,
            )

    def _on_hard_skip(self) -> None:
        if self.tracker.skip_break():
            self.break_overlay.hide()
            return
        self.notification.notify(
            self._reminder_text("hard_title"),
            tr(self.settings.language, "limit_skip"),
            critical=True,
        )

    def _on_save_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self.settings_service.save(settings)
        self.tracker.apply_settings(settings)
        self.autostart_service.set_enabled(settings.autostart_enabled)

        self.main_window.set_settings(settings)
        self.main_window.retranslate()
        self.main_window.refresh_learning_block(force=True)
        self.break_overlay.set_language(settings.language, settings.reminder_tone)
        self._retranslate_tray()

    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self.settings, self.main_window)
        if dialog.exec() == QDialog.Accepted:
            self._on_save_settings(dialog.settings)
            QMessageBox.information(self.main_window, "ControlWork", tr(self.settings.language, "saved_ok"))

    def _reminder_text(self, key: str, **kwargs: object) -> str:
        return tr(self.settings.language, key, _tone=self.settings.reminder_tone, **kwargs)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self.main_window.show_status_tab()

    def _shutdown(self) -> None:
        if self._shutdown_done:
            return
        self._shutdown_done = True
        self.timer.stop()
        self.tracker.stop_session()
        self.database.close()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        self.qt_app.quit()

    def run(self) -> int:
        exit_code = self.qt_app.exec()
        self._shutdown()
        return exit_code
