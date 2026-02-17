from controlwork.services.reminder import ReminderController


def test_reminders_fire_default_points_over_hour() -> None:
    controller = ReminderController([15, 30, 45], [50])
    soft = []
    hard = []

    for minute in range(1, 61):
        due = controller.evaluate_due_events(minute)
        for event in due:
            if event.event_type == "soft":
                soft.append(event.point_min)
            else:
                hard.append(event.point_min)

    assert soft == [15, 30, 45]
    assert hard == [50]


def test_snooze_adds_future_soft_point() -> None:
    controller = ReminderController([15], [50])
    assert controller.evaluate_due_events(15)[0].point_min == 15

    controller.add_snooze("soft", current_minute=15, offset_minutes=5)
    due_19 = controller.evaluate_due_events(19)
    due_20 = controller.evaluate_due_events(20)

    assert due_19 == []
    assert len(due_20) == 1
    assert due_20[0].event_type == "soft"
    assert due_20[0].point_min == 20
