import pytest

from stark.general.localisation import LocaleString
from stark.models.voice_transcription import (
    Transcription,
    VoiceTranscriptionTrack,
    VoiceTranscriptionWord,
)
from stark.models.voice_transcription_string import VoiceTranscriptionString


def _make_track(words_data: list[tuple[str, str, float, float, float]], lang: str = 'en') -> VoiceTranscriptionTrack:
    offset = 0
    words = []
    for word, wlang, start, end, conf in words_data:
        words.append(VoiceTranscriptionWord(
            word=word, language_code=wlang,
            char_start=offset, char_end=offset + len(word),
            start=start, end=end, conf=conf,
        ))
        offset += len(word) + 1
    text = ' '.join(w.word for w in words)
    return VoiceTranscriptionTrack(text=text, result=words, language_code=lang)


@pytest.fixture
def vts():
    track = _make_track([
        ('set', 'en', 0.0, 0.3, 0.9),
        ('timer', 'en', 0.3, 0.7, 0.8),
        ('for', 'en', 0.7, 0.9, 0.9),
        ('zwei', 'de', 0.9, 1.2, 0.7),
        ('часа', 'ru', 1.2, 1.6, 0.8),
    ])
    return track.to_voice_transcription_string()


def test_basic_properties(vts):
    assert vts == 'set timer for zwei часа'
    assert isinstance(vts, VoiceTranscriptionString)
    assert vts.track is not None
    assert len(vts.words) == 5


def test_slice_preserves_track(vts):
    sliced = vts[14:]  # "zwei часа"
    assert sliced == 'zwei часа'
    assert isinstance(sliced, VoiceTranscriptionString)
    assert sliced.track is not None
    assert len(sliced.track.result) >= 1


def test_slice_language_from_words(vts):
    sliced = vts[14:]  # "zwei часа"
    assert sliced.language_code in ('de', 'ru')


def test_with_preserves_track(vts):
    sub = vts._with('timer for')
    assert sub == 'timer for'
    assert isinstance(sub, VoiceTranscriptionString)
    assert sub.track is not None


def test_replace_updates_track(vts):
    result = vts.replace('timer', 'clock')
    assert result == 'set clock for zwei часа'
    assert isinstance(result, VoiceTranscriptionString)
    assert result.track is not None
    assert 'clock' in result.track.text


def test_strip_preserves_track():
    track = _make_track([('hello', 'en', 0.0, 0.5, 0.9)])
    vts = VoiceTranscriptionString('  hello  ', 'en', track=track,
        words=(VoiceTranscriptionWord(word='hello', language_code='en', char_start=2, char_end=7, start=0.0, end=0.5, conf=0.9),))
    stripped = vts.strip()
    assert stripped == 'hello'
    assert isinstance(stripped, VoiceTranscriptionString)


def test_transcription_to_voice_transcription_string():
    en_track = _make_track([
        ('set', 'en', 0.0, 0.3, 0.9),
        ('timer', 'en', 0.3, 0.7, 0.8),
    ], lang='en')
    ru_track = _make_track([
        ('сет', 'ru', 0.0, 0.3, 0.3),
        ('таймер', 'ru', 0.3, 0.7, 0.4),
    ], lang='ru')

    transcription = Transcription(
        best=en_track,
        origins={'en': en_track, 'ru': ru_track},
    )

    vts = transcription.to_voice_transcription_string()
    assert vts == 'set timer'
    assert isinstance(vts, VoiceTranscriptionString)
    assert 'en' in vts.alternative_texts
    assert 'ru' in vts.alternative_texts
    assert vts.alternative_texts['ru'] == 'сет таймер'


def test_repr(vts):
    r = repr(vts)
    assert 'VoiceTranscriptionString' in r
    assert 'has_track=True' in r
