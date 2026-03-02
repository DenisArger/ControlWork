from __future__ import annotations

import json
from dataclasses import dataclass


class LearningContentError(ValueError):
    pass


@dataclass(frozen=True)
class LearningCard:
    english: str
    russian: str
    transcription: str | None = None
    example: str | None = None
    example_translation: str | None = None


def validate_learning_cards_payload(payload: object) -> list[LearningCard]:
    if not isinstance(payload, list):
        raise LearningContentError("payload must be a list")

    cards: list[LearningCard] = []
    for item in payload:
        if not isinstance(item, dict):
            raise LearningContentError("card must be an object")

        english = item.get("english")
        russian = item.get("russian")
        transcription = item.get("transcription")
        if transcription is None:
            transcription = item.get("phonetic")
        if transcription is None:
            transcription = item.get("ipa")
        example = item.get("example")
        example_translation = item.get("example_translation")
        if example_translation is None:
            example_translation = item.get("example_ru")

        if not isinstance(english, str) or not english.strip():
            raise LearningContentError("english must be a non-empty string")
        if not isinstance(russian, str) or not russian.strip():
            raise LearningContentError("russian must be a non-empty string")
        if transcription is not None and not isinstance(transcription, str):
            raise LearningContentError("transcription must be a string or null")
        if example is not None and not isinstance(example, str):
            raise LearningContentError("example must be a string or null")
        if example_translation is not None and not isinstance(example_translation, str):
            raise LearningContentError("example_translation must be a string or null")

        normalized_transcription = transcription.strip() if isinstance(transcription, str) else None
        normalized_example = example.strip() if isinstance(example, str) else None
        normalized_example_translation = example_translation.strip() if isinstance(example_translation, str) else None
        cards.append(
            LearningCard(
                english=english.strip(),
                russian=russian.strip(),
                transcription=normalized_transcription or None,
                example=normalized_example or None,
                example_translation=normalized_example_translation or None,
            )
        )

    return cards


def load_learning_cards(path: str) -> list[LearningCard]:
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return validate_learning_cards_payload(payload)
