from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass

from PySide6.QtWidgets import QSystemTrayIcon


@dataclass
class NotificationService:
    tray_icon: QSystemTrayIcon

    def notify(self, title: str, message: str, critical: bool = False) -> None:
        self._try_native_backend(title, message, critical)
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Warning if critical else QSystemTrayIcon.Information, 7000)

    def _try_native_backend(self, title: str, message: str, critical: bool) -> None:
        system = platform.system()
        if system == "Linux":
            self._notify_linux(title, message, critical)
        elif system == "Windows":
            self._notify_windows_winrt(title, message)

    @staticmethod
    def _notify_linux(title: str, message: str, critical: bool) -> None:
        urgency = "critical" if critical else "normal"
        try:
            subprocess.run(
                ["notify-send", "-u", urgency, title, message],
                check=False,
                timeout=0.5,
            )
        except (OSError, subprocess.SubprocessError):
            return

    @staticmethod
    def _notify_windows_winrt(title: str, message: str) -> None:
        try:
            from winrt.windows.data.xml.dom import XmlDocument
            from winrt.windows.ui.notifications import (
                ToastNotification,
                ToastNotificationManager,
            )
        except Exception:
            return
        xml = (
            "<toast><visual><binding template='ToastGeneric'>"
            f"<text>{title}</text><text>{message}</text>"
            "</binding></visual></toast>"
        )
        try:
            doc = XmlDocument()
            doc.load_xml(xml)
            toast = ToastNotification(doc)
            notifier = ToastNotificationManager.create_toast_notifier("ControlWork")
            notifier.show(toast)
        except Exception:
            return
