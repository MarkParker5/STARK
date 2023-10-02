
import pytest 
from stark.core import Pattern
from stark.core.types import Object, ParseError
from stark.general.classproperty import classproperty
from stark.models.transcription import Transcription, TranscriptionTrack
from stark.general.localisation import Localizer


class Lorem(Object):
    
    @classproperty
    def pattern(cls):
        return Pattern('* ipsum')
    
    async def did_parse(self, track: TranscriptionTrack, transcription: Transcription, re_match_group: dict[str, str]) -> tuple[TranscriptionTrack, Transcription]:
        if not 'lorem' in track.text:
            raise ParseError('lorem not found')
        self.value = 'lorem'
        time = next(iter(track.get_time('lorem')))
        return track.get_slice(*time), transcription.get_slice(*time)
    
async def test_complex_parsing_failed(get_transcription):
    with pytest.raises(ParseError):
        transcription = get_transcription('some lor ipsum')
        track = transcription.best
        await Lorem.parse(track, transcription)
    
async def test_complex_parsing(get_transcription):
    string = 'some lorem ipsum'
    transcription = get_transcription(string)
    track = transcription.best
    match = await Lorem.parse(track, transcription)
    assert match
    assert match.obj
    assert match.obj.value == 'lorem'
    assert match.track.text == 'lorem'
    assert (await Lorem.pattern.match(transcription, Localizer()))[0].subtrack.text == 'lorem ipsum'
    