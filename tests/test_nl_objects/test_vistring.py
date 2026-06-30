from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import String


def test_pattern():
    assert String.pattern == Pattern("**")


parser = PatternParser()


async def test_parse():
    match = await parser.parse_object(String, "a")
    assert match
    match2 = await parser.parse_object(String, "play some jazz music")
    assert match2.obj.value == "play some jazz music"


async def test_match():
    p = Pattern("play $song:String now")
    assert p

    m = await parser.match(p, "play stairway now")
    assert m
    assert m[0].parameters["song"] == String("stairway")

    m = await parser.match(p, "play lorem ipsum dolor sit amet now")
    assert m
    assert m[0].parameters["song"] == String("lorem ipsum dolor sit amet")


async def test_formatted():
    string = (await parser.parse_object(String, "play some jazz music")).obj
    assert str(string) == '<String value: "play some jazz music">'
    assert f"{string}" == "play some jazz music"
