from stark.core import Pattern
from stark.core.patterns.parsing import ObjectParser, parse_object
from stark.core.types import Word

# def test_pattern():
#     assert Word.pattern == Pattern('*')

async def test_parse():
    word = (await parse_object(Word, ObjectParser(), 'foo')).obj
    assert word
    assert word.value == 'foo'

async def test_match():
    p = Pattern('foo $bar:Word baz')
    assert p

    m = await p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == Word('qwerty')

    m = await p.match('foo lorem ipsum dolor sit amet baz')
    assert not m

async def test_formatted():
    string = (await parse_object(Word, ObjectParser(), 'foo')).obj
    assert str(string) == '<Word value: "foo">'
    assert f'{string}' == 'foo'
