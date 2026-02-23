from __future__ import annotations

import json

import pytest

from controlwork.services.learning_content import LearningContentError, load_learning_cards, validate_learning_cards_payload


def test_validate_learning_cards_payload_accepts_valid_cards() -> None:
    cards = validate_learning_cards_payload(
        [
            {
                "english": "deal with",
                "russian": "иметь дело с",
                "example": "I deal with clients daily.",
                "example_translation": "Я ежедневно работаю с клиентами.",
            },
            {"english": "resilient", "russian": "устойчивый"},
        ]
    )
    assert len(cards) == 2
    assert cards[0].english == "deal with"
    assert cards[0].russian == "иметь дело с"
    assert cards[0].example == "I deal with clients daily."
    assert cards[0].example_translation == "Я ежедневно работаю с клиентами."
    assert cards[1].example is None
    assert cards[1].example_translation is None


def test_validate_learning_cards_payload_supports_example_ru_alias() -> None:
    cards = validate_learning_cards_payload(
        [
            {
                "english": "focus",
                "russian": "фокус",
                "example": "Stay focused.",
                "example_ru": "Сохраняй фокус.",
            }
        ]
    )
    assert cards[0].example_translation == "Сохраняй фокус."


@pytest.mark.parametrize(
    "payload",
    [
        {"english": "a", "russian": "b"},
        [{"english": "", "russian": "b"}],
        [{"english": "a"}],
        [{"english": "a", "russian": 42}],
        [{"english": "a", "russian": "b", "example": 1}],
        [{"english": "a", "russian": "b", "example_translation": 1}],
    ],
)
def test_validate_learning_cards_payload_rejects_invalid_payload(payload: object) -> None:
    with pytest.raises(LearningContentError):
        validate_learning_cards_payload(payload)


def test_load_learning_cards_reads_file(tmp_path) -> None:
    path = tmp_path / "cards.json"
    path.write_text(
        json.dumps([{"english": "focus", "russian": "фокус"}], ensure_ascii=False),
        encoding="utf-8",
    )
    cards = load_learning_cards(str(path))
    assert len(cards) == 1
    assert cards[0].english == "focus"
