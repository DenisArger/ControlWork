from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from ..models import AppSettings, ReminderEvent, TickOutcome, TrackerState
from .database import Database
from .idle import IdleProvider
from .reminder import ReminderController


@dataclass
class SystemClock:
    def now(self) -> datetime:
        return datetime.now()


class TrackerService:
    def __init__(
        self,
        settings: AppSettings,
        idle_provider: IdleProvider,
        reminder: ReminderController,
        database: Database,
        clock: SystemClock | None = None,
    ) -> None:
        self.settings = settings
        self.idle_provider = idle_provider
        self.reminder = reminder
        self.database = database
        self.clock = clock or SystemClock()

        self.state = TrackerState.ACTIVE
        self.session_id: int | None = None
        self.break_event_id: int | None = None

        self.active_sec = 0
        self.idle_sec = 0
        self.break_sec = 0
        self.cycle_active_sec = 0

        self.break_elapsed_sec = 0
        self.break_idle_streak_sec = 0
        self.break_max_idle_streak_sec = 0

        self.snooze_hour_bucket = 0
        self.snooze_count_in_bucket = 0
        self.skip_count_today = 0
        self.current_day_key = self._day_window(self.clock.now())[0].isoformat()

    def start_session(self) -> None:
        now = self.clock.now()
        self.database.close_open_sessions(now)
        self.session_id = self.database.create_session(now)
        self.skip_count_today = self.database.get_skip_count(*self._day_window(now))
        self.database.save_settings_cache(asdict(self.settings))

    def stop_session(self) -> None:
        if self.session_id is None:
            return
        if self.break_event_id is not None:
            self.database.close_break_event(self.break_event_id, self.clock.now(), completed=False)
            self.break_event_id = None
        self.database.update_session_totals(self.session_id, self.active_sec, self.idle_sec, self.break_sec)
        self.database.close_session(self.session_id, self.clock.now())
        self.session_id = None

    def apply_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self.reminder.update_points(settings.soft_points_min, settings.hard_points_min)
        self.database.save_settings_cache(asdict(settings))

    def pause_session(self) -> None:
        self.state = TrackerState.PAUSED

    def resume_session(self) -> None:
        if self.state == TrackerState.PAUSED:
            self.state = TrackerState.ACTIVE

    def can_skip_today(self) -> bool:
        return self.skip_count_today < 1

    def request_snooze(self, event_type: str) -> bool:
        bucket = self.cycle_active_sec // 3600
        if bucket != self.snooze_hour_bucket:
            self.snooze_hour_bucket = bucket
            self.snooze_count_in_bucket = 0
        if self.snooze_count_in_bucket >= 2:
            return False
        current_min = max(1, self.cycle_active_sec // 60)
        self.reminder.add_snooze(event_type, current_min, 5)
        self.snooze_count_in_bucket += 1
        self.database.log_reminder(self.clock.now(), event_type, current_min, "snooze")
        return True

    def skip_break(self) -> bool:
        if not self.can_skip_today():
            return False
        self.skip_count_today += 1
        self.database.log_reminder(self.clock.now(), "hard", max(1, self.cycle_active_sec // 60), "skip")
        return True

    def enter_break(self) -> None:
        self.state = TrackerState.BREAK
        self.break_elapsed_sec = 0
        self.break_idle_streak_sec = 0
        self.break_max_idle_streak_sec = 0
        self.break_event_id = self.database.start_break_event(self.clock.now())

    def tick(self) -> TickOutcome:
        now = self.clock.now()
        self._roll_day_if_needed(now)

        if self.session_id is None:
            self.start_session()

        outcome = TickOutcome(state=self.state)

        if self.state == TrackerState.PAUSED:
            self._flush_session_totals()
            return outcome

        if self.state == TrackerState.BREAK:
            self._tick_break()
            remaining = max(0, self.settings.break_duration_min * 60 - self.break_elapsed_sec)
            outcome.state = self.state
            outcome.break_remaining_sec = remaining
            outcome.break_idle_streak_sec = self.break_max_idle_streak_sec
            if remaining <= 0 and self.break_max_idle_streak_sec >= 120:
                self._complete_break()
                outcome.break_completed = True
                outcome.state = self.state
            self._flush_session_totals()
            return outcome

        idle_seconds = self.idle_provider.get_idle_seconds()
        if idle_seconds >= self.settings.idle_threshold_sec:
            self.state = TrackerState.IDLE
            self.idle_sec += 1
        else:
            self.state = TrackerState.ACTIVE
            self.active_sec += 1
            self.cycle_active_sec += 1
            active_minutes = self.cycle_active_sec // 60
            reminders = self.reminder.evaluate_due_events(active_minutes)
            if reminders:
                for event in reminders:
                    self.database.log_reminder(now, event.event_type, event.point_min, "shown")
                outcome.reminders = reminders

        outcome.state = self.state
        self._flush_session_totals()
        return outcome

    def acknowledge_ignore(self, event: ReminderEvent) -> None:
        self.database.log_reminder(self.clock.now(), event.event_type, event.point_min, "ignore")

    def get_today_stats(self) -> dict[str, int]:
        return self.database.get_today_stats(*self._day_window(self.clock.now()))

    def get_cycle_active_seconds(self) -> int:
        return self.cycle_active_sec

    def get_seconds_to_next_break(self) -> int | None:
        if self.state == TrackerState.BREAK:
            return max(0, self.settings.break_duration_min * 60 - self.break_elapsed_sec)
        active_minutes = self.cycle_active_sec // 60
        next_hard_min = self.reminder.next_hard_point_min(active_minutes)
        if next_hard_min is None:
            return None
        return max(0, next_hard_min * 60 - self.cycle_active_sec)

    def _tick_break(self) -> None:
        self.break_sec += 1
        self.break_elapsed_sec += 1
        idle_seconds = self.idle_provider.get_idle_seconds()

        if idle_seconds >= self.settings.idle_threshold_sec:
            self.break_idle_streak_sec += 1
        else:
            self.break_idle_streak_sec = 0
        self.break_max_idle_streak_sec = max(self.break_max_idle_streak_sec, self.break_idle_streak_sec)

        if self.break_event_id is not None:
            self.database.update_break_event(self.break_event_id, self.break_max_idle_streak_sec)

    def _complete_break(self) -> None:
        self.state = TrackerState.ACTIVE
        self.cycle_active_sec = 0
        self.snooze_hour_bucket = 0
        self.snooze_count_in_bucket = 0
        self.reminder.reset_cycle()
        if self.break_event_id is not None:
            self.database.close_break_event(self.break_event_id, self.clock.now(), completed=True)
            self.break_event_id = None

    def _roll_day_if_needed(self, now: datetime) -> None:
        current = self._day_window(now)[0].isoformat()
        if current == self.current_day_key:
            return
        self.current_day_key = current
        self.skip_count_today = self.database.get_skip_count(*self._day_window(now))

    def _flush_session_totals(self) -> None:
        if self.session_id is not None:
            self.database.update_session_totals(self.session_id, self.active_sec, self.idle_sec, self.break_sec)

    def _day_window(self, now: datetime) -> tuple[datetime, datetime]:
        hh, mm = [int(part) for part in self.settings.workday_reset_time.split(":")]
        reset_today = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if now < reset_today:
            start = reset_today - timedelta(days=1)
        else:
            start = reset_today
        return (start, start + timedelta(days=1))
