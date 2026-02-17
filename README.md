# ControlWork

ControlWork — компактное desktop-приложение для контроля времени работы за компьютером и напоминаний о перерывах.

Текущая реализация:
- компактное плавающее окно со статусом и таймерами
- управление через иконку в трее
- настройки открываются из контекстного меню трея
- мягкие и строгие напоминания
- полноэкранный экран обязательного перерыва

## Возможности
- Учет только активного времени (idle не засчитывается в работу)
- Настраиваемые точки напоминаний: `soft` и `hard`
- Пауза/продолжение из окна и из трея
- 5 стилей текста напоминаний
- Локальное хранение данных (`settings.json` + SQLite)
- RU/EN интерфейс
- Автозапуск (Windows и Linux)

## Требования
- Python `>=3.7`
- Linux/Windows
- `PySide6>=6.5.3,<6.6`

## Быстрый старт (Linux / Astra)
```bash
cd ~/ADV/SD/SD/ControlWork
python3 -m pip install --user virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
python -m controlwork.main
```

## Быстрый старт (если `venv` доступен)
```bash
cd ~/ADV/SD/SD/ControlWork
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
python -m controlwork.main
```

## Как пользоваться
1. Запустите приложение.
2. В компактном окне видны:
   - текущее состояние
   - время работы
   - время до следующего перерыва
3. Для действий используйте иконку в трее:
   - `Статус`
   - `Пауза/Продолжить`
   - `Настройки`
   - `Выход`

## Напоминания
- Мягкое напоминание: предлагает отложить или закрыть сообщение.
- Строгое напоминание: открывает полноэкранный экран перерыва.
- Перерыв засчитывается в mixed-режиме:
  - таймер перерыва завершен
  - внутри перерыва набрано минимум 120 секунд непрерывного idle

## Остановка и перезапуск
Остановка:
- через трей: `Выход`
- или в терминале, где запущено приложение: `Ctrl + C`

Перезапуск:
```bash
source .venv/bin/activate
python -m controlwork.main
```

## Тесты
```bash
./.venv/bin/pytest -q
```

## Сборка
Linux:
```bash
./scripts/build_linux.sh
```

Windows:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

## Где лежат данные
Linux:
- `~/.config/controlwork/settings.json`
- `~/.config/controlwork/controlwork.db`

Windows:
- `%APPDATA%\ControlWork\settings.json`
- `%APPDATA%\ControlWork\controlwork.db`

## Структура проекта
- `src/controlwork/app.py` — точка сборки приложения, трей, таймер тиков
- `src/controlwork/ui/` — UI окна, overlay и диалоги
- `src/controlwork/services/` — трекер, уведомления, idle, БД, автозапуск
- `src/controlwork/i18n.py` — тексты RU/EN и тоны сообщений
- `tests/` — unit-тесты логики

## Частые проблемы
`No module named PySide6`:
```bash
pip install -e .[dev]
```

`python3 -m venv` не работает на Astra:
- используйте путь через `virtualenv` из раздела "Быстрый старт (Linux / Astra)".
