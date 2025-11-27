from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import String


def test_pattern():
    assert String.pattern == Pattern("**")


parser = PatternParser()


async def test_parse():
    match = await parser.parse_object(String, "a")
    assert match
    match2 = await parser.parse_object(String, "foo bar baz")
    assert match2.obj.value == "foo bar baz"


async def test_match():
    p = Pattern("foo $bar:String baz")
    assert p

    m = await parser.match(p, "foo qwerty baz")
    assert m
    assert m[0].parameters["bar"] == String("qwerty")

    m = await parser.match(p, "foo lorem ipsum dolor sit amet baz")
    assert m
    assert m[0].parameters["bar"] == String("lorem ipsum dolor sit amet")


async def test_formatted():
    string = (await parser.parse_object(String, "foo bar baz")).obj
    assert str(string) == '<String value: "foo bar baz">'
    assert f"{string}" == "foo bar baz"
