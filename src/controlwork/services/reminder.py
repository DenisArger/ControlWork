from __future__ import annotations

from dataclasses import dataclass, field

from ..models import ReminderEvent


@dataclass
class ReminderController:
    soft_points: list[int]
    hard_points: list[int]
    _extra_soft: list[int] = field(default_factory=list)
    _extra_hard: list[int] = field(default_factory=list)
    _fired_soft: set[int] = field(default_factory=set)
    _fired_hard: set[int] = field(default_factory=set)

    def evaluate_due_events(self, active_minutes: int) -> list[ReminderEvent]:
        if active_minutes <= 0:
            return []

        due: list[ReminderEvent] = []
        soft_candidates = sorted(set(self.soft_points + self._extra_soft))
        hard_candidates = sorted(set(self.hard_points + self._extra_hard))

        for point in soft_candidates:
            if active_minutes >= point and point not in self._fired_soft:
                self._fired_soft.add(point)
                due.append(ReminderEvent(event_type="soft", point_min=point))

        for point in hard_candidates:
            if active_minutes >= point and point not in self._fired_hard:
                self._fired_hard.add(point)
                due.append(ReminderEvent(event_type="hard", point_min=point))

        due.sort(key=lambda event: (event.point_min, 0 if event.event_type == "soft" else 1))
        return due

    def add_snooze(self, event_type: str, current_minute: int, offset_minutes: int = 5) -> None:
        target = max(1, current_minute + offset_minutes)
        if event_type == "hard":
            self._extra_hard.append(target)
        else:
            self._extra_soft.append(target)

    def reset_cycle(self) -> None:
        self._extra_soft.clear()
        self._extra_hard.clear()
        self._fired_soft.clear()
        self._fired_hard.clear()

    def update_points(self, soft_points: list[int], hard_points: list[int]) -> None:
        self.soft_points = sorted(set(soft_points))
        self.hard_points = sorted(set(hard_points))
        self.reset_cycle()

    def next_hard_point_min(self, active_minutes: int) -> int | None:
        hard_candidates = sorted(set(self.hard_points + self._extra_hard))
        for point in hard_candidates:
            if point > active_minutes and point not in self._fired_hard:
                return point
        return None
