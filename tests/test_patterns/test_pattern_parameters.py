import re
import pytest
from core import Pattern, Object, Word, String
from core.patterns import expressions
from general.classproperty import classproperty


word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'
    
class ExtraParameterInPattern(Object):
    word1: Word
    word2: Word
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word $word3:Word')

def test_typed_parameters():
    p = Pattern('lorem $name:Word dolor')
    assert p.parameters == {'name': Word}
    assert p.compiled == fr'lorem (?P<name>{word}) dolor'
    
    m = p.match('lorem ipsum dolor')
    assert m
    assert m[0].substring == 'lorem ipsum dolor'
    assert m[0].parameters == {'name': Word('ipsum')}
    assert not p.match('lorem ipsum foo dolor')
    
    p = Pattern('lorem $name:String dolor')
    assert p.parameters == {'name': String}
    m = p.match('lorem ipsum foo bar dolor')
    assert m
    assert m[0].substring == 'lorem ipsum foo bar dolor'
    assert m[0].parameters == {'name': String('ipsum foo bar')}
    
def test_undefined_typed_parameters():
    pattern = 'lorem $name:Lorem dolor'
    with pytest.raises(NameError, match=re.escape(f'Unknown type: "Lorem" for parameter: "name" in pattern: "{pattern}"')):
        Pattern(pattern)
        
def test_extra_parameter_in_pattern():
    with pytest.raises(AssertionError, match='Can`t add parameter type "ExtraParameterInPattern": pattern parameters do not match properties annotated in class'):
        Pattern.add_parameter_type(ExtraParameterInPattern)