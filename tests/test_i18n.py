from controlwork.i18n import tr


def test_ru_tone_variants_are_different() -> None:
    friendly = tr("ru", "soft_title", _tone="friendly")
    care = tr("ru", "soft_title", _tone="care")
    short = tr("ru", "soft_title", _tone="short")

    assert friendly != care
    assert care != short


def test_unknown_tone_falls_back_to_friendly() -> None:
    fallback = tr("ru", "soft_title", _tone="unknown-tone")
    friendly = tr("ru", "soft_title", _tone="friendly")
    assert fallback == friendly


def test_message_formatting_works_with_tone() -> None:
    text = tr("ru", "soft_body", _tone="neutral", minutes=25)
    assert "25" in text
