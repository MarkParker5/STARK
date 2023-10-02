import re
import pytest
from stark.core import Pattern
from stark.core.types import Object, Word, String
from stark.core.patterns import expressions
from stark.general.classproperty import classproperty
from stark.general.localisation import Localizer


word = fr'[{expressions.alphanumerics}]*'
words = fr'[{expressions.alphanumerics}\s]*'
    
class ExtraParameterInPattern(Object):
    word1: Word
    word2: Word
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word $word3:Word')

async def test_typed_parameters(get_transcription):
    p = Pattern('lorem $name:Word dolor')
    p.get_compiled('en', Localizer())
    assert p.parameters == {'name': Word}
    # assert p._compiled['en'] == fr'lorem (?P<name>{word}) dolor'
    
    m = await p.match(get_transcription('lorem ipsum dolor'), Localizer())
    assert m
    assert m[0].subtrack.text == 'lorem ipsum dolor'
    assert m[0].parameters == {'name': Word('ipsum')}
    assert not await p.match(get_transcription('lorem ipsum foo dolor'), Localizer())
    
    p = Pattern('lorem $name:String dolor')
    assert p.parameters == {'name': String}
    m = await p.match(get_transcription('lorem ipsum foo bar dolor'), Localizer())
    assert m
    assert m[0].subtrack.text == 'lorem ipsum foo bar dolor'
    assert m[0].parameters == {'name': String('ipsum foo bar')}
    
def test_undefined_typed_parameters():
    pattern = 'lorem $name:Lorem dolor'
    with pytest.raises(NameError, match=re.escape(f'Unknown type: "Lorem" for parameter: "name" in pattern: "{pattern}"')):
        Pattern(pattern)
        
def test_extra_parameter_in_pattern():
    with pytest.raises(AssertionError, match='Can`t add parameter type "ExtraParameterInPattern": pattern parameters do not match properties annotated in class'):
        Pattern.add_parameter_type(ExtraParameterInPattern)