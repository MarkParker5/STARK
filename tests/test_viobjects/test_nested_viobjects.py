from stark.core import Pattern
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty


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

async def test_nested_objects():
    Pattern.add_parameter_type(FullName)

    p = Pattern('$name:FullName')
    assert p
    assert p.compiled

    m = await p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].first == Word('John')
    assert m[0].parameters['name'].second == Word('Galt')

async def test_extra_parameter_in_annotation():
    Pattern.add_parameter_type(ExtraParameterInAnnotation)

    p = Pattern('$name:ExtraParameterInAnnotation')
    assert p
    assert p.compiled

    m = await p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].word1 == Word('John')
    assert m[0].parameters['name'].word2 == Word('Galt')
    assert not hasattr(m[0].parameters['name'], 'word3')
