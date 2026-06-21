from stark.general.localisation import LocaleString
from stark.models.transcription_string import (
    TranscriptionString,
    TranscriptionWord,
)


# --- Construction ---


def test_from_words_basic():
    ts = TranscriptionString.from_words([("hello", "en"), ("мир", "ru")])
    assert ts == "hello мир"
    assert ts.language_code == "en"
    assert len(ts.words) == 2
    assert ts.words[0].word == "hello"
    assert ts.words[0].language_code == "en"
    assert ts.words[1].word == "мир"
    assert ts.words[1].language_code == "ru"


def test_from_words_char_offsets():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de")])
    assert ts.words[0].char_start == 0
    assert ts.words[0].char_end == 3
    assert ts.words[1].char_start == 4
    assert ts.words[1].char_end == 9
    assert ts.words[2].char_start == 10
    assert ts.words[2].char_end == 14


def test_empty():
    ts = TranscriptionString()
    assert ts == ""
    assert ts.language_code == "base"
    assert len(ts.words) == 0


def test_plain_str_compatible():
    ts = TranscriptionString("hello", "en")
    assert ts == "hello"
    assert isinstance(ts, str)
    assert isinstance(ts, LocaleString)


def test_language_code_majority():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de")])
    assert ts.language_code == "en"


def test_language_code_all_same():
    ts = TranscriptionString.from_words([("hello", "ru"), ("мир", "ru")])
    assert ts.language_code == "ru"


def test_alternative_texts():
    alts = {"ru": LocaleString("привет мир", "ru"), "de": LocaleString("hallo welt", "de")}
    ts = TranscriptionString.from_words([("hello", "en"), ("world", "en")], alternative_texts=alts)
    assert ts.alternative_texts["ru"] == "привет мир"
    assert ts.alternative_texts["de"] == "hallo welt"


# --- Slicing (__getitem__) ---


def test_slice_preserves_words():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de"), ("часа", "ru")])
    # "set timer zwei часа"
    sliced = ts[10:]  # "zwei часа"
    assert sliced == "zwei часа"
    assert isinstance(sliced, TranscriptionString)
    assert len(sliced.words) == 2
    assert sliced.words[0].word == "zwei"
    assert sliced.words[0].language_code == "de"
    assert sliced.words[1].word == "часа"
    assert sliced.words[1].language_code == "ru"


def test_slice_adjusts_char_offsets():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de")])
    sliced = ts[4:]  # "timer zwei"
    assert sliced.words[0].char_start == 0
    assert sliced.words[0].char_end == 5
    assert sliced.words[1].char_start == 6
    assert sliced.words[1].char_end == 10


def test_slice_language_resolves_per_substring():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de"), ("часа", "ru")])
    # Full string: majority is "en"
    assert ts.language_code == "en"
    # Slice "zwei часа": no majority (1 de, 1 ru), first wins in Counter
    sliced = ts[10:]
    assert sliced.language_code in ("de", "ru")


def test_full_copy_slice():
    ts = TranscriptionString.from_words([("hello", "en"), ("world", "en")])
    copy = ts[:]
    assert copy == "hello world"
    assert isinstance(copy, TranscriptionString)
    assert len(copy.words) == 2


def test_single_char_slice():
    ts = TranscriptionString.from_words([("hi", "en")])
    c = ts[0]
    assert c == "h"
    assert isinstance(c, TranscriptionString)


# --- _with ---


def test_with_finds_substring():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de")])
    sub = ts._with("timer zwei")
    assert sub == "timer zwei"
    assert len(sub.words) == 2
    assert sub.words[0].word == "timer"
    assert sub.words[1].word == "zwei"


def test_with_not_found():
    ts = TranscriptionString.from_words([("hello", "en")])
    sub = ts._with("xyz")
    assert sub == "xyz"
    assert len(sub.words) == 0


# --- replace ---


def test_replace_removes_words():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de"), ("часа", "ru")])
    # Remove "timer"
    result = ts.replace("timer ", "")
    assert result == "set zwei часа"
    assert isinstance(result, TranscriptionString)
    words = result.words
    assert len(words) == 3
    assert words[0].word == "set"
    assert words[1].word == "zwei"
    assert words[2].word == "часа"


def test_replace_with_substitution():
    ts = TranscriptionString.from_words([("hello", "en"), ("мир", "ru")])
    result = ts.replace("hello", "hi")
    assert result == "hi мир"
    assert isinstance(result, TranscriptionString)
    assert result.words[0].word == "hi"
    assert result.words[0].language_code == "en"


def test_replace_adjusts_offsets():
    ts = TranscriptionString.from_words([("set", "en"), ("timer", "en"), ("zwei", "de")])
    result = ts.replace("timer", "t")
    # "set t zwei"
    assert result == "set t zwei"
    assert result.words[2].char_start == 6  # "zwei" shifted left


# --- strip ---


def test_strip_preserves_words():
    ts = TranscriptionString("  hello world  ", "en", [
        TranscriptionWord("hello", "en", 2, 7),
        TranscriptionWord("world", "en", 8, 13),
    ])
    stripped = ts.strip()
    assert stripped == "hello world"
    assert isinstance(stripped, TranscriptionString)
    assert len(stripped.words) == 2
    assert stripped.words[0].char_start == 0


# --- split ---


def test_split_preserves_words():
    ts = TranscriptionString.from_words([("hello", "en"), ("мир", "ru"), ("foo", "de")])
    parts = ts.split()
    assert len(parts) == 3
    assert all(isinstance(p, TranscriptionString) for p in parts)
    assert parts[0] == "hello"
    assert parts[0].words[0].language_code == "en"
    assert parts[1] == "мир"
    assert parts[1].words[0].language_code == "ru"


# --- removing ---


def test_removing():
    ts = TranscriptionString.from_words([("hello", "en"), ("world", "en")])
    result = ts.removing("hello ")
    assert result == "world"
    assert isinstance(result, TranscriptionString)


def test_removing_on_locale_string():
    ls = LocaleString("hello world", "en")
    result = ls.removing("hello ")
    assert result == "world"
    assert isinstance(result, LocaleString)


# --- repr ---


def test_repr():
    ts = TranscriptionString.from_words([("hello", "en")])
    r = repr(ts)
    assert "TranscriptionString" in r
    assert "en" in r


# --- integration: language resolution through slicing ---


def test_mixed_language_parameter_slicing():
    """Simulates what the parser does: slice a parameter substring and resolve its language."""
    ts = TranscriptionString.from_words([
        ("set", "en"), ("timer", "en"), ("for", "en"),
        ("zwei", "de"), ("часа", "ru"),
    ])
    # Overall language is English (3 en words vs 1 de + 1 ru)
    assert ts.language_code == "en"

    # Parser slices the Duration parameter: "zwei часа"
    param_start = ts.index("zwei")
    param_end = len(ts)
    param_substr = ts[param_start:param_end]

    assert param_substr == "zwei часа"
    assert isinstance(param_substr, TranscriptionString)
    # Per-word languages preserved
    assert param_substr.words[0].language_code == "de"
    assert param_substr.words[1].language_code == "ru"
    # Majority language of the parameter is not English
    assert param_substr.language_code != "en"
