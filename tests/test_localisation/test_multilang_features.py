"""Tests for multilanguage features: matrix matching, suggestions expansion, and relay confidence building."""

from stark.core.command import Response
from stark.core.commands_manager import CommandsManager
from stark.core.parsing import PatternParser
from stark.core.patterns import Pattern
from stark.core.processors.search_processor import SearchProcessor
from stark.general.localisation import LocaleString
from stark.models.transcription_string import TranscriptionString
from stark.models.voice_transcription import (
    Suggestion,
    VoiceTranscriptionTrack,
    VoiceTranscriptionWord,
)

# --- Recognizable suggestions expansion ---


async def test_suggestions_expand_regex():
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("helo", "en"), ("there", "en")],
        recognizable_alternatives=[Suggestion(variant="helo", keyword="hello")],
    )

    # "helo there" doesn't match "hello there" normally
    # but with alternatives present, regex becomes "(hello|helo) there"
    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 1
    assert matches[0].substring == "helo there"


async def test_suggestions_not_expanded_without_alternatives():
    p = PatternParser()

    ts = TranscriptionString.from_words(
        [("helo", "en"), ("there", "en")],
        # no recognizable_alternatives → no expansion
    )

    matches = await p.match(Pattern("hello there"), ts)
    assert len(matches) == 0


# --- _build_best_confidence ---


def _make_word(word, lang, start, end, conf):
    return VoiceTranscriptionWord(
        word=word,
        language_code=lang,
        char_start=0,
        char_end=len(word),
        start=start,
        end=end,
        conf=conf,
    )


def _make_track(words, lang="en"):
    return VoiceTranscriptionTrack(
        text=" ".join(w.word for w in words),
        result=words,
        language_code=lang,
    )


def test_build_best_confidence_prefers_higher_confidence():
    from stark.interfaces.recognizer_relay import SpeechRecognizerRelay

    relay = SpeechRecognizerRelay([])

    en_track = _make_track(
        [
            _make_word("hello", "en", 0.0, 0.5, 0.9),
            _make_word("world", "en", 0.5, 1.0, 0.8),
        ],
        "en",
    )

    ru_track = _make_track(
        [
            _make_word("привет", "ru", 0.0, 0.5, 0.3),
            _make_word("мир", "ru", 0.5, 1.0, 0.4),
        ],
        "ru",
    )

    best = relay._build_best_confidence({en_track, ru_track})

    assert "hello" in best.text
    assert "world" in best.text


def test_build_best_confidence_mixed_languages():
    from stark.interfaces.recognizer_relay import SpeechRecognizerRelay

    relay = SpeechRecognizerRelay([])

    en_track = _make_track(
        [
            _make_word("set", "en", 0.0, 0.3, 0.9),
            _make_word("timer", "en", 0.3, 0.7, 0.8),
            _make_word("for", "en", 0.7, 0.9, 0.9),
            _make_word("two", "en", 0.9, 1.2, 0.3),
            _make_word("hours", "en", 1.2, 1.6, 0.3),
        ],
        "en",
    )

    ru_track = _make_track(
        [
            _make_word("сет", "ru", 0.0, 0.3, 0.3),
            _make_word("таймер", "ru", 0.3, 0.7, 0.3),
            _make_word("фор", "ru", 0.7, 0.9, 0.3),
            _make_word("два", "ru", 0.9, 1.2, 0.9),
            _make_word("часа", "ru", 1.2, 1.6, 0.9),
        ],
        "ru",
    )

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


# --- RecognizableAlternativesProcessor ---


async def test_recognizable_alternatives_processor(tmp_path, monkeypatch):

    from stark.core.processors.recognizable_alternatives_processor import RecognizableAlternativesProcessor

    # create recognizable strings
    d = tmp_path / "strings" / "en"
    d.mkdir(parents=True)
    (d / "recognizable.strings").write_text('"hello" = "hello";')
    (d / "localizable.strings").write_text('"hello" = "hello";')
    monkeypatch.chdir(tmp_path)

    from stark.general.localisation import Localizer

    localizer = Localizer(languages={"en"})
    localizer.load()

    parser = PatternParser(localizer=localizer)

    from unittest.mock import MagicMock

    context = MagicMock()
    context.pattern_parser = parser

    ts = TranscriptionString.from_words([("helo", "en"), ("world", "en")])
    assert len(ts.recognizable_alternatives) == 0

    processor = RecognizableAlternativesProcessor()
    await processor.process_string(ts, context, [])

    assert len(ts.recognizable_alternatives) >= 1
    assert any(s.keyword == "hello" and s.variant == "helo" for s in ts.recognizable_alternatives)


# --- Position translation ---


def test_locale_string_translate_position_identity():
    ls = LocaleString("hello world")
    assert ls.translate_position(5, "hello world", "hello world") == 5


def test_locale_string_translate_position_substring():
    ls = LocaleString("hello world")
    # from_track is substring of to_track: offset shifts
    assert ls.translate_position(0, "world", "hello world") == 6


def test_locale_string_translate_position_unrelated():
    import pytest

    ls = LocaleString("hello world")
    # neither is substring of the other: raises ValueError (can't verify overlap)
    with pytest.raises(ValueError):
        ls.translate_position(3, "другой текст", "hello world")


# ==============================================================================
# Cross-track matrix matching & overlap resolution (VoiceTranscriptionString)
# ==============================================================================
#
# How it works:
#
# 1. SearchProcessor collects tracks to match: the primary VoiceTranscriptionString
#    plus each alternative_texts entry (when STARK_ENABLE_MULTILANG_MATRIX=1).
#
# 2. Each track is matched concurrently against all commands using
#    get_pattern(track_lang) — English track vs English patterns, Russian track
#    vs Russian patterns, with "base" fallback.
#
# 3. Results are tagged with (source_text, track_lang, SearchResult) and assigned
#    a global index: primary track results get lower indices = higher priority.
#
# 4. Results are sorted by match_result.start (character position in source text).
#
# 5. Adjacent pairs are checked for overlap: translate_position converts positions
#    between tracks via timestamps (VoiceTranscriptionString) or substring offsets
#    (plain LocaleString). Overlapping results are resolved:
#    - Try to cut the loser (lower priority) to fit; if that matches, keep both.
#    - If loser can't be cut, try cutting the winner; if that matches, keep both.
#    - If neither cut works, remove the loser entirely.
#


def _vts_word(word, lang, start, end, conf=0.9):
    return VoiceTranscriptionWord(
        word=word,
        language_code=lang,
        char_start=0,
        char_end=len(word),
        start=start,
        end=end,
        conf=conf,
    )


def _vts_track(words, lang="en"):
    return VoiceTranscriptionTrack(
        text=" ".join(w.word for w in words),
        result=words,
        language_code=lang,
    )


def _make_vts(en_words, ru_words):
    """Build a VoiceTranscriptionString with English primary and Russian alternative."""
    from stark.models.voice_transcription import Transcription

    en_track = _vts_track(en_words, "en")
    ru_track = _vts_track(ru_words, "ru")
    transcription = Transcription(
        best=en_track,
        origins={"en": en_track, "ru": ru_track},
    )
    return transcription.to_voice_transcription_string()


# --- translate_position ---


def test_translate_position_same_track_identity():
    vts = _make_vts(
        en_words=[_vts_word("hello", "en", 0.0, 0.5)],
        ru_words=[_vts_word("привет", "ru", 0.0, 0.5)],
    )
    assert vts.translate_position(3, "hello", "hello") == 3


def test_translate_position_en_to_ru():
    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.7),
        ],
        ru_words=[
            _vts_word("поставь", "ru", 0.0, 0.3),
            _vts_word("таймер", "ru", 0.3, 0.7),
        ],
    )
    # position 0 in en = time 0.0 = position 0 in ru
    assert vts.translate_position(0, "set timer", "поставь таймер") == 0
    # position 4 in en = start of "timer" = time 0.3 = boundary in ru
    pos = vts.translate_position(4, "set timer", "поставь таймер")
    assert 7 <= pos <= 8  # "поставь" is 7 chars, space at 7, "таймер" starts at 8


def test_translate_position_ru_to_en():
    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.7),
        ],
        ru_words=[
            _vts_word("поставь", "ru", 0.0, 0.3),
            _vts_word("таймер", "ru", 0.3, 0.7),
        ],
    )
    assert vts.translate_position(0, "поставь таймер", "set timer") == 0


# --- matrix matching: sequential (no overlap) ---


async def test_matrix_sequential_no_command_overlap_both_match():
    """User says two commands — one only exists in English, the other only in Russian.
    Each is found from its own track; they don't overlap in time so both are kept."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"ru": "включи музыку"})
    async def play_music() -> Response:
        return Response(text="music")

    # en: "set timer and включи музыку" — only "set timer" matches en pattern
    # ru: "поставь таймер и включи музыку" — only "включи музыку" matches ru pattern
    # time-wise: set timer 0.0-0.7, filler 0.7-0.9, включи музыку 0.9-1.6
    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.7),
            _vts_word("and", "en", 0.7, 0.9),
            _vts_word("play", "en", 0.9, 1.2),
            _vts_word("music", "en", 1.2, 1.6),
        ],
        ru_words=[
            _vts_word("поставь", "ru", 0.0, 0.3),
            _vts_word("таймер", "ru", 0.3, 0.7),
            _vts_word("и", "ru", 0.7, 0.9),
            _vts_word("включи", "ru", 0.9, 1.2),
            _vts_word("музыку", "ru", 1.2, 1.6),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    names = {r.command.name for r in results}
    assert len(results) == 2
    assert "CommandsManager.set_timer" in names
    assert "CommandsManager.play_music" in names


async def test_matrix_sequential_no_transcription_overlap_both_match():
    """User says two commands — one only exists in English, the other only in Russian.
    Each is found from its own track; they don't overlap in time so both are kept."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"ru": "выключи свет"})
    async def lights_off() -> Response:
        return Response(text="lights off")

    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.7),
        ],
        ru_words=[
            _vts_word("таймер", "ru", 0.3, 0.7),
            _vts_word("и", "ru", 0.7, 0.9),
            _vts_word("выключи", "ru", 0.9, 1.4),
            _vts_word("свет", "ru", 1.4, 1.8),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    names = {r.command.name for r in results}
    assert len(results) == 2
    assert "CommandsManager.set_timer" in names
    assert "CommandsManager.lights_off" in names


async def test_matrix_only_alternative_track_matches():
    """Command only has a Russian pattern — must be found via the alternative track."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"ru": "включи музыку"})
    async def play_music() -> Response:
        return Response(text="music")

    vts = _make_vts(
        en_words=[
            _vts_word("turn", "en", 0.0, 0.3),
            _vts_word("on", "en", 0.3, 0.5),
            _vts_word("music", "en", 0.5, 0.9),
        ],
        ru_words=[
            _vts_word("включи", "ru", 0.0, 0.5),
            _vts_word("музыку", "ru", 0.5, 0.9),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.play_music"


async def test_matrix_disabled_skips_alternatives(monkeypatch):
    """With flag off, alternative tracks are not matched — ru-only command not found."""
    monkeypatch.setenv("STARK_ENABLE_MULTILANG_MATRIX", "0")
    p = PatternParser()
    m = CommandsManager()

    @m.new({"ru": "включи музыку"})
    async def play_music() -> Response:
        return Response(text="music")

    vts = _make_vts(
        en_words=[
            _vts_word("turn", "en", 0.0, 0.3),
            _vts_word("on", "en", 0.3, 0.5),
            _vts_word("music", "en", 0.5, 0.9),
        ],
        ru_words=[_vts_word("включи", "ru", 0.0, 0.5), _vts_word("музыку", "ru", 0.5, 0.9)],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    assert len(results) == 0


# --- matrix matching: full overlap ---


async def test_matrix_full_overlap_same_command_deduped():
    """Same command matches in both en and ru tracks (full time overlap) — only one result kept."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer", "ru": "поставь таймер"})
    async def set_timer() -> Response:
        return Response(text="timer")

    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.7),
        ],
        ru_words=[
            _vts_word("поставь", "ru", 0.0, 0.3),
            _vts_word("таймер", "ru", 0.3, 0.7),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    timer_results = [r for r in results if r.command.name == "CommandsManager.set_timer"]
    assert len(timer_results) == 1


async def test_matrix_full_overlap_different_commands_primary_track_wins():
    """STT transcribes same voice in two languages, patterns phonetically match; en pattern 'stop music' and ru pattern 'стоп музыка' both match the
    same time range. Primary track (en) has lower global index (declared first) and wins."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "stop music"})
    async def stop_music_en() -> Response:
        return Response(text="stopped")

    @m.new({"ru": "стоп музыка"})
    async def stop_music_ru() -> Response:
        return Response(text="остановлено")

    vts = _make_vts(
        en_words=[
            _vts_word("stop", "en", 0.0, 0.3),
            _vts_word("music", "en", 0.3, 0.7),
        ],
        ru_words=[
            _vts_word("стоп", "ru", 0.0, 0.3),
            _vts_word("музыка", "ru", 0.3, 0.7),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.stop_music_en"


# --- matrix matching: partial overlap ---


async def test_matrix_partial_overlap_loser_removed():
    """User says 'set timer for five minutes play songs'. En matches 'set timer for five minutes'
    (0.0–1.5s), ru matches 'пять минут включи музыку' which overlaps at 'five minutes'/'пять минут'
    (0.9–1.5s). Neither can be cut to still match, so the loser (ru, higher index) is removed."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer for five minutes"})
    async def set_timer() -> Response:
        return Response(text="timer set")

    @m.new({"ru": "пять минут включи музыку"})
    async def play_after_five() -> Response:
        return Response(text="playing after 5")

    vts = _make_vts(
        en_words=[
            _vts_word("set", "en", 0.0, 0.3),
            _vts_word("timer", "en", 0.3, 0.6),
            _vts_word("for", "en", 0.6, 0.9),
            _vts_word("five", "en", 0.9, 1.2),
            _vts_word("minutes", "en", 1.2, 1.5),
            _vts_word("lucci", "en", 1.5, 1.8),
            _vts_word("music", "en", 1.8, 2.1),
        ],
        ru_words=[
            _vts_word("сет", "ru", 0.0, 0.3),
            _vts_word("таймер", "ru", 0.3, 0.6),
            _vts_word("фор", "ru", 0.6, 0.9),
            _vts_word("пять", "ru", 0.9, 1.2),
            _vts_word("минут", "ru", 1.2, 1.5),
            _vts_word("включи", "ru", 1.5, 1.8),
            _vts_word("музыку", "ru", 1.8, 2.1),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    assert len(results) == 1
    names = {r.command.name for r in results}
    assert "CommandsManager.set_timer" in names
    assert "CommandsManager.play_after_five" not in names


async def test_matrix_partial_overlap_winner_cuttable():
    """User says 'play some music stop timer'. En matches 'play * stop' which overlaps with
    ru 'стоп таймер' at 'stop'/'стоп'. The winner ('play * stop') can be cut to 'play some music'
    (still matches 'play *'), so both commands survive."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "play *"})
    async def play() -> Response:
        return Response(text="playing")

    @m.new({"ru": "стоп таймер"})
    async def stop_timer() -> Response:
        return Response(text="stopped")

    vts = _make_vts(
        en_words=[
            _vts_word("play", "en", 0.0, 0.3),
            _vts_word("some", "en", 0.3, 0.6),
            _vts_word("music", "en", 0.6, 0.9),
            _vts_word("stop", "en", 0.9, 1.2),
            _vts_word("timer", "en", 1.2, 1.5),
        ],
        ru_words=[
            _vts_word("плей", "ru", 0.0, 0.3),
            _vts_word("сом", "ru", 0.3, 0.6),
            _vts_word("музыка", "ru", 0.6, 0.9),
            _vts_word("стоп", "ru", 0.9, 1.2),
            _vts_word("таймер", "ru", 1.2, 1.5),
        ],
    )

    results = await SearchProcessor().search(vts, p, m.commands, [])
    assert len(results) == 2
    names = {r.command.name for r in results}
    assert "CommandsManager.play" in names
    assert "CommandsManager.stop_timer" in names


# --- matrix matching: TranscriptionString without VoiceTranscriptionTrack ---
#
# TranscriptionString carries alternative_texts but no timestamps.
# Matrix matching still searches all tracks, but translate_position falls back
# to text-based (substring) logic — which returns None for unrelated texts.
# This means cross-track overlap resolution can't work: overlapping results
# from different tracks both survive because the overlap check is skipped.


async def test_ts_no_timestamps_single_match_in_alt():
    """Command only has a Russian pattern. Primary en track doesn't match,
    but the ru alternative does — matrix finds it."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"ru": "включи музыку"})
    async def play_music() -> Response:
        return Response(text="playing")

    ts = TranscriptionString.from_words(
        [("turn", "en"), ("on", "en"), ("music", "en")],
        alternative_texts={"ru": LocaleString("включи музыку", "ru")},
    )

    results = await SearchProcessor().search(ts, p, m.commands, [])
    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.play_music"


async def test_ts_no_timestamps_two_commands_same_track_no_overlap():
    """Two en commands match from the primary track, no overlap — both kept."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"en": "play songs"})
    async def play_songs() -> Response:
        return Response(text="songs")

    ts = TranscriptionString.from_words(
        [("set", "en"), ("timer", "en"), ("and", "en"), ("play", "en"), ("songs", "en")],
        alternative_texts={"ru": LocaleString("сет таймер энд плей сонгс", "ru")},
    )

    results = await SearchProcessor().search(ts, p, m.commands, [])
    assert len(results) == 2
    names = {r.command.name for r in results}
    assert "CommandsManager.set_timer" in names
    assert "CommandsManager.play_songs" in names


async def test_ts_no_timestamps_two_commands_same_track_overlap_cuttable():
    """Two en commands overlap on the primary track. 'set timer *' matches
    'set timer for five minutes' and '* minutes stop' matches 'five minutes stop'.
    They overlap at 'five minutes'. The loser 'set timer *' is cut to
    'set timer for' which still matches — both survive."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer *"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"en": "stop"})
    async def stop_after() -> Response:
        return Response(text="stopped")

    ts = TranscriptionString.from_words(
        [("set", "en"), ("timer", "en"), ("for", "en"), ("five", "en"), ("minutes", "en"), ("stop", "en")],
        alternative_texts={"ru": LocaleString("сет таймер фор файв минутс стоп", "ru")},
    )

    results = await SearchProcessor().search(ts, p, m.commands, [])
    assert len(results) == 2
    names = {r.command.name for r in results}
    assert "CommandsManager.set_timer" in names
    assert "CommandsManager.stop_after" in names


async def test_ts_no_timestamps_cross_track_no_overlap():
    """En command and ru command don't overlap, but without timestamps the system
    can't confirm separate substring usage. Only the higher-priority (primary track)
    result should survive — cross-track results require explicit confirmation."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"ru": "включи музыку"})
    async def play_music() -> Response:
        return Response(text="playing")

    ts = TranscriptionString.from_words(
        [("set", "en"), ("timer", "en"), ("and", "en"), ("turn", "en"), ("on", "en"), ("music", "en")],
        alternative_texts={"ru": LocaleString("сет таймер и включи музыку", "ru")},
    )

    results = await SearchProcessor().search(ts, p, m.commands, [])
    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.set_timer"


async def test_ts_no_timestamps_cross_track_overlap():
    """En and ru commands overlap, but without timestamps the system can't resolve it.
    Only the higher-priority (primary track) result should survive."""
    p = PatternParser()
    m = CommandsManager()

    @m.new({"en": "set timer for five"})
    async def set_timer() -> Response:
        return Response(text="timer")

    @m.new({"ru": "пять минут включи музыку"})
    async def play_after() -> Response:
        return Response(text="playing")

    ts = TranscriptionString.from_words(
        [
            ("set", "en"),
            ("timer", "en"),
            ("for", "en"),
            ("five", "en"),
            ("minutes", "en"),
            ("turn", "en"),
            ("on", "en"),
            ("music", "en"),
        ],
        alternative_texts={"ru": LocaleString("сет таймер фор пять минут включи музыку", "ru")},
    )

    results = await SearchProcessor().search(ts, p, m.commands, [])
    assert len(results) == 1
    assert results[0].command.name == "CommandsManager.set_timer"
