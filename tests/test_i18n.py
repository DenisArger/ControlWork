from controlwork.i18n import (
    IRREGULAR_VERBS,
    THEMED_QUOTES,
    ThemedQuote,
    format_thematic_quote_author,
    random_irregular_verb,
    random_thematic_quote,
    tr,
)


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


def test_quote_placeholder_is_filled_automatically() -> None:
    text = tr("ru", "hard_body", _tone="neutral")
    assert "{quote}" not in text


def test_quote_can_be_overridden_explicitly() -> None:
    text = tr("en", "break_done", _tone="friendly", quote="Test quote")
    assert "Test quote" in text


def test_themed_quotes_have_required_topics_and_sizes() -> None:
    required_topics = {"family", "discipline", "health", "children", "leadership", "bible"}
    ru_topics = set(THEMED_QUOTES["ru"].keys())
    en_topics = set(THEMED_QUOTES["en"].keys())
    assert ru_topics == required_topics
    assert en_topics == required_topics
    for topic in required_topics:
        if topic == "bible":
            assert len(THEMED_QUOTES["ru"][topic]) == 10
        else:
            assert len(THEMED_QUOTES["ru"][topic]) == 5
        assert len(THEMED_QUOTES["en"][topic]) == 5


def test_themed_quotes_have_no_cross_topic_duplicates() -> None:
    for lang in ("ru", "en"):
        seen: set[tuple[str, str]] = set()
        for topic_quotes in THEMED_QUOTES[lang].values():
            for quote in topic_quotes:
                key = (quote.text, quote.author)
                assert key not in seen
                seen.add(key)


def test_no_technical_placeholder_quotes_present() -> None:
    for lang in ("ru", "en"):
        for topic_quotes in THEMED_QUOTES[lang].values():
            for quote in topic_quotes:
                assert "ControlWork" not in quote.author
                assert "#1:" not in quote.text


def test_thematic_quote_author_translation_suffix_rule() -> None:
    synodal = ThemedQuote(topic="bible", text="x", author="Библия, Притчи 4:23")
    nrp = ThemedQuote(topic="bible", text="x", author="Библия, Притчи 4:23", translation="nrp")
    assert format_thematic_quote_author(synodal) == "Библия, Притчи 4:23"
    assert format_thematic_quote_author(nrp) == "Библия, Притчи 4:23 (НРП)"


def test_random_thematic_quote_can_change_from_previous() -> None:
    previous = random_thematic_quote("ru")
    current = random_thematic_quote("ru", previous)
    assert current != previous


def test_irregular_verbs_available_for_both_languages() -> None:
    assert len(IRREGULAR_VERBS["ru"]) >= 20
    assert len(IRREGULAR_VERBS["en"]) >= 20


def test_random_irregular_verb_can_change_from_previous() -> None:
    previous = random_irregular_verb("ru")
    current = random_irregular_verb("ru", previous)
    assert current != previous


def test_screenshot_irregular_verbs_exist() -> None:
    required = {
        "deal",
        "feed",
        "leave",
        "meet",
        "sleep",
        "feel",
        "mean",
        "hold",
        "keep",
        "read",
        "sweep",
        "blow",
        "fly",
        "know",
        "draw",
        "grow",
        "throw",
        "show",
        "wear",
        "come",
        "become",
        "begin",
        "drink",
        "run",
        "swim",
        "sink",
        "sing",
        "ring",
    }
    ru_bases = {verb.base for verb in IRREGULAR_VERBS["ru"]}
    en_bases = {verb.base for verb in IRREGULAR_VERBS["en"]}
    assert required.issubset(ru_bases)
    assert required.issubset(en_bases)
