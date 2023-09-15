import pytest
from core import Object, Word, Pattern
from general.classproperty import classproperty


class FullName(Object):
    first: Word
    second: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$first:Word $second:Word')

class ExtraParameterInAnnotation(Object):
    word1: Word = None
    word2: Word = None
    word3: Word = None
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word')

def test_nested_objects():
    Pattern.add_parameter_type(FullName)
    
    p = Pattern('$name:FullName')
    assert p
    assert p.compiled
    
    m = p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].first == Word('John')
    assert m[0].parameters['name'].second == Word('Galt')
    
def test_extra_parameter_in_annotation():
    Pattern.add_parameter_type(ExtraParameterInAnnotation)
    
    p = Pattern('$name:ExtraParameterInAnnotation')
    assert p
    assert p.compiled
    
    m = p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].word1 == Word('John')
    assert m[0].parameters['name'].word2 == Word('Galt')
    assert m[0].parameters['name'].word3 == None