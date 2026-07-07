from __future__ import annotations

import ctypes
import platform
import subprocess
import threading
import time
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


try:
    from Xlib import display as _Xdisplay
    from Xlib import X as _X
    _XLIB_OK = True
except Exception:
    _XLIB_OK = False


class X11PollingIdleProvider(IdleProvider):
    """Measure idle by tracking real keyboard/mouse input via X11 polling.

    On some environments (e.g. fly-wm) the session idle timer reported by
    org.freedesktop.ScreenSaver.GetSessionIdleTime is reset on every query and
    never accumulates, so the screensaver-based providers always report ~0.
    This provider records the last moment of actual input independently of the
    (broken) screensaver timer, polling pointer position and key map each
    second.
    """

    def __init__(self) -> None:
        self.available = _XLIB_OK
        self._last = time.time()
        self._lock = threading.Lock()
        self._disp = None
        if not _XLIB_OK:
            return
        try:
            self._disp = _Xdisplay.Display()
            root = self._disp.screen().root
            ptr = root.query_pointer()
            self._last_ptr = (ptr.root_x, ptr.root_y, ptr.mask)
            self._last_keys = self._disp.query_keymap()
            self._poll = _Xdisplay.Display()
        except Exception:
            self._disp = None
            self.available = False
            return
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        root = self._poll.screen().root
        while True:
            time.sleep(1)
            try:
                ptr = root.query_pointer()
                keys = self._poll.query_keymap()
            except Exception:
                continue
            cur_ptr = (ptr.root_x, ptr.root_y, ptr.mask)
            if cur_ptr != self._last_ptr or keys != self._last_keys:
                with self._lock:
                    self._last = time.time()
                self._last_ptr = cur_ptr
                self._last_keys = keys

    def get_idle_seconds(self) -> int:
        if self._disp is None:
            return 0
        with self._lock:
            return int(time.time() - self._last)


def create_idle_provider() -> IdleProvider:
    system = platform.system()
    if system == "Windows":
        return WindowsIdleProvider()
    if system == "Linux":
        if _XLIB_OK:
            provider = X11PollingIdleProvider()
            if provider.available:
                return provider
        return LinuxIdleProvider()
    return IdleProvider()
