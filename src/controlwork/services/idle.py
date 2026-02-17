from __future__ import annotations

import ctypes
import platform
import subprocess
from dataclasses import dataclass


class IdleProvider:
    def get_idle_seconds(self) -> int:
        return 0


@dataclass
class WindowsIdleProvider(IdleProvider):
    def get_idle_seconds(self) -> int:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_uint),
            ]

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not user32.GetLastInputInfo(ctypes.byref(info)):
            return 0
        tick_count = kernel32.GetTickCount()
        elapsed_ms = tick_count - info.dwTime
        return max(0, int(elapsed_ms / 1000))


@dataclass
class LinuxIdleProvider(IdleProvider):
    def get_idle_seconds(self) -> int:
        dbus_value = self._get_idle_via_screensaver_dbus()
        if dbus_value is not None:
            return dbus_value
        x11_value = self._get_idle_via_xprintidle()
        if x11_value is not None:
            return x11_value
        return 0

    @staticmethod
    def _get_idle_via_screensaver_dbus() -> int | None:
        cmd = [
            "dbus-send",
            "--session",
            "--dest=org.freedesktop.ScreenSaver",
            "--type=method_call",
            "--print-reply",
            "/org/freedesktop/ScreenSaver",
            "org.freedesktop.ScreenSaver.GetSessionIdleTime",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=0.3)
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode != 0:
            return None
        for token in proc.stdout.replace("\n", " ").split():
            if token.isdigit():
                value = int(token)
                return max(0, int(value / 1000))
        return None

    @staticmethod
    def _get_idle_via_xprintidle() -> int | None:
        try:
            proc = subprocess.run(["xprintidle"], capture_output=True, text=True, check=False, timeout=0.3)
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode != 0:
            return None
        try:
            return max(0, int(float(proc.stdout.strip()) / 1000))
        except ValueError:
            return None


def create_idle_provider() -> IdleProvider:
    system = platform.system()
    if system == "Windows":
        return WindowsIdleProvider()
    if system == "Linux":
        return LinuxIdleProvider()
    return IdleProvider()
