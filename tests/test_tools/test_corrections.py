"""Tests for the corrections system: CorrectionsProcessor, build_recognizable_dictionary,
LatinPassthroughProvider, backtracking, and corrected_string."""

import pytest

from stark.core.parsing import CorrectionMatch, PatternParser, Pattern
from stark.general.localisation import LocaleString
from stark.models.transcription_string import Correction, TranscriptionString
from stark.tools.common.span import Span


# --- LatinPassthroughProvider ---


class TestLatinPassthroughProvider:
    def test_latin_text_passthrough(self):
        from stark.tools.phonetic.transcription import LatinPassthroughProvider

        provider = LatinPassthroughProvider()
        assert provider.to_ipa("hello world", "en") == "hello world"

    def test_latin_text_lowercased(self):
        from stark.tools.phonetic.transcription import LatinPassthroughProvider

        provider = LatinPassthroughProvider()
        assert provider.to_ipa("Hello World", "en") == "hello world"

    def test_non_latin_no_fallback_raises(self):
        from stark.tools.phonetic.transcription import LatinPassthroughProvider

        provider = LatinPassthroughProvider()
        with pytest.raises(ValueError, match="Non-latin"):
            provider.to_ipa("привет", "ru")

    def test_non_latin_with_fallback(self):
        from stark.tools.phonetic.transcription import LatinPassthroughProvider

        class MockProvider:
            def to_ipa(self, string, language_code):
                return "mock_ipa"

        provider = LatinPassthroughProvider(fallback=MockProvider())
        assert provider.to_ipa("привет", "ru") == "mock_ipa"

    def test_mixed_text_delegates_to_fallback(self):
        from stark.tools.phonetic.transcription import LatinPassthroughProvider

        class MockProvider:
            def to_ipa(self, string, language_code):
                return f"ipa:{string}"

        provider = LatinPassthroughProvider(fallback=MockProvider())
        assert provider.to_ipa("hello мир", "en") == "ipa:hello мир"


# --- build_recognizable_dictionary ---


def test_build_recognizable_dictionary(tmp_path, monkeypatch):
    from stark.general.localisation import Localizer
    from stark.tools.dictionary import build_recognizable_dictionary
    from stark.tools.phonetic.transcription import LatinPassthroughProvider

    d = tmp_path / "strings" / "en"
    d.mkdir(parents=True)
    (d / "recognizable.strings").write_text('"turn" = "turn";\n"light" = "light";')
    (d / "localizable.strings").write_text("")
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    dictionary = build_recognizable_dictionary(localizer, ipa_provider=LatinPassthroughProvider())
    assert dictionary.storage.get_count() == 2

    results = list(dictionary.lookup("turn", "en"))
    assert any(r.name == "turn" for r in results)


# --- CorrectionsProcessor ---


async def test_corrections_processor_generates_corrections(tmp_path, monkeypatch):
    from unittest.mock import MagicMock

    from stark.core.processors.corrections_processor import CorrectionsProcessor
    from stark.general.localisation import Localizer
    from stark.tools.dictionary import build_recognizable_dictionary
    from stark.tools.phonetic.transcription import LatinPassthroughProvider

    d = tmp_path / "strings" / "en"
    d.mkdir(parents=True)
    (d / "recognizable.strings").write_text('"hello" = "hello";')
    (d / "localizable.strings").write_text("")
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()
    dictionary = build_recognizable_dictionary(localizer, ipa_provider=LatinPassthroughProvider())

    context = MagicMock()
    context.pattern_parser = PatternParser(localizer=localizer)

    ts = TranscriptionString.from_words([("helo", "en"), ("world", "en")])
    processor = CorrectionsProcessor(dictionaries=[dictionary])
    await processor.process_string(ts, context, [])

    assert len(ts.corrections) == 1
    assert ts.corrections[0] == Correction(variant="helo", keyword="hello")


async def test_corrections_processor_no_dictionaries_is_noop():
    from unittest.mock import MagicMock

    from stark.core.processors.corrections_processor import CorrectionsProcessor

    context = MagicMock()
    ts = TranscriptionString.from_words([("helo", "en")])
    processor = CorrectionsProcessor()
    await processor.process_string(ts, context, [])
    assert len(ts.corrections) == 0


async def test_corrections_processor_per_track(tmp_path, monkeypatch):
    from unittest.mock import MagicMock

    from stark.core.processors.corrections_processor import CorrectionsProcessor
    from stark.general.localisation import Localizer
    from stark.tools.dictionary import build_recognizable_dictionary
    from stark.tools.phonetic.transcription import LatinPassthroughProvider

    d_en = tmp_path / "strings" / "en"
    d_en.mkdir(parents=True)
    (d_en / "recognizable.strings").write_text('"turn" = "turn";')
    (d_en / "localizable.strings").write_text("")
    d_ru = tmp_path / "strings" / "ru"
    d_ru.mkdir(parents=True)
    (d_ru / "recognizable.strings").write_text('"light" = "light";')
    (d_ru / "localizable.strings").write_text("")
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en", "ru"})
    localizer.load()
    dictionary = build_recognizable_dictionary(localizer, ipa_provider=LatinPassthroughProvider())

    context = MagicMock()
    context.pattern_parser = PatternParser(localizer=localizer)

    ts = TranscriptionString.from_words(
        [("tern", "en"), ("on", "en")],
        alternative_texts={"ru": LocaleString("lite on", "ru")},
    )

    processor = CorrectionsProcessor(dictionaries=[dictionary])
    await processor.process_string(ts, context, [])

    # primary track: "tern" → "turn"
    assert len(ts.corrections) == 1
    assert ts.corrections[0] == Correction(variant="tern", keyword="turn")
    # ru track: "lite" → "light"
    assert "ru" in ts._corrections_by_track
    assert len(ts._corrections_by_track["ru"]) == 1
    assert ts._corrections_by_track["ru"][0] == Correction(variant="lite", keyword="light")


# --- Expansion + backtracking ---


async def test_expansion_and_backtracking():
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("helo", "en"), ("there", "en")],
        corrections=[Correction(variant="helo", keyword="hello")],
    )

    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 1
    assert matches[0].substring == "helo there"
    assert matches[0].corrections == [CorrectionMatch(Span(0, 4), Correction("helo", "hello"))]
    assert matches[0].corrected_string == "hello there"


async def test_no_corrections_empty_backtrack():
    p = PatternParser()

    ts = TranscriptionString.from_words([("hello", "en"), ("there", "en")])

    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 1
    assert matches[0].corrections == []
    assert matches[0].corrected_string == "hello there"


async def test_multiple_corrections_in_same_match():
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("tern", "en"), ("on", "en"), ("the", "en"), ("lite", "en")],
        corrections=[
            Correction(variant="tern", keyword="turn"),
            Correction(variant="lite", keyword="light"),
        ],
    )

    matches = await p.match(Pattern("turn on the light"), ts)
    assert len(matches) == 1
    # "tern on the lite" — "tern" at 0-4, "lite" at 12-16
    assert len(matches[0].corrections) == 2
    assert CorrectionMatch(Span(0, 4), Correction("tern", "turn")) in matches[0].corrections
    assert CorrectionMatch(Span(12, 16), Correction("lite", "light")) in matches[0].corrections
    assert matches[0].corrected_string == "turn on the light"


async def test_duplicate_word_both_corrected():
    """Same word appears twice and both are misspelled — both get corrected."""
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("tern", "en"), ("and", "en"), ("tern", "en")],
        corrections=[Correction(variant="tern", keyword="turn")],
    )

    matches = await p.match(Pattern("turn and turn"), ts)
    assert len(matches) == 1
    # two separate spans for the two "tern" occurrences
    assert len(matches[0].corrections) == 2
    assert CorrectionMatch(Span(0, 4), Correction("tern", "turn")) in matches[0].corrections
    assert CorrectionMatch(Span(9, 13), Correction("tern", "turn")) in matches[0].corrections
    assert matches[0].corrected_string == "turn and turn"


async def test_duplicate_word_only_one_misspelled():
    """Same keyword appears twice but only one is misspelled — only one correction."""
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("turn", "en"), ("and", "en"), ("tern", "en")],
        corrections=[Correction(variant="tern", keyword="turn")],
    )

    matches = await p.match(Pattern("turn and turn"), ts)
    assert len(matches) == 1
    # only the second "tern" at position 9-13 was corrected; the first "turn" matched directly
    assert matches[0].corrections == [CorrectionMatch(Span(9, 13), Correction("tern", "turn"))]
    assert matches[0].corrected_string == "turn and turn"
