from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from controlwork.models import AppSettings, TrackerState
from controlwork.services.database import Database
from controlwork.services.reminder import ReminderController
from controlwork.services.tracker import TrackerService


class SequenceIdleProvider:
    def __init__(self, sequence: list[int]) -> None:
        self.sequence = sequence
        self.index = 0

    def get_idle_seconds(self) -> int:
        if self.index >= len(self.sequence):
            return self.sequence[-1] if self.sequence else 0
        value = self.sequence[self.index]
        self.index += 1
        return value


class FakeClock:
    def __init__(self, current: datetime) -> None:
        self.current = current

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: int = 1) -> None:
        self.current += timedelta(seconds=seconds)


def make_tracker(tmp_path: Path, idle_sequence: list[int], break_minutes: int = 10) -> tuple[TrackerService, FakeClock, Database]:
    db = Database(tmp_path / "test.db")
    settings = AppSettings(
        language="en",
        idle_threshold_sec=120,
        break_duration_min=break_minutes,
        soft_points_min=[15, 30, 45],
        hard_points_min=[50],
    ).normalize()
    clock = FakeClock(datetime(2026, 2, 17, 12, 0, 0))
    tracker = TrackerService(
        settings=settings,
        idle_provider=SequenceIdleProvider(idle_sequence),
        reminder=ReminderController(settings.soft_points_min, settings.hard_points_min),
        database=db,
        clock=clock,
    )
    tracker.start_session()
    return tracker, clock, db


def test_active_vs_idle_accounting(tmp_path: Path) -> None:
    tracker, clock, db = make_tracker(tmp_path, [0] * 10 + [200] * 5)

    for _ in range(15):
        tracker.tick()
        clock.advance()

    assert tracker.active_sec == 10
    assert tracker.idle_sec == 5
    assert tracker.state == TrackerState.IDLE
    db.close()


def test_mixed_break_rule_timer_plus_idle_streak(tmp_path: Path) -> None:
    tracker, clock, db = make_tracker(tmp_path, [200] * 140, break_minutes=2)

    tracker.enter_break()
    completed = False

    for _ in range(120):
        outcome = tracker.tick()
        clock.advance()
        completed = completed or outcome.break_completed

    assert completed is True
    assert tracker.state == TrackerState.ACTIVE
    db.close()


def test_snooze_limit_per_work_hour(tmp_path: Path) -> None:
    tracker, clock, db = make_tracker(tmp_path, [0] * 100)

    assert tracker.request_snooze("soft") is True
    assert tracker.request_snooze("soft") is True
    assert tracker.request_snooze("soft") is False
    db.close()


def test_skip_limit_per_day(tmp_path: Path) -> None:
    tracker, clock, db = make_tracker(tmp_path, [0] * 10)

    assert tracker.skip_break() is True
    assert tracker.skip_break() is False
    stats = tracker.get_today_stats()
    assert stats["skips"] == 1
    db.close()


def test_seconds_to_next_break_for_active_cycle(tmp_path: Path) -> None:
    tracker, clock, db = make_tracker(tmp_path, [0] * 10)
    tracker.cycle_active_sec = 49 * 60 + 30
    assert tracker.get_seconds_to_next_break() == 30
    db.close()
