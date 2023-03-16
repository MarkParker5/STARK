import re
import pytest
from VICore import Pattern, VIObject, VIWord, VIString
from VICore.patterns import expressions
from VICore.VIObjects.VIObject import classproperty


word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'
    
class ExtraParameterInPattern(VIObject):
    word1: VIWord
    word2: VIWord
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:VIWord $word2:VIWord $word3:VIWord')

def test_typed_parameters():
    p = Pattern('lorem $name:VIWord dolor')
    assert p.parameters == {'name': VIWord}
    assert p.compiled == fr'lorem (?P<name>{word}) dolor'
    
    m = p.match('lorem ipsum dolor')
    assert m
    assert m[0].substring == 'lorem ipsum dolor'
    assert m[0].parameters == {'name': VIWord('ipsum')}
    assert not p.match('lorem ipsum foo dolor')
    
    p = Pattern('lorem $name:VIString dolor')
    assert p.parameters == {'name': VIString}
    m = p.match('lorem ipsum foo bar dolor')
    assert m
    assert m[0].substring == 'lorem ipsum foo bar dolor'
    assert m[0].parameters == {'name': VIString('ipsum foo bar')}
    
def test_undefined_typed_parameters():
    pattern = 'lorem $name:Lorem dolor'
    with pytest.raises(NameError, match=re.escape(f'Unknown type: "Lorem" for parameter: "name" in pattern: "{pattern}"')):
        Pattern(pattern)
        
def test_extra_parameter_in_pattern():
    with pytest.raises(AssertionError, match='Can`t add parameter type "ExtraParameterInPattern": pattern parameters do not match properties annotated in class'):
        Pattern.add_parameter_type(ExtraParameterInPattern)