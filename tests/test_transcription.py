import pytest
from stark.models.transcription import TranscriptionTrack, TranscriptionWord

@pytest.fixture
def transcription_track():
    return TranscriptionTrack(
        text='This is a test transcription track',
        result=[
            TranscriptionWord(word='This', start=0.0, end=0.5, conf=0.9),
            TranscriptionWord(word='is', start=0.5, end=0.7, conf=0.8),
            TranscriptionWord(word='a', start=0.7, end=0.8, conf=0.7),
            TranscriptionWord(word='test', start=0.8, end=1.1, conf=0.6),
            TranscriptionWord(word='transcription', start=1.1, end=1.8, conf=0.5),
            TranscriptionWord(word='track', start=1.8, end=2.2, conf=0.4),
        ],
        spk=[],
        spk_frames=0,
        language_code='en-US',
    )
    
def check_sorted(track: TranscriptionTrack):
    for i, word in enumerate(track.result):
        print(i, word)
        assert i == 0 or track.result[i-1].end <= word.start

def test_replace(transcription_track):
    transcription_track.replace('test', 'example')
    check_sorted(transcription_track)
    assert transcription_track.text == 'This is a example transcription track'
    assert transcription_track.result[3].word == 'example'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.1

def test_replace_multiple_words(transcription_track):
    transcription_track.replace('test transcription', 'example')
    check_sorted(transcription_track)
    assert transcription_track.text == 'This is a example track'
    assert transcription_track.result[3].word == 'example'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.8
    assert transcription_track.result[4].word == 'track'
    assert transcription_track.result[4].start == 1.8
    assert transcription_track.result[4].end == 2.2

def test_replace_empty_substring(transcription_track):
    transcription_track.replace('', 'example')
    check_sorted(transcription_track)
    assert transcription_track.text == 'This is a test transcription track'
    assert transcription_track.result[3].word == 'test'
    assert transcription_track.result[3].start == 0.8
    assert transcription_track.result[3].end == 1.1

def test_get_slice(transcription_track):
    new_track = transcription_track.get_slice(1.0, 1.5)
    check_sorted(new_track)
    assert new_track.text == 'transcription'
    assert len(new_track.result) == 1
    assert new_track.result[0].word == 'transcription'
    assert new_track.result[0].start == 1.1
    assert new_track.result[0].end == 1.8
    
    new_track = transcription_track.get_slice(0.9, 1.5)
    check_sorted(new_track)
    assert new_track.text == 'test transcription'
    assert len(new_track.result) == 2

def test_get_time(transcription_track):
    times = list(transcription_track.get_time('test'))
    assert len(times) == 1
    assert times[0][0] == 0.8
    assert times[0][1] == 1.1

def test_get_time_multiple_words(transcription_track):
    times = list(transcription_track.get_time('test transcription'))
    assert len(times) == 1
    assert times[0][0] == 0.8
    assert times[0][1] == 1.8

def test_get_time_not_found(transcription_track):
    times = list(transcription_track.get_time('example'))
    assert len(times) == 0

def test_get_time_out_of_range(transcription_track):
    times = list(transcription_track.get_time('test', to_index=2))
    assert len(times) == 0
