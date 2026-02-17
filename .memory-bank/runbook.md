# Runbook

## 1) Локальный запуск (Astra / Linux)
```bash
cd ~/ADV/SD/SD/ControlWork
python3 -m pip install --user virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
python -m controlwork.main
```

## 2) Тесты
```bash
./.venv/bin/pytest -q
```

## 3) Остановка
- Через трей: `Выход`
- Или `Ctrl + C` в терминале запуска

## 4) Перезапуск
```bash
source .venv/bin/activate
python -m controlwork.main
```

## 5) Где данные
Linux:
- `~/.config/controlwork/settings.json`
- `~/.config/controlwork/controlwork.db`

Windows:
- `%APPDATA%\\ControlWork\\settings.json`
- `%APPDATA%\\ControlWork\\controlwork.db`

## 6) Сборка
Linux:
```bash
./scripts/build_linux.sh
```

Windows:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```
