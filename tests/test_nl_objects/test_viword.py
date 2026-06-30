from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import Word

# def test_pattern():
#     assert Word.pattern == Pattern('*')


parser = PatternParser()


async def test_parse():
    word = (await parser.parse_object(Word, "hello")).obj
    assert word
    assert word.value == "hello"


async def test_match():
    p = Pattern("play $song:Word now")
    assert p

    m = await parser.match(p, "play stairway now")
    assert m
    assert m[0].parameters["song"] == Word("stairway")

    m = await parser.match(p, "play lorem ipsum dolor sit amet now")
    assert not m


async def test_formatted():
    string = (await parser.parse_object(Word, "hello")).obj
    assert str(string) == '<Word value: "hello">'
    assert f"{string}" == "hello"
