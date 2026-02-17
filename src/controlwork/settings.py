from __future__ import annotations

import json
import os
import platform
from dataclasses import asdict
from pathlib import Path

from .models import AppSettings


class AppPaths:
    def __init__(self) -> None:
        self.config_dir = self._resolve_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_path = self.config_dir / "settings.json"
        self.db_path = self.config_dir / "controlwork.db"

    @staticmethod
    def _resolve_config_dir() -> Path:
        system = platform.system()
        if system == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            return base / "ControlWork"
        return Path.home() / ".config" / "controlwork"


class SettingsService:
    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths

    @property
    def is_first_run(self) -> bool:
        return not self._paths.settings_path.exists()

    def load(self) -> AppSettings:
        if not self._paths.settings_path.exists():
            return AppSettings().normalize()
        try:
            payload = json.loads(self._paths.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return AppSettings().normalize()
        settings = AppSettings(**payload)
        return settings.normalize()

    def save(self, settings: AppSettings) -> None:
        settings.normalize()
        self._paths.settings_path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
