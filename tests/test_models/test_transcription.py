import pytest

from stark.models.voice_transcription import VoiceTranscriptionTrack, VoiceTranscriptionWord


@pytest.fixture
def transcription_track():
    return VoiceTranscriptionTrack(
        text='please play some jazz music now',
        result=[
            VoiceTranscriptionWord(word='please', language_code='en', char_start=0, char_end=6, start=0.0, end=0.5, conf=0.9),
            VoiceTranscriptionWord(word='play', language_code='en', char_start=7, char_end=11, start=0.5, end=0.7, conf=0.8),
            VoiceTranscriptionWord(word='some', language_code='en', char_start=12, char_end=16, start=0.7, end=0.8, conf=0.7),
            VoiceTranscriptionWord(word='jazz', language_code='en', char_start=17, char_end=21, start=0.8, end=1.1, conf=0.6),
            VoiceTranscriptionWord(word='music', language_code='en', char_start=22, char_end=27, start=1.1, end=1.8, conf=0.5),
            VoiceTranscriptionWord(word='now', language_code='en', char_start=28, char_end=31, start=1.8, end=2.2, conf=0.4),
        ],
        language_code='en',
    )


def check_sorted(track: VoiceTranscriptionTrack):
    for i, word in enumerate(track.result):
        assert i == 0 or track.result[i - 1].end <= word.start


def test_replace(transcription_track):
    transcription_track.replace('jazz', 'rock')
    check_sorted(transcription_track)
    assert transcription_track.text == 'please play some rock music now'
    assert transcription_track.result[3].word == 'rock'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.1


def test_replace_multiple_words(transcription_track):
    transcription_track.replace('jazz music', 'rock')
    check_sorted(transcription_track)
    assert transcription_track.text == 'please play some rock now'
    assert transcription_track.result[3].word == 'rock'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.8
    assert transcription_track.result[4].word == 'now'
    assert transcription_track.result[4].start == 1.8
    assert transcription_track.result[4].end == 2.2


def test_replace_empty_substring(transcription_track):
    transcription_track.replace('', 'rock')
    check_sorted(transcription_track)
    assert transcription_track.text == 'please play some jazz music now'
    assert transcription_track.result[3].word == 'jazz'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.1


def test_get_slice(transcription_track):
    new_track = transcription_track.get_slice(1.0, 1.5)
    check_sorted(new_track)
    assert new_track.text == 'music'
    assert len(new_track.result) == 1
    assert new_track.result[0].word == 'music'
    assert new_track.result[0].start == 1.1
    assert new_track.result[0].end == 1.8

    new_track = transcription_track.get_slice(0.9, 1.5)
    check_sorted(new_track)
    assert new_track.text == 'jazz music'
    assert len(new_track.result) == 2


def test_get_time(transcription_track):
    times = list(transcription_track.get_time('jazz'))
    assert len(times) == 1
    assert times[0][0] == 0.8
    assert times[0][1] == 1.1


def test_get_time_multiple_words(transcription_track):
    times = list(transcription_track.get_time('jazz music'))
    assert len(times) == 1
    assert times[0][0] == 0.8
    assert times[0][1] == 1.8


def test_get_time_not_found(transcription_track):
    times = list(transcription_track.get_time('rock'))
    assert len(times) == 0


def test_get_time_out_of_range(transcription_track):
    times = list(transcription_track.get_time('jazz', to_index=2))
    assert len(times) == 0


def test_confidence(transcription_track):
    conf = transcription_track.confidence
    assert 0 < conf < 1


def test_to_voice_transcription_string(transcription_track):
    vts = transcription_track.to_voice_transcription_string()
    assert vts == 'please play some jazz music now'
    assert vts.track is transcription_track
    assert len(vts.words) == 6
    assert vts.words[0].word == 'please'
