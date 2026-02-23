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
