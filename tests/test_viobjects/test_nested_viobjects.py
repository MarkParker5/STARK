import pytest
from VICore import VIObject, VIWord, Pattern
from VICore.VIObjects.VIObject import classproperty


class VIFullName(VIObject):
    first: VIWord
    second: VIWord

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$first:VIWord $second:VIWord')

class ExtraParameterInAnnotation(VIObject):
    word1: VIWord = None
    word2: VIWord = None
    word3: VIWord = None
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:VIWord $word2:VIWord')

def test_nested_viobjects():
    Pattern.add_parameter_type(VIFullName)
    
    p = Pattern('$name:VIFullName')
    assert p
    assert p.compiled
    
    m = p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].first == VIWord('John')
    assert m[0].parameters['name'].second == VIWord('Galt')
    
def test_extra_parameter_in_annotation():
    Pattern.add_parameter_type(ExtraParameterInAnnotation)
    
    p = Pattern('$name:ExtraParameterInAnnotation')
    assert p
    assert p.compiled
    
    m = p.match('John Galt')
    assert m
    assert set(m[0].parameters.keys()) == {'name'}
    assert m[0].parameters['name'].word1 == VIWord('John')
    assert m[0].parameters['name'].word2 == VIWord('Galt')
    assert m[0].parameters['name'].word3 == None