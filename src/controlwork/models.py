from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrackerState(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    BREAK = "break"
    PAUSED = "paused"


@dataclass
class ReminderEvent:
    event_type: str
    point_min: int


@dataclass
class AppSettings:
    language: str = "ru"
    autostart_enabled: bool = True
    idle_threshold_sec: int = 120
    break_duration_min: int = 10
    reminder_tone: str = "friendly"
    soft_points_min: list[int] = field(default_factory=lambda: [15, 30, 45])
    hard_points_min: list[int] = field(default_factory=lambda: [50])
    workday_reset_time: str = "04:00"
    learning_json_path: str = ""
    learning_json_paths: list[str] = field(default_factory=list)
    learning_recent_history: dict[str, list[str]] = field(default_factory=dict)

    def normalize(self) -> "AppSettings":
        self.language = "en" if self.language == "en" else "ru"
        self.idle_threshold_sec = max(30, int(self.idle_threshold_sec))
        self.break_duration_min = max(1, int(self.break_duration_min))
        if self.reminder_tone not in REMINDER_TONES:
            self.reminder_tone = "friendly"
        self.soft_points_min = _normalize_points(self.soft_points_min)
        self.hard_points_min = _normalize_points(self.hard_points_min)
        normalized_paths: list[str] = []
        for path in self.learning_json_paths or []:
            text = str(path).strip()
            if text and text not in normalized_paths:
                normalized_paths.append(text)

        legacy_path = str(self.learning_json_path or "").strip()
        if not normalized_paths and legacy_path:
            normalized_paths.append(legacy_path)

        self.learning_json_paths = normalized_paths
        self.learning_json_path = normalized_paths[0] if normalized_paths else ""
        self.learning_recent_history = _normalize_learning_recent_history(self.learning_recent_history)
        parts = self.workday_reset_time.split(":")
        if len(parts) != 2:
            self.workday_reset_time = "04:00"
            return self
        try:
            hh = int(parts[0])
            mm = int(parts[1])
        except ValueError:
            self.workday_reset_time = "04:00"
            return self
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            self.workday_reset_time = "04:00"
            return self
        self.workday_reset_time = f"{hh:02d}:{mm:02d}"
        return self


@dataclass
class TickOutcome:
    state: TrackerState
    reminders: list[ReminderEvent] = field(default_factory=list)
    break_remaining_sec: int | None = None
    break_idle_streak_sec: int = 0
    break_idle_max_streak_sec: int = 0
    break_completed: bool = False


def _normalize_points(values: list[int]) -> list[int]:
    normalized = sorted({int(v) for v in values if int(v) > 0})
    return normalized or [15]


def _normalize_learning_recent_history(payload: object) -> dict[str, list[str]]:
    allowed_keys = ("quotes", "verbs", "cards")
    result: dict[str, list[str]] = {}
    source = payload if isinstance(payload, dict) else {}
    for key in allowed_keys:
        raw_values = source.get(key, [])
        if not isinstance(raw_values, list):
            result[key] = []
            continue
        values: list[str] = []
        for raw in raw_values:
            text = str(raw).strip()
            if not text or text in values:
                continue
            values.append(text)
        result[key] = values[-5:]
    return result


REMINDER_TONES = (
    "friendly",
    "care",
    "neutral",
    "motivation",
    "short",
)
