from __future__ import annotations

from dataclasses import replace

from controlwork.models import AppSettings
from controlwork.settings import SettingsService


class DummyPaths:
    def __init__(self, settings_path) -> None:
        self.settings_path = settings_path


def test_learning_json_paths_saved_and_loaded(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"
    service = SettingsService(DummyPaths(settings_path))

    source = AppSettings(learning_json_paths=[" /tmp/cards1.json ", "/tmp/cards2.json"]).normalize()
    service.save(source)
    loaded = service.load()

    assert loaded.learning_json_paths == ["/tmp/cards1.json", "/tmp/cards2.json"]
    assert loaded.learning_json_path == "/tmp/cards1.json"


def test_learning_json_paths_empty_is_stable() -> None:
    settings = replace(AppSettings(), learning_json_paths=["   "]).normalize()
    assert settings.learning_json_paths == []
    assert settings.learning_json_path == ""


def test_learning_json_legacy_path_migrates_to_paths() -> None:
    settings = replace(AppSettings(), learning_json_path=" /tmp/cards.json ").normalize()
    assert settings.learning_json_paths == ["/tmp/cards.json"]
    assert settings.learning_json_path == "/tmp/cards.json"


def test_learning_recent_history_is_normalized() -> None:
    settings = replace(
        AppSettings(),
        learning_recent_history={
            "quotes": [" a ", "a", "", "b", "c", "d", "e", "f"],
            "verbs": "bad",
            "cards": ["x", "x", "y"],
            "other": ["ignored"],
        },
    ).normalize()
    assert settings.learning_recent_history == {
        "quotes": ["b", "c", "d", "e", "f"],
        "verbs": [],
        "cards": ["x", "y"],
    }


def test_learning_recent_history_saved_and_loaded(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"
    service = SettingsService(DummyPaths(settings_path))
    source = AppSettings(
        learning_recent_history={
            "quotes": ["q1", "q2"],
            "verbs": ["v1"],
            "cards": ["c1"],
        }
    ).normalize()
    service.save(source)
    loaded = service.load()
    assert loaded.learning_recent_history == {
        "quotes": ["q1", "q2"],
        "verbs": ["v1"],
        "cards": ["c1"],
    }
