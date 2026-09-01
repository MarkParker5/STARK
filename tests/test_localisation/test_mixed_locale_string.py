import pytest

from stark.general.localisation import MixedLocaleString
from stark.general.localisation.mixed_locale_string import SpeechSegment


# ── MixedLocaleString construction ────────────────────────────────────────────

def test_segments_stored():
    segs = [SpeechSegment("hello", "en"), SpeechSegment("мир", "ru")]
    mls = MixedLocaleString(segs)
    assert mls.segments == tuple(segs)

def test_text_is_joined():
    mls = MixedLocaleString([SpeechSegment("hello", "en"), SpeechSegment("мир", "ru")])
    assert str(mls) == "hello мир"

def test_majority_language_by_char_count():
    # "привет" (6 chars) > "hi" (2 chars) → ru wins
    mls = MixedLocaleString([SpeechSegment("hi", "en"), SpeechSegment("привет", "ru")])
    assert mls.language_code == "ru"

def test_majority_language_en_wins():
    mls = MixedLocaleString([SpeechSegment("hello world", "en"), SpeechSegment("мир", "ru")])
    assert mls.language_code == "en"

def test_with_returns_plain_locale_string():
    mls = MixedLocaleString([SpeechSegment("hello", "en")])
    result = mls._with("bye")
    assert type(result) is not MixedLocaleString
    assert str(result) == "bye"


# ── MixedLocaleString.detect ───────────────────────────────────────────────────

pytest.importorskip("lingua", reason="lingua-language-detector not installed")


def test_detect_pure_english():
    mls = MixedLocaleString.detect("hello world how are you")
    assert len(mls.segments) >= 1
    assert mls.language_code == "en"

def test_detect_pure_russian():
    mls = MixedLocaleString.detect("привет мир как дела")
    assert len(mls.segments) >= 1
    assert mls.language_code == "ru"

def test_detect_mixed_en_ru():
    mls = MixedLocaleString.detect("I want to buy молоко и хлеб")
    langs = {s.language_code for s in mls.segments}
    assert "en" in langs or "ru" in langs  # at minimum detects something
    assert len(mls.segments) >= 1

def test_detect_returns_mixed_locale_string():
    result = MixedLocaleString.detect("buenos dias good morning")
    assert isinstance(result, MixedLocaleString)

def test_detect_text_preserved():
    text = "hello привет"
    mls = MixedLocaleString.detect(text)
    # all original words should appear somewhere in the segments
    reconstructed = " ".join(s.text for s in mls.segments)
    for word in text.split():
        assert word in reconstructed

def test_detect_no_lingua_raises_import_error(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "lingua", None)  # type: ignore[arg-type]
    # clear the cached detector so it re-evaluates the import
    from stark.general.localisation.mixed_locale_string import _get_detector
    _get_detector.cache_clear()
    with pytest.raises((ImportError, AttributeError)):
        MixedLocaleString.detect("hello world")
    # restore for subsequent tests
    _get_detector.cache_clear()
