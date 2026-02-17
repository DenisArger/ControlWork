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

    def normalize(self) -> "AppSettings":
        self.language = "en" if self.language == "en" else "ru"
        self.idle_threshold_sec = max(30, int(self.idle_threshold_sec))
        self.break_duration_min = max(1, int(self.break_duration_min))
        if self.reminder_tone not in REMINDER_TONES:
            self.reminder_tone = "friendly"
        self.soft_points_min = _normalize_points(self.soft_points_min)
        self.hard_points_min = _normalize_points(self.hard_points_min)
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
    break_completed: bool = False


def _normalize_points(values: list[int]) -> list[int]:
    normalized = sorted({int(v) for v in values if int(v) > 0})
    return normalized or [15]


REMINDER_TONES = (
    "friendly",
    "care",
    "neutral",
    "motivation",
    "short",
)
