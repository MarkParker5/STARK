from stark.core import Pattern
from stark.core.types import String
from stark.general.localisation import Localizer


def test_pattern():
    assert String.pattern == Pattern('**')
    
async def test_parse(get_transcription):
    transcription = get_transcription('')
    track = transcription.best
    assert await String.parse(track, transcription)
    transcription = get_transcription('foo bar baz')
    track = transcription.best
    assert (await String.parse(track, transcription)).obj.value == 'foo bar baz'
    
async def test_match(get_transcription):
    p = Pattern('foo $bar:String baz')
    assert p
    
    m = await p.match(get_transcription('foo qwerty baz'), Localizer())
    assert m
    assert m[0].parameters['bar'] == String('qwerty')
    
    m = await p.match(get_transcription('foo lorem ipsum dolor sit amet baz'), Localizer())
    assert m
    assert m[0].parameters['bar'] == String('lorem ipsum dolor sit amet')
    
async def test_formatted(get_transcription):
    transcription = get_transcription('foo bar baz')
    track = transcription.best
    string = (await String.parse(track, transcription)).obj
    assert str(string) == '<String value: "foo bar baz">'
    assert f'{string}' == 'foo bar baz'
