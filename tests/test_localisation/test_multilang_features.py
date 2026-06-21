"""Tests for multilanguage features: matrix matching, suggestions expansion, and relay confidence building."""
import os

import pytest

from stark.core.command import Response
from stark.core.commands_manager import CommandsManager
from stark.core.parsing import PatternParser
from stark.core.patterns import Pattern
from stark.core.processors.search_processor import SearchProcessor
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty
from stark.general.localisation import LocaleString
from stark.models.transcription_string import TranscriptionString
from stark.models.voice_transcription import (
    Suggestion,
    VoiceTranscriptionTrack,
    VoiceTranscriptionWord,
)


# --- Fixtures ---


class GreetingEn(Object):
    value: str

    @classproperty
    def patterns(cls) -> dict[str, Pattern]:
        return {
            "base": Pattern("hello $name:Word"),
            "en": Pattern("hello $name:Word"),
            "ru": Pattern("привет $name:Word"),
        }


@pytest.fixture
def parser():
    p = PatternParser()
    p.register_parameter_type(GreetingEn)
    return p


@pytest.fixture
def manager():
    m = CommandsManager()

    @m.new({"base": "hello $name:Word", "en": "hello $name:Word", "ru": "привет $name:Word"})
    async def greet(name: Word) -> Response:
        return Response(text=f"Hello {name}!")

    return m


# --- Matrix matching ---


async def test_matrix_matching_finds_command_in_alternative_track(parser, manager):
    ts = TranscriptionString.from_words(
        [("hello", "en"), ("world", "en")],
        alternative_texts={
            "ru": LocaleString("привет мир", "ru"),
        },
    )

    processor = SearchProcessor()
    results = await processor.search(ts, parser, manager.commands, [])

    assert len(results) >= 1
    assert results[0].command.name == "CommandsManager.greet"


async def test_matrix_matching_finds_russian_command_from_alternative(parser, manager):
    ts = TranscriptionString.from_words(
        [("привет", "ru"), ("мир", "ru")],
        alternative_texts={
            "en": LocaleString("hello world", "en"),
        },
    )

    processor = SearchProcessor()
    results = await processor.search(ts, parser, manager.commands, [])

    assert len(results) >= 1


async def test_matrix_matching_disabled_via_flag(parser, manager, monkeypatch):
    monkeypatch.setenv("STARK_ENABLE_MULTILANG_MATRIX", "0")

    ts = TranscriptionString.from_words(
        [("xyz", "en")],
        alternative_texts={
            "ru": LocaleString("привет мир", "ru"),
        },
    )

    processor = SearchProcessor()
    results = await processor.search(ts, parser, manager.commands, [])

    # "xyz" doesn't match any command, and matrix is disabled so "привет мир" is not tried
    assert len(results) == 0


async def test_plain_string_still_works(parser, manager):
    processor = SearchProcessor()
    results = await processor.search("hello world", parser, manager.commands, [])

    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.greet"


# --- Recognizable suggestions expansion ---


async def test_suggestions_expand_regex(monkeypatch):
    monkeypatch.setenv("STARK_ENABLE_RECOGNIZABLE_EXPAND", "1")
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("helo", "en"), ("there", "en")],
        suggestions=(Suggestion(variant="helo", keyword="hello"),),
    )

    # "helo there" doesn't match "hello there" normally
    # but with expansion, regex becomes "(hello|helo) there"
    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 1
    assert matches[0].substring == "helo there"


async def test_suggestions_not_expanded_by_default():
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("helo", "en"), ("there", "en")],
        suggestions=(Suggestion(variant="helo", keyword="hello"),),
    )

    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 0


# --- _build_best_confidence ---


def _make_word(word, lang, start, end, conf):
    return VoiceTranscriptionWord(
        word=word, language_code=lang, char_start=0, char_end=len(word),
        start=start, end=end, conf=conf,
    )


def _make_track(words, lang='en'):
    return VoiceTranscriptionTrack(
        text=' '.join(w.word for w in words),
        result=words,
        language_code=lang,
    )


def test_build_best_confidence_prefers_higher_confidence():
    from stark.interfaces.recognizer_relay import SpeechRecognizerRelay

    relay = SpeechRecognizerRelay([])

    en_track = _make_track([
        _make_word("hello", "en", 0.0, 0.5, 0.9),
        _make_word("world", "en", 0.5, 1.0, 0.8),
    ], "en")

    ru_track = _make_track([
        _make_word("привет", "ru", 0.0, 0.5, 0.3),
        _make_word("мир", "ru", 0.5, 1.0, 0.4),
    ], "ru")

    best = relay._build_best_confidence({en_track, ru_track})

    assert "hello" in best.text
    assert "world" in best.text


def test_build_best_confidence_mixed_languages():
    from stark.interfaces.recognizer_relay import SpeechRecognizerRelay

    relay = SpeechRecognizerRelay([])

    en_track = _make_track([
        _make_word("set", "en", 0.0, 0.3, 0.9),
        _make_word("timer", "en", 0.3, 0.7, 0.8),
        _make_word("for", "en", 0.7, 0.9, 0.9),
        _make_word("two", "en", 0.9, 1.2, 0.3),
        _make_word("hours", "en", 1.2, 1.6, 0.3),
    ], "en")

    ru_track = _make_track([
        _make_word("сет", "ru", 0.0, 0.3, 0.3),
        _make_word("таймер", "ru", 0.3, 0.7, 0.3),
        _make_word("фор", "ru", 0.7, 0.9, 0.3),
        _make_word("два", "ru", 0.9, 1.2, 0.9),
        _make_word("часа", "ru", 1.2, 1.6, 0.9),
    ], "ru")

    best = relay._build_best_confidence({en_track, ru_track})

    # English words had higher confidence for "set", "timer", "for"
    # Russian words had higher confidence for "два", "часа"
    assert "set" in best.text
    assert "два" in best.text or "часа" in best.text


def test_build_best_confidence_language_priority():
    from stark.interfaces.recognizer_relay import SpeechRecognizerRelay

    relay = SpeechRecognizerRelay([])

    en_track = _make_track([_make_word("hello", "en", 0.0, 0.5, 0.8)], "en")
    ru_track = _make_track([_make_word("привет", "ru", 0.0, 0.5, 0.8)], "ru")

    # equal confidence — priority should decide
    best = relay._build_best_confidence(
        {en_track, ru_track},
        language_priority={"en": 0, "ru": 1},
    )
    assert "hello" in best.text

    # reverse priority
    en_track2 = _make_track([_make_word("hello", "en", 0.0, 0.5, 0.8)], "en")
    ru_track2 = _make_track([_make_word("привет", "ru", 0.0, 0.5, 0.8)], "ru")
    best2 = relay._build_best_confidence(
        {en_track2, ru_track2},
        language_priority={"en": 1, "ru": 0},
    )
    assert "привет" in best2.text


# --- Cross-track phonetic dedup ---


def test_phonetic_dedup_similar_strings(monkeypatch):
    monkeypatch.setenv("STARK_ENABLE_MULTILANG_PHONETIC_OVERLAP", "1")

    from stark.core.parsing import MatchResult
    from stark.core.commands_manager import SearchResult
    from stark.core.command import Command

    cmd = Command("test.greet", {"base": Pattern("hello")}, lambda: None)

    # TranscriptionString enables phonetic overlap detection
    ts = TranscriptionString.from_words([("hello", "en"), ("world", "en")])

    results = [
        SearchResult(cmd, MatchResult(substring="hello world", start=0, end=11, parameters={}), index=0),
        SearchResult(cmd, MatchResult(substring="helo world", start=0, end=10, parameters={}), index=1),
    ]

    deduped = SearchProcessor._deduplicate_cross_track(results, ts)
    assert len(deduped) == 1
    assert deduped[0].match_result.substring == "hello world"


def test_phonetic_dedup_different_strings(monkeypatch):
    monkeypatch.setenv("STARK_ENABLE_MULTILANG_PHONETIC_OVERLAP", "1")

    from stark.core.parsing import MatchResult
    from stark.core.commands_manager import SearchResult
    from stark.core.command import Command

    cmd = Command("test.greet", {"base": Pattern("hello")}, lambda: None)

    ts = TranscriptionString.from_words([("hello", "en"), ("world", "en")])

    results = [
        SearchResult(cmd, MatchResult(substring="hello world", start=0, end=11, parameters={}), index=0),
        SearchResult(cmd, MatchResult(substring="привет мир", start=0, end=10, parameters={}), index=1),
    ]

    deduped = SearchProcessor._deduplicate_cross_track(results, ts)
    assert len(deduped) == 2


def test_locale_string_overlap_returns_none():
    ls = LocaleString("hello world", "en")
    assert ls.are_substrings_overlapping("hello", "world") is None
