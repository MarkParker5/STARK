from stark.core import Pattern
from stark.core.patterns.parsing import parse_object
from stark.core.types import String


def test_pattern():
    assert String.pattern == Pattern('**')

async def test_parse():
    from stark.core.patterns.parsing import ObjectParser
    match = await parse_object(String, ObjectParser(), 'a')
    assert match
    match2 = await parse_object(String, ObjectParser(), 'foo bar baz')
    assert match2.obj.value == 'foo bar baz'

async def test_match():
    p = Pattern('foo $bar:String baz')
    assert p

    m = await p.match('foo qwerty baz')
    assert m
    assert m[0].parameters['bar'] == String('qwerty')

    m = await p.match('foo lorem ipsum dolor sit amet baz')
    assert m
    assert m[0].parameters['bar'] == String('lorem ipsum dolor sit amet')

async def test_formatted():
    from stark.core.patterns.parsing import ObjectParser
    string = (await parse_object(String, ObjectParser(), 'foo bar baz')).obj
    assert str(string) == '<String value: "foo bar baz">'
    assert f'{string}' == 'foo bar baz'
