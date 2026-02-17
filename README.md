# ControlWork

Desktop app (Windows/Linux MVP) for active work-time tracking and break reminders.

## Features
- Tray app with status/settings/statistics window
- Active time counting with idle pause (`idle >= 120 sec` by default)
- Configurable soft and hard reminder points
- 5 reminder text styles (friendly/care/neutral/motivation/short)
- Fullscreen hard-break overlay
- Mixed break validation: timer done + 120s continuous idle during break
- Local SQLite history and JSON settings
- RU/EN UI
- Autostart (Windows registry / Linux `.desktop`)

## Run
```bash
# Preferred (if python3 -m venv works)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m controlwork.main
```

```bash
# Fallback for systems without python3-venv (e.g. Astra Linux 1.7)
python3 -m pip install --user virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m controlwork.main
```

## Build
```bash
./scripts/build_linux.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

## Tests
```bash
pytest
```
