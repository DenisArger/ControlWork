from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr


class BreakOverlay(QWidget):
    start_break = Signal()
    snooze = Signal()
    skip = Signal()

    def __init__(self, language: str, reminder_tone: str = "friendly") -> None:
        super().__init__()
        self.language = language
        self.reminder_tone = reminder_tone
        self._is_break_mode = False

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet(
            "background-color: rgba(20, 20, 20, 240); color: white; font-size: 22px;"
        )

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(24)

        self.title = QLabel()
        self.countdown = QLabel()
        self.idle_info = QLabel()

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton()
        self.snooze_btn = QPushButton()
        self.skip_btn = QPushButton()
        self.start_btn.clicked.connect(self.start_break.emit)
        self.snooze_btn.clicked.connect(self.snooze.emit)
        self.skip_btn.clicked.connect(self.skip.emit)

        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.snooze_btn)
        btn_row.addWidget(self.skip_btn)

        root.addWidget(self.title, alignment=Qt.AlignCenter)
        root.addWidget(self.countdown, alignment=Qt.AlignCenter)
        root.addWidget(self.idle_info, alignment=Qt.AlignCenter)
        root.addLayout(btn_row)
        self.setLayout(root)

        self.retranslate()

    def retranslate(self) -> None:
        self.title.setText(tr(self.language, "overlay_prompt", _tone=self.reminder_tone))
        self.start_btn.setText(tr(self.language, "overlay_start"))
        self.snooze_btn.setText(tr(self.language, "overlay_snooze"))
        self.skip_btn.setText(tr(self.language, "overlay_skip"))
        if not self._is_break_mode:
            self.countdown.setText("")
            self.idle_info.setText("")

    def set_language(self, language: str, reminder_tone: str | None = None) -> None:
        self.language = language
        if reminder_tone is not None:
            self.reminder_tone = reminder_tone
        self.retranslate()

    def show_prompt(self, can_skip: bool) -> None:
        self._is_break_mode = False
        self.title.setText(tr(self.language, "overlay_prompt", _tone=self.reminder_tone))
        self.countdown.setText("")
        self.idle_info.setText("")
        self.start_btn.setEnabled(True)
        self.snooze_btn.setEnabled(True)
        self.skip_btn.setEnabled(can_skip)
        self.showFullScreen()

    def set_break_mode(self, remaining_sec: int, idle_streak_sec: int) -> None:
        self._is_break_mode = True
        self.start_btn.setEnabled(False)
        self.snooze_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.update_break_metrics(remaining_sec, idle_streak_sec)

    def update_break_metrics(self, remaining_sec: int, idle_streak_sec: int) -> None:
        self.countdown.setText(tr(self.language, "overlay_remaining", seconds=remaining_sec))
        self.idle_info.setText(tr(self.language, "overlay_idle", seconds=idle_streak_sec))
