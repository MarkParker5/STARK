import pytest

from stark.core import Pattern
from stark.core.patterns import rules

word = rf"[{rules.alphanumerics}]*"
words = rf"[{rules.alphanumerics}\s]+"
words_optional = rf"[{rules.alphanumerics}\s]*"

from stark.core.parsing import PatternParser

pattern_parser = PatternParser()


async def test_leading_star():
    p = Pattern("*text")
    assert pattern_parser._compile_pattern(p) == rf"{word}text"
    assert await pattern_parser.match(p, "text")
    assert await pattern_parser.match(p, "aaatext")
    assert (await pattern_parser.match(p, "bbb aaaatext cccc"))[0].substring == "aaaatext"
    assert not await pattern_parser.match(p, "aaaaext")

    p = Pattern("Some *text here")
    assert pattern_parser._compile_pattern(p) == rf"Some {word}text here"
    assert await pattern_parser.match(p, "Some text here")
    assert await pattern_parser.match(p, "Some aaatext here")
    assert (await pattern_parser.match(p, "bbb Some aaatext here cccc"))[0].substring == "Some aaatext here"
    assert not await pattern_parser.match(p, "aaatext here")


async def test_trailing_star():
    p = Pattern("text*")
    assert pattern_parser._compile_pattern(p) == rf"text{word}"
    assert await pattern_parser.match(p, "text")
    assert await pattern_parser.match(p, "textaaa")
    assert (await pattern_parser.match(p, "bbb textaaa cccc"))[0].substring == "textaaa"

    p = Pattern("Some text* here")
    assert pattern_parser._compile_pattern(p) == rf"Some text{word} here"
    assert await pattern_parser.match(p, "Some text here")
    assert await pattern_parser.match(p, "Some textaaa here")
    assert (await pattern_parser.match(p, "bbb Some textaaa here cccc"))[0].substring == "Some textaaa here"
    assert not await pattern_parser.match(p, "Some textaaa ")


async def test_middle_star():
    p = Pattern("te*xt")
    assert pattern_parser._compile_pattern(p) == rf"te{word}xt"
    assert await pattern_parser.match(p, "text")
    assert await pattern_parser.match(p, "teaaaaaxt")
    assert (await pattern_parser.match(p, "bbb teaaaaaxt cccc"))[0].substring == "teaaaaaxt"

    p = Pattern("Some te*xt here")
    assert pattern_parser._compile_pattern(p) == rf"Some te{word}xt here"
    assert await pattern_parser.match(p, "Some text here")
    assert await pattern_parser.match(p, "Some teaaaaaxt here")
    assert (await pattern_parser.match(p, "bbb Some teaaeaaaxt here cccc"))[0].substring == "Some teaaeaaaxt here"
    assert not await pattern_parser.match(p, "Some teaaaaaxt")


async def test_single_star():
    p = Pattern("Some * here")
    assert pattern_parser._compile_pattern(p) == rf"Some {word} here"
    assert (await pattern_parser.match(p, "bbb Some teaaeaaaxt here cccc"))[0].substring == "Some teaaeaaaxt here"
    assert await pattern_parser.match(p, "Some  here")  # note double space

    p = Pattern("Some *")
    assert pattern_parser._compile_pattern(p) == rf"Some {word}"
    assert (await pattern_parser.match(p, "bbb Some teaaeaaaxt here cccc"))[0].substring == "Some teaaeaaaxt"
    assert await pattern_parser.match(p, "Some ")  # note space

    p = Pattern("* some")
    assert pattern_parser._compile_pattern(p) == rf"{word} some"
    assert (await pattern_parser.match(p, "bbb teaaeaaaxt some cccc"))[0].substring == "teaaeaaaxt some"
    assert await pattern_parser.match(p, " some")  # note space

    p = Pattern("*")
    assert pattern_parser._compile_pattern(p) == rf"{word}"
    # assert (await pattern_parser.match(p, 'bbb teaaeaaaxt some cccc'))[0].substring == 'bbb' # takes the first word
    assert (await pattern_parser.match(p, "bbb teaaeaaaxt some cccc"))[0].substring == "teaaeaaaxt"  # takes the largest word, TODO: review behavior
    assert not await pattern_parser.match(p, "")
    assert not await pattern_parser.match(p, " ")
    assert len(await pattern_parser.match(p, "a b c d")) == 4, await pattern_parser.match(p, "a b c d")


async def test_double_star():
    p = Pattern("**")
    assert pattern_parser._compile_pattern(p) == rf"{words}"
    assert (await pattern_parser.match(p, "bbb teaaaaaxt cccc"))[0].substring == "bbb teaaaaaxt cccc"

    p = Pattern("Some ** here")
    assert pattern_parser._compile_pattern(p) == rf"Some {words} here"
    assert await pattern_parser.match(p, "Some text here")
    assert await pattern_parser.match(p, "Some lorem ipsum dolor here")
    assert (await pattern_parser.match(p, "bbb Some lorem ipsum dolor here cccc"))[0].substring == "Some lorem ipsum dolor here"
    assert not await pattern_parser.match(p, "some here")


async def test_optional_double_star():
    p = Pattern("**?")
    assert pattern_parser._compile_pattern(p) == rf"{words_optional}"
    assert (await pattern_parser.match(p, "bbb teaaaaaxt cccc"))[0].substring == "bbb teaaaaaxt cccc"

    p = Pattern("Some **?here")
    assert pattern_parser._compile_pattern(p) == rf"Some {words_optional}here"
    assert await pattern_parser.match(p, "Some text here")
    assert await pattern_parser.match(p, "Some lorem ipsum dolor here")
    assert (await pattern_parser.match(p, "bbb Some lorem ipsum dolor here cccc"))[0].substring == "Some lorem ipsum dolor here"
    assert await pattern_parser.match(p, "Some here")  # The only difference from double star


async def test_one_of():
    p = Pattern("(foo|bar)")
    assert pattern_parser._compile_pattern(p) == r"(?:foo|bar)"
    assert await pattern_parser.match(p, "foo")
    assert await pattern_parser.match(p, "bar")
    assert (await pattern_parser.match(p, "bbb foo cccc"))[0].substring == "foo"
    assert (await pattern_parser.match(p, "bbb bar cccc"))[0].substring == "bar"

    p = Pattern("Some (foo|bar) here")
    assert pattern_parser._compile_pattern(p) == r"Some (?:foo|bar) here"
    assert await pattern_parser.match(p, "Some foo here")
    assert await pattern_parser.match(p, "Some bar here")
    assert (await pattern_parser.match(p, "bbb Some foo here cccc"))[0].substring == "Some foo here"
    assert (await pattern_parser.match(p, "bbb Some bar here cccc"))[0].substring == "Some bar here"
    assert not await pattern_parser.match(p, "Some foo")


@pytest.mark.skip(reason="Not implemented as a not important feature")
async def test_one_of_with_spaces():
    p = Pattern("Hello ( foo | bar | baz ) world")
    print(pattern_parser._compile_pattern(p))
    assert await pattern_parser.match(p, "Hello foo world")
    assert await pattern_parser.match(p, "Hello bar world")
    assert await pattern_parser.match(p, "Hello baz world")


async def test_optional_one_of():
    p = Pattern("(foo|bar)?")
    assert pattern_parser._compile_pattern(p) == r"(?:foo|bar)?"
    assert await pattern_parser.match(p, "foo")
    assert await pattern_parser.match(p, "bar")
    assert not await pattern_parser.match(p, "")
    assert not await pattern_parser.match(p, "bbb cccc")
    assert (await pattern_parser.match(p, "bbb foo cccc"))[0].substring == "foo"
    assert (await pattern_parser.match(p, "bbb bar cccc"))[0].substring == "bar"

    p = Pattern("Some (foo|bar)? here")
    assert pattern_parser._compile_pattern(p) == r"Some (?:foo|bar)? here"
    assert await pattern_parser.match(p, "Some foo here")
    assert await pattern_parser.match(p, "Some bar here")
    assert await pattern_parser.match(p, "Some  here")
    assert (await pattern_parser.match(p, "bbb Some foo here cccc"))[0].substring == "Some foo here"
    assert (await pattern_parser.match(p, "bbb Some bar here cccc"))[0].substring == "Some bar here"
    assert (await pattern_parser.match(p, "bbb Some  here cccc"))[0].substring == "Some  here"

    # assert Pattern('[foo|bar]').compiled == Pattern('(foo|bar)?').compiled


async def test_one_or_more_of():
    p = Pattern("{foo|bar}")
    assert pattern_parser._compile_pattern(p) == r"(?:(?:foo|bar)\s?)+"
    assert await pattern_parser.match(p, "foo")
    assert await pattern_parser.match(p, "bar")
    assert not await pattern_parser.match(p, "")
    assert (await pattern_parser.match(p, "bbb foo cccc"))[0].substring == "foo"
    assert (await pattern_parser.match(p, "bbb bar cccc"))[0].substring == "bar"
    assert (await pattern_parser.match(p, "bbb foo bar cccc"))[0].substring == "foo bar"
    assert not await pattern_parser.match(p, "bbb cccc")

    p = Pattern("Some {foo|bar} here")
    assert pattern_parser._compile_pattern(p) == r"Some (?:(?:foo|bar)\s?)+ here"
    assert await pattern_parser.match(p, "Some foo here")
    assert await pattern_parser.match(p, "Some bar here")
    assert not await pattern_parser.match(p, "Some  here")
    assert (await pattern_parser.match(p, "bbb Some foo here cccc"))[0].substring == "Some foo here"
    assert (await pattern_parser.match(p, "bbb Some bar here cccc"))[0].substring == "Some bar here"
    assert (await pattern_parser.match(p, "bbb Some foo bar here cccc"))[0].substring == "Some foo bar here"
    assert not await pattern_parser.match(p, "Some foo")


async def test_none_or_more_of():
    p = Pattern("one {foo|bar}?two")
    assert pattern_parser._compile_pattern(p) == r"one (?:(?:foo|bar)\s?)*two"
    assert await pattern_parser.match(p, "one two")
    assert await pattern_parser.match(p, "one foo two")
    assert await pattern_parser.match(p, "one bar two")
    assert await pattern_parser.match(p, "one foo bar two")
    assert not await pattern_parser.match(p, "one foo bar baz two")
    assert (await pattern_parser.match(p, "bbb one two cccc"))[0].substring == "one two"
    assert (await pattern_parser.match(p, "bbb one foo two cccc"))[0].substring == "one foo two"
    assert (await pattern_parser.match(p, "bbb one bar two cccc"))[0].substring == "one bar two"
    assert (await pattern_parser.match(p, "bbb one foo bar two cccc"))[0].substring == "one foo bar two"
