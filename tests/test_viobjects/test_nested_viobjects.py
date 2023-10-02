import pytest
from stark.core import Pattern
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty
from stark.general.localisation import Localizer


class FullName(Object):
    first: Word
    second: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$first:Word $second:Word')

class ExtraParameterInAnnotation(Object):
    word1: Word
    word2: Word
    word3: Word
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word')

async def test_nested_objects(get_transcription):
    Pattern.add_parameter_type(FullName)
    
    p = Pattern('$name:FullName')
    assert p
    p.get_compiled('en', Localizer())
    assert p._compiled
    
    m = await p.match(get_transcription('John Galt'), Localizer())
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert isinstance(m[0].parameters['name'], FullName)
    assert m[0].parameters['name'].first == Word('John')
    assert m[0].parameters['name'].second == Word('Galt')
    
async def test_extra_parameter_in_annotation(get_transcription):
    Pattern.add_parameter_type(ExtraParameterInAnnotation)
    
    p = Pattern('$name:ExtraParameterInAnnotation')
    assert p
    p.get_compiled('en', Localizer())
    assert p._compiled
    
    m = await p.match(get_transcription('John Galt'), Localizer())
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert isinstance(m[0].parameters['name'], ExtraParameterInAnnotation)
    assert m[0].parameters['name'].word1 == Word('John')
    assert m[0].parameters['name'].word2 == Word('Galt')
    assert not hasattr(m[0].parameters['name'], 'word3')
