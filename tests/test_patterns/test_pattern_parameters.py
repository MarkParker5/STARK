import re

import pytest

from stark.core import Pattern
from stark.core.patterns import rules
from stark.core.types import Object, String, Word
from stark.general.classproperty import classproperty

word = fr'[{rules.alphanumerics}]+'
words = fr'[{rules.alphanumerics}\s]*'

class ExtraParameterInPattern(Object):
    word1: Word
    word2: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word $word3:Word')

async def test_typed_parameters():
    p = Pattern('lorem $name:Word dolor')
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == Word
    assert p.compiled == fr'lorem (?P<name>{word}) dolor'

    m = await p.match('lorem ipsum dolor')
    assert m
    assert m[0].substring == 'lorem ipsum dolor'
    assert m[0].parameters['name'] == Word('ipsum')
    assert not await p.match('lorem ipsum foo dolor')

    p = Pattern('lorem $name:String dolor')
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == String
    m = await p.match('lorem ipsum foo bar dolor')
    assert m
    assert m[0].substring == 'lorem ipsum foo bar dolor'
    assert m[0].parameters['name'] == String('ipsum foo bar')

def test_undefined_typed_parameters():
    pattern = 'lorem $name:Lorem dolor'
    with pytest.raises(NameError, match=re.escape(f'Unknown type: "Lorem" for parameter: "name" in pattern: "{pattern}"')):
        Pattern(pattern)

@pytest.mark.skip(reason="Refactored") # TODO: review
def test_extra_parameter_in_pattern():
    with pytest.raises(AssertionError, match='Can`t add parameter type "ExtraParameterInPattern": pattern parameters do not match properties annotated in class'):
        Pattern.add_parameter_type(ExtraParameterInPattern)

async def test_middle_optional_parameter():
    p = Pattern('lorem $name:Word? dolor')
    print(p.compiled)
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == Word

    assert await p.match('lorem  dolor')
    # assert await p.match('lorem dolor')

    m2 = await p.match('lorem ipsum dolor')
    assert m2
    assert m2[0].parameters['name'] == Word('ipsum')

async def test_trailing_optional_parameter():
    p = Pattern('lorem $name:Word?')
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == Word

    assert await p.match('lorem ')
    # assert await p.match('lorem')
    m = await p.match('lorem ipsum')
    assert m
    assert m[0].parameters['name'] == Word('ipsum')

async def test_optional_group():
    p = Pattern('lorem( ipsum $name:Word)? dolor')
    # assert p.parameters == {('name', Word, True)}
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == Word

    assert await p.match('lorem dolor')

    m2 = await p.match('lorem ipsum variable dolor')
    assert m2
    assert m2[0].parameters['name'] == Word('variable')


class TwoWords(Object):
    word1: Word
    word2: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$word1:Word $word2:Word')

Pattern.add_parameter_type(TwoWords)

async def test_parameter_type_duplicate():
    # test fix for re.error: redefinition of group name
    p = Pattern('hello $name:TwoWords and $name2:TwoWords')
    assert Pattern._parameter_types[p.parameters['name'].type_name].type == TwoWords
    m = await p.match('hello John Galt and Alice Smith')
    assert m
