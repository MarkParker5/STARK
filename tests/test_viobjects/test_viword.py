from stark.core import Pattern
from stark.core.types import Word
from stark.general.localisation import Localizer


def test_pattern():
    assert Word.pattern == Pattern('*')
    
async def test_parse(get_transcription):
    transcription = get_transcription('foo')
    track = transcription.best
    word = (await Word.parse(track, transcription)).obj
    assert word
    assert word.value == 'foo'
    
async def test_match(get_transcription):
    p = Pattern('foo $bar:Word baz')
    assert p
    
    m = await p.match(get_transcription('foo qwerty baz'), Localizer())
    assert m
    assert m[0].parameters['bar'] == Word('qwerty')
    
    m = await p.match(get_transcription('foo lorem ipsum dolor sit amet baz'), Localizer())
    assert not m
    
async def test_formatted(get_transcription):
    transcription = get_transcription('foo')
    track = transcription.best
    string = (await Word.parse(track, transcription)).obj
    assert str(string) == '<Word value: "foo">'
    assert f'{string}' == 'foo'
