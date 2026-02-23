from __future__ import annotations

import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PySide6_QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QApplication = PySide6_QtWidgets.QApplication

from controlwork.models import AppSettings
from controlwork.ui.main_window import MainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_learning_rotation_uses_custom_json_slot(tmp_path, monkeypatch) -> None:
    _app()
    cards_path = tmp_path / "cards.json"
    cards_path.write_text(
        json.dumps([{"english": "resilient", "russian": "устойчивый", "example": "Stay resilient."}], ensure_ascii=False),
        encoding="utf-8",
    )
    window = MainWindow(AppSettings(language="en", learning_json_paths=[str(cards_path)]).normalize())

    monkeypatch.setattr("controlwork.ui.main_window.time.time", lambda: 62)
    window.refresh_learning_block(force=True)

    text = window.quote_label.text()
    assert "Custom English: resilient" in text
    assert "устойчивый" in text
    assert "Example: Stay resilient." in text


def test_learning_rotation_falls_back_when_custom_json_unavailable(monkeypatch) -> None:
    _app()
    window = MainWindow(AppSettings(language="en", learning_json_paths=["/no/such/path.json"]).normalize())

    monkeypatch.setattr("controlwork.ui.main_window.time.time", lambda: 62)
    window.refresh_learning_block(force=True)

    assert window.pop_learning_json_error() is not None
    assert window.quote_label.text().strip() != ""
    assert "Custom English:" not in window.quote_label.text()


def test_learning_rotation_uses_valid_cards_when_one_file_is_broken(tmp_path, monkeypatch) -> None:
    _app()
    valid_path = tmp_path / "valid.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text(
        json.dumps([{"english": "consistent", "russian": "последовательный"}], ensure_ascii=False),
        encoding="utf-8",
    )
    invalid_path.write_text("{invalid", encoding="utf-8")
    window = MainWindow(
        AppSettings(language="en", learning_json_paths=[str(valid_path), str(invalid_path)]).normalize()
    )

    monkeypatch.setattr("controlwork.ui.main_window.time.time", lambda: 62)
    window.refresh_learning_block(force=True)

    assert "Custom English: consistent" in window.quote_label.text()
    assert window.pop_learning_json_error() is not None
