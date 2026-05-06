from __future__ import annotations

import hashlib
import random
import time
from datetime import date
from html import escape
from dataclasses import replace
from typing import Callable, TypeVar

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..i18n import (
    IRREGULAR_VERBS,
    THEMED_QUOTES,
    IrregularVerb,
    ThemedQuote,
    format_thematic_quote_author,
    tr,
)
from ..models import AppSettings, REMINDER_TONES, TrackerState
from ..services.learning_content import LearningCard, LearningContentError, load_learning_cards

_T = TypeVar("_T")


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
        self.learning_path_edit = QLineEdit()
        self.learning_browse_btn = QPushButton()
        self.learning_browse_btn.clicked.connect(self._browse_learning_json)
        learning_path_row = QHBoxLayout()
        learning_path_row.addWidget(self.learning_path_edit)
        learning_path_row.addWidget(self.learning_browse_btn)

        form = QFormLayout()
        self.language_label = QLabel()
        self.autostart_label = QLabel()
        self.idle_label = QLabel()
        self.break_label = QLabel()
        self.tone_label = QLabel()
        self.soft_label = QLabel()
        self.hard_label = QLabel()
        self.reset_label = QLabel()
        self.learning_path_label = QLabel()

        form.addRow(self.language_label, self.language_combo)
        form.addRow(self.autostart_label, self.autostart_checkbox)
        form.addRow(self.idle_label, self.idle_spin)
        form.addRow(self.break_label, self.break_spin)
        form.addRow(self.tone_label, self.tone_combo)
        form.addRow(self.soft_label, self.soft_edit)
        form.addRow(self.hard_label, self.hard_edit)
        form.addRow(self.reset_label, self.reset_edit)
        form.addRow(self.learning_path_label, learning_path_row)

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
        self.learning_path_edit.setText(_format_learning_paths(settings.learning_json_paths))

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
        self.learning_path_label.setText(tr(lang, "settings_learning_json"))
        self.learning_browse_btn.setText(tr(lang, "settings_browse"))
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
            learning_json_paths=_parse_learning_paths(self.learning_path_edit.text()),
        )
        next_settings.normalize()
        self.settings = next_settings
        self.accept()

    def _browse_learning_json(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            tr(self.settings.language, "settings_learning_json"),
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not selected:
            return
        existing = _parse_learning_paths(self.learning_path_edit.text())
        for path in selected:
            if path not in existing:
                existing.append(path)
        self.learning_path_edit.setText(_format_learning_paths(existing))


class MainWindow(QMainWindow):
    pause_toggle_requested = Signal()

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._size_with_learning_block = (340, 470)
        self._size_without_learning_block = (340, 280)
        self._fixed_learning_scroll_height = 220
        self._current_state = TrackerState.ACTIVE
        self.settings = settings
        self._hide_to_tray_enabled = True
        self._learning_block_visible = True
        self._last_learning_slot: int | None = None
        self._current_quote: ThemedQuote | None = None
        self._current_verb: IrregularVerb | None = None
        self._custom_cards: list[LearningCard] = []
        self._current_card: LearningCard | None = None
        self._custom_json_error_keys: list[str] = []
        self._custom_json_error_shown = False
        self._recent_history = self._normalized_recent_history(settings.learning_recent_history)
        self._last_work_seconds = 0
        self._last_until_break_seconds: int | None = None
        self.setWindowFlag(Qt.Window, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setFixedSize(*self._size_with_learning_block)

        body = QWidget()
        body.setObjectName("mainRoot")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.state_title_label = QLabel()
        self.state_badge_label = QLabel()
        state_row = QHBoxLayout()
        state_row.setContentsMargins(0, 0, 0, 0)
        state_row.setSpacing(8)
        state_row.addWidget(self.state_title_label)
        state_row.addStretch(1)
        state_row.addWidget(self.state_badge_label)

        self.timer_card = QFrame()
        self.timer_card.setObjectName("timerCard")
        self.timer_card.setMinimumHeight(80)
        timer_layout = QVBoxLayout()
        timer_layout.setContentsMargins(12, 8, 12, 8)
        timer_layout.setSpacing(0)
        self.work_time_title_label = QLabel()
        self.work_time_title_label.setObjectName("secondaryText")
        self.work_time_label = QLabel()
        self.work_time_label.setObjectName("workTimeValue")
        self.work_time_label.setMinimumHeight(32)
        self.until_break_label = QLabel()
        self.until_break_label.setObjectName("secondaryText")
        timer_layout.addWidget(self.work_time_title_label)
        timer_layout.addWidget(self.work_time_label)
        timer_layout.addWidget(self.until_break_label)
        self.timer_card.setLayout(timer_layout)

        self.toggle_learning_btn = QPushButton()
        self.quote_label = ClickableLabel()
        self.learning_title_label = QLabel()
        self.learning_card = QFrame()
        self.learning_card.setObjectName("learningCard")
        self.learning_scroll = QScrollArea()
        self.pause_btn = QPushButton()
        self.toggle_learning_btn.setObjectName("secondaryButton")
        self.pause_btn.setObjectName("primaryButton")
        self.state_badge_label.setObjectName("stateBadge")
        self.state_title_label.setObjectName("sectionTitle")
        self.learning_title_label.setObjectName("sectionTitle")
        self.pause_btn.setFixedHeight(36)
        self.toggle_learning_btn.setFixedHeight(36)
        self.pause_btn.clicked.connect(self.pause_toggle_requested.emit)
        self.toggle_learning_btn.clicked.connect(self._toggle_learning_block)
        self.quote_label.clicked.connect(self._on_quote_click)
        self.quote_label.setWordWrap(True)
        self.quote_label.setCursor(Qt.PointingHandCursor)
        self.quote_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.quote_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.quote_label.setTextFormat(Qt.RichText)
        self.learning_scroll.setWidgetResizable(True)
        self.learning_scroll.setFrameShape(QFrame.NoFrame)
        self.learning_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.learning_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.learning_scroll.setFixedHeight(self._fixed_learning_scroll_height)
        self.learning_content = QWidget()
        learning_content_layout = QVBoxLayout()
        learning_content_layout.setContentsMargins(0, 0, 4, 0)
        learning_content_layout.setSpacing(0)
        learning_content_layout.addWidget(self.quote_label)
        learning_content_layout.setAlignment(self.quote_label, Qt.AlignTop)
        self.learning_content.setLayout(learning_content_layout)
        self.learning_scroll.setWidget(self.learning_content)
        learning_layout = QVBoxLayout()
        learning_layout.setContentsMargins(10, 8, 10, 8)
        learning_layout.setSpacing(0)
        learning_layout.addWidget(self.learning_scroll)
        self.learning_card.setLayout(learning_layout)

        layout.addLayout(state_row)
        layout.addWidget(self.timer_card)
        layout.addWidget(self.toggle_learning_btn)
        layout.addWidget(self.learning_title_label)
        layout.addWidget(self.learning_card)
        layout.addWidget(self.pause_btn)
        layout.addStretch(1)

        body.setLayout(layout)
        self.setCentralWidget(body)
        self._apply_styles()

        self.retranslate()
        self._reload_custom_cards()
        self._apply_learning_block_visibility()
        self.refresh_learning_block(force=True)

    def set_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self._custom_json_error_shown = False
        self._recent_history = self._normalized_recent_history(settings.learning_recent_history)
        self._reload_custom_cards()
        self.refresh_learning_block(force=True)  # ← добавить эту строку        self._reload_custom_cards()

    def set_hide_to_tray_enabled(self, enabled: bool) -> None:
        self._hide_to_tray_enabled = enabled

    def retranslate(self) -> None:
        lang = self.settings.language
        self.setWindowTitle(tr(lang, "app_title"))
        self.state_title_label.setText(f"{tr(lang, 'status_title')}:")
        self.learning_title_label.setText(tr(lang, "learning_block_title"))
        self.work_time_title_label.setText(tr(lang, "status_work_time"))
        self.pause_btn.setText(tr(lang, "menu_pause"))
        self.toggle_learning_btn.setText(
            tr(lang, "btn_hide_quotes") if self._learning_block_visible else tr(lang, "btn_show_quotes")
        )
        self.update_state(self._current_state)
        self.update_timers(self._last_work_seconds, self._last_until_break_seconds)
        self.refresh_learning_block(force=True)

    def update_state(self, state: TrackerState) -> None:
        self._current_state = state
        key_map = {
            TrackerState.ACTIVE: "state_active",
            TrackerState.IDLE: "state_idle",
            TrackerState.BREAK: "state_break",
            TrackerState.PAUSED: "state_paused",
        }
        state_text = tr(self.settings.language, key_map[state])
        self.state_badge_label.setText(state_text)
        self._apply_status_badge_style(state)
        self.pause_btn.setText(
            tr(self.settings.language, "menu_resume")
            if state == TrackerState.PAUSED
            else tr(self.settings.language, "menu_pause")
        )

    def update_timers(self, work_seconds: int, until_break_seconds: int | None) -> None:
        self._last_work_seconds = max(0, int(work_seconds))
        self._last_until_break_seconds = None if until_break_seconds is None else max(0, int(until_break_seconds))

        lang = self.settings.language
        self.work_time_label.setText(_format_duration(self._last_work_seconds))
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
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.move(20, 60)
            return
        geometry = screen.availableGeometry()
        x = geometry.x() + max(0, (geometry.width() - self.width()) // 2)
        y = geometry.y() + max(0, (geometry.height() - self.height()) // 4)
        self.move(x, y)

    def refresh_learning_block(self, force: bool = False) -> None:
        slot = int(time.time() // 30)
        if not force and self._last_learning_slot == slot:
            return
        self._last_learning_slot = slot
        learning_slot = slot % 3

        if learning_slot == 0:
            self._render_quote()
            return

        if learning_slot == 1:
            self._render_irregular_verb()
            return

        if self._custom_cards:
            self._render_custom_card()
            return

        self._render_quote()

    def _render_quote(self) -> None:
        lang_key = "en" if self.settings.language == "en" else "ru"
        pool = self._daily_quote_pool(lang_key)
        ordered_pool = self._daily_ordered_pool(
            pool,
            item_id_fn=lambda item: f"{item.topic}|{item.author}|{item.text}",
            day_key=f"{date.today().isoformat()}|{lang_key}",
        )
        seconds_since_midnight = int(time.time() % 86400)
        slot_index = (seconds_since_midnight // 30) % len(ordered_pool)
        quote = ordered_pool[slot_index]
        self._current_quote = quote
        topic = tr(self.settings.language, f"quote_topic_{quote.topic}")
        author = format_thematic_quote_author(quote)
        self.quote_label.setText(
            self._format_learning_html(
                [
                    ("label", topic),
                    ("quote", f"«{quote.text}»"),
                    ("meta", f"- {author}"),
                ]
            )
        )

    def _render_irregular_verb(self) -> None:
        lang_key = "en" if self.settings.language == "en" else "ru"
        verb = self._select_with_recent_ids(
            IRREGULAR_VERBS[lang_key],
            item_id_fn=lambda item: f"{item.base}|{item.past}|{item.past_participle}",
            history_key="verbs",
        )
        self._current_verb = verb
        verb_topic = tr(self.settings.language, "quote_topic_irregular")
        self.quote_label.setText(
            self._format_learning_html(
                [
                    ("label", verb_topic),
                    ("text", f"{verb.base} - {verb.past} - {verb.past_participle}"),
                    ("meta", verb.translation),
                ]
            )
        )

    def _render_custom_card(self) -> None:
        card = self._select_with_recent_ids(
            self._custom_cards,
            item_id_fn=lambda item: (
                f"{item.english}|{item.russian}|{item.transcription or ''}|"
                f"{item.example or ''}|{item.example_translation or ''}"
            ),
            history_key="cards",
        )
        self._current_card = card
        topic = tr(self.settings.language, "quote_topic_custom_json")

        rows: list[tuple[str, str]] = [("label", topic), ("text", card.english), ("meta", card.russian)]
        if card.transcription:
            rows.append(("label", tr(self.settings.language, "learning_transcription_prefix")))
            rows.append(("meta", card.transcription))
        if card.example:
            rows.append(("label", tr(self.settings.language, "learning_example_prefix")))
            rows.append(("text", card.example))
        if card.example_translation:
            rows.append(("label", tr(self.settings.language, "learning_example_translation_prefix")))
            rows.append(("meta", card.example_translation))
        self.quote_label.setText(self._format_learning_html(rows))

    def _reload_custom_cards(self) -> None:
        self._custom_cards = []
        self._current_card = None
        self._custom_json_error_keys = []
        paths = self.settings.learning_json_paths
        if not paths:
            return
        for path in paths:
            try:
                self._custom_cards.extend(load_learning_cards(path))
            except FileNotFoundError:
                self._custom_json_error_keys.append("learning_json_unavailable")
            except (OSError, ValueError, LearningContentError):
                self._custom_json_error_keys.append("learning_json_invalid")

    def pop_learning_json_error(self) -> str | None:
        if self._custom_json_error_shown or not self._custom_json_error_keys:
            return None
        self._custom_json_error_shown = True
        unique_keys: list[str] = []
        for key in self._custom_json_error_keys:
            if key not in unique_keys:
                unique_keys.append(key)
        return "\n".join(tr(self.settings.language, key) for key in unique_keys)

    def _normalized_recent_history(self, payload: object) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {"quotes": [], "verbs": [], "cards": []}
        if not isinstance(payload, dict):
            return normalized
        for key in normalized:
            raw_values = payload.get(key, [])
            if not isinstance(raw_values, list):
                continue
            values: list[str] = []
            for raw in raw_values:
                text = str(raw).strip()
                if not text or text in values:
                    continue
                values.append(text)
            normalized[key] = values[-5:]
        return normalized

    def _sync_recent_history_to_settings(self) -> None:
        self.settings.learning_recent_history = self._normalized_recent_history(self._recent_history)

    def _select_with_recent_ids(
        self,
        pool: list[_T],
        item_id_fn: Callable[[_T], str],
        history_key: str,
        recent_window: int = 5,
    ) -> _T:
        if not pool:
            raise ValueError("pool must not be empty")

        history = self._recent_history.setdefault(history_key, [])
        recent = history[-recent_window:]
        candidates = [item for item in pool if item_id_fn(item) not in recent]

        if not candidates and history:
            last_id = history[-1]
            candidates = [item for item in pool if item_id_fn(item) != last_id]

        if not candidates:
            candidates = pool

        selected = random.choice(candidates)
        selected_id = item_id_fn(selected)
        updated = [item_id for item_id in history if item_id != selected_id]
        updated.append(selected_id)
        self._recent_history[history_key] = updated[-recent_window:]
        self._sync_recent_history_to_settings()
        return selected

    def _daily_ordered_pool(
        self,
        pool: list[_T],
        item_id_fn: Callable[[_T], str],
        day_key: str,
    ) -> list[_T]:
        if not pool:
            raise ValueError("pool must not be empty")

        return sorted(
            pool,
            key=lambda item: hashlib.sha256(f"{day_key}|{item_id_fn(item)}".encode("utf-8")).hexdigest(),
        )

    def _daily_quote_pool(self, lang_key: str) -> list[ThemedQuote]:
        topics = list(THEMED_QUOTES[lang_key].keys())
        if not topics:
            return []

        today = date.today()
        day_key = f"{today.isoformat()}|{lang_key}|topics"
        ordered_topics = sorted(
            topics,
            key=lambda topic: hashlib.sha256(f"{day_key}|{topic}".encode("utf-8")).hexdigest(),
        )
        topic_count = min(3, len(ordered_topics))
        if topic_count == len(ordered_topics):
            chosen_topics = ordered_topics
        else:
            start_index = today.toordinal() % len(ordered_topics)
            chosen_topics = [ordered_topics[(start_index + offset) % len(ordered_topics)] for offset in range(topic_count)]
        return [quote for topic in chosen_topics for quote in THEMED_QUOTES[lang_key][topic]]

    def _on_quote_click(self) -> None:
        self._last_learning_slot = None
        self.refresh_learning_block(force=True)

    def _toggle_learning_block(self) -> None:
        self._learning_block_visible = not self._learning_block_visible
        self._apply_learning_block_visibility()
        self.retranslate()

    def _apply_learning_block_visibility(self) -> None:
        self.learning_title_label.setVisible(self._learning_block_visible)
        self.learning_card.setVisible(self._learning_block_visible)
        if self._learning_block_visible:
            self.setFixedSize(*self._size_with_learning_block)
        else:
            self.setFixedSize(*self._size_without_learning_block)

    def _format_learning_html(self, rows: list[tuple[str, str]]) -> str:
        parts: list[str] = ['<div style="line-height:1.28;">']
        for kind, value in rows:
            text = escape(value.strip())
            if not text:
                continue
            if kind == "label":
                parts.append(f'<div style="font-weight:600;color:#374151;margin-top:1px;">{text}</div>')
            elif kind == "quote":
                parts.append(f'<div style="font-style:italic;color:#1F2937;">{text}</div>')
            elif kind == "meta":
                parts.append(f'<div style="color:#4B5563;">{text}</div>')
            else:
                parts.append(f'<div style="color:#1F2937;">{text}</div>')
        parts.append("</div>")
        return "".join(parts)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F6F8FB;
            }
            QWidget#mainRoot {
                background-color: #F6F8FB;
            }
            QWidget {
                color: #1F2937;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            QFrame#timerCard, QFrame#learningCard {
                background-color: #FFFFFF;
                border: 1px solid #D5DCE6;
                border-radius: 10px;
            }
            QLabel#sectionTitle {
                color: #1F2937;
                font-weight: 600;
            }
            QLabel#workTimeValue {
                font-family: "Consolas";
                font-size: 24px;
                font-weight: 700;
                color: #111827;
            }
            QLabel#secondaryText {
                color: #4B5563;
                font-size: 13px;
            }
            QLabel#stateBadge {
                border-radius: 999px;
                padding: 3px 10px;
                font-size: 13px;
                font-weight: 600;
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QLabel#learningText {
                color: #1F2937;
                font-size: 13px;
                background-color: transparent;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QPushButton {
                min-height: 36px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton#primaryButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: 1px solid #2563EB;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover {
                background-color: #1D4ED8;
                border-color: #1D4ED8;
            }
            QPushButton#primaryButton:pressed {
                background-color: #1E40AF;
                border-color: #1E40AF;
            }
            QPushButton#secondaryButton {
                background-color: #FFFFFF;
                color: #1F2937;
                border: 1px solid #D5DCE6;
            }
            QPushButton#secondaryButton:hover {
                background-color: #F3F6FA;
            }
            QPushButton#secondaryButton:pressed {
                background-color: #E8EEF7;
            }
            QPushButton:focus {
                border: 1px solid #93C5FD;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #C7D2E0;
                border-radius: 4px;
                min-height: 18px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
            """
        )
        self.quote_label.setObjectName("learningText")
        self.quote_label.setContentsMargins(0, 0, 0, 0)
        self.quote_label.style().unpolish(self.quote_label)
        self.quote_label.style().polish(self.quote_label)

    def _apply_status_badge_style(self, state: TrackerState) -> None:
        style_map = {
            TrackerState.ACTIVE: ("#DBEAFE", "#1E40AF"),
            TrackerState.IDLE: ("#E5E7EB", "#374151"),
            TrackerState.BREAK: ("#D1FAE5", "#065F46"),
            TrackerState.PAUSED: ("#FEF3C7", "#92400E"),
        }
        bg, fg = style_map[state]
        self.state_badge_label.setStyleSheet(
            f"background-color: {bg}; color: {fg}; border-radius: 999px; padding: 3px 10px; font-size: 13px; font-weight: 600;"
        )

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


def _parse_learning_paths(raw: str) -> list[str]:
    paths: list[str] = []
    for chunk in raw.replace(";", "\n").splitlines():
        path = chunk.strip()
        if path and path not in paths:
            paths.append(path)
    return paths


def _format_learning_paths(paths: list[str]) -> str:
    return "; ".join(paths)


def _format_duration(seconds: int) -> str:
    total = max(0, int(seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
