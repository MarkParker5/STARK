from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import NLWord

# def test_pattern():
#     assert NLWord.pattern == Pattern('*')


parser = PatternParser()


async def test_parse():
    word = (await parser.parse_object(NLWord, "hello")).obj
    assert word
    assert word.value == "hello"


async def test_match():
    p = Pattern("play $song:NLWord now")
    assert p

    m = await parser.match(p, "play stairway now")
    assert m
    assert m[0].parameters["song"] == NLWord("stairway")

    m = await parser.match(p, "play lorem ipsum dolor sit amet now")
    assert not m


async def test_formatted():
    string = (await parser.parse_object(NLWord, "hello")).obj
    assert str(string) == '<NLWord value: "hello">'
    assert f"{string}" == "hello"
