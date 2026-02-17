from __future__ import annotations

import os
import platform
import shlex
import sys
from pathlib import Path

APP_NAME = "ControlWork"


class AutostartService:
    def __init__(self) -> None:
        self._system = platform.system()

    def set_enabled(self, enabled: bool) -> None:
        if self._system == "Windows":
            self._set_windows(enabled)
        elif self._system == "Linux":
            self._set_linux(enabled)

    def is_enabled(self) -> bool:
        if self._system == "Windows":
            return self._is_windows_enabled()
        if self._system == "Linux":
            return self._is_linux_enabled()
        return False

    def _launch_command(self) -> str:
        if getattr(sys, "frozen", False):
            return shlex.quote(sys.executable)
        return f"{shlex.quote(sys.executable)} -m controlwork.main"

    def _set_windows(self, enabled: bool) -> None:
        try:
            import winreg
        except ImportError:
            return
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        except OSError:
            return
        with key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, self._launch_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass

    def _is_windows_enabled(self) -> bool:
        try:
            import winreg
        except ImportError:
            return False
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        except OSError:
            return False
        with key:
            try:
                winreg.QueryValueEx(key, APP_NAME)
                return True
            except FileNotFoundError:
                return False

    def _desktop_path(self) -> Path:
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        return autostart_dir / "controlwork.desktop"

    def _set_linux(self, enabled: bool) -> None:
        path = self._desktop_path()
        if enabled:
            content = "\n".join(
                [
                    "[Desktop Entry]",
                    "Type=Application",
                    "Version=1.0",
                    f"Name={APP_NAME}",
                    f"Exec={self._launch_command()}",
                    "Terminal=false",
                    "X-GNOME-Autostart-enabled=true",
                    "",
                ]
            )
            path.write_text(content, encoding="utf-8")
            os.chmod(path, 0o755)
        else:
            if path.exists():
                path.unlink()

    def _is_linux_enabled(self) -> bool:
        return self._desktop_path().exists()
