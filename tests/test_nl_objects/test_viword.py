from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import Word

# def test_pattern():
#     assert Word.pattern == Pattern('*')


parser = PatternParser()


async def test_parse():
    word = (await parser.parse_object(Word, "foo")).obj
    assert word
    assert word.value == "foo"


async def test_match():
    p = Pattern("foo $bar:Word baz")
    assert p

    m = await parser.match(p, "foo qwerty baz")
    assert m
    assert m[0].parameters["bar"] == Word("qwerty")

    m = await parser.match(p, "foo lorem ipsum dolor sit amet baz")
    assert not m


async def test_formatted():
    string = (await parser.parse_object(Word, "foo")).obj
    assert str(string) == '<Word value: "foo">'
    assert f"{string}" == "foo"
