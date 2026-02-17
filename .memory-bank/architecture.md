# Architecture

## High-level
- `ControlWorkApplication` собирает все сервисы и UI, запускает тик `QTimer(1s)`.
- Каждый тик вызывает `TrackerService.tick()`.
- UI обновляется из результата тика.

## Слои
- UI (`src/controlwork/ui/`)
  - `MainWindow`: компактный статус
  - `SettingsDialog`: настройки из трея
  - `BreakOverlay`: полноэкранный hard-break экран
- Application (`src/controlwork/app.py`)
  - связывает UI, трекер, уведомления, автозапуск
- Domain/Services (`src/controlwork/services/`)
  - `tracker.py`: состояние и правила
  - `reminder.py`: точки soft/hard и snooze
  - `idle.py`: idle-детекторы для ОС
  - `database.py`: SQLite persistence
  - `autostart.py`, `notification.py`
- Config (`src/controlwork/settings.py`, `src/controlwork/models.py`)
- i18n (`src/controlwork/i18n.py`)

## Состояния трекера
- `active`
- `idle`
- `break`
- `paused`

## Ключевые контракты
- `tick()` возвращает `TickOutcome`.
- `get_seconds_to_next_break()` — расчет таймера до ближайшей hard-точки.
