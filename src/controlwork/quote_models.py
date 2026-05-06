from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemedQuote:
    topic: str
    text: str
    author: str
    translation: str | None = None
