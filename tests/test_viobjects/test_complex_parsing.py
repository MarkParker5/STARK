import pytest

from stark.core import Pattern
from stark.core.parsing import ObjectParser, ParseError, PatternParser
from stark.core.types import Object
from stark.general.classproperty import classproperty


class Lorem(Object):
    @classproperty
    def pattern(cls):
        return Pattern("* ipsum")

    async def did_parse(self, from_string: str) -> str:
        if "lorem" not in from_string:
            raise ParseError("lorem not found")
        self.value = "lorem"
        return "lorem ipsum"


async def test_complex_parsing_failed():
    parser = PatternParser()
    parser.register_parameter_type(Lorem)
    with pytest.raises(ParseError):
        await parser.parse_object(Lorem, "some lor ipsum")


async def test_complex_parsing():
    parser = PatternParser()
    parser.register_parameter_type(Lorem)
    string = "some lorem ipsum"
    match = await parser.parse_object(Lorem, string)
    assert match
    assert match.obj
    assert match.obj.value == "lorem"
    assert match.substring == "lorem ipsum"
    assert (await parser.match(Lorem.pattern, string))[0].substring == "lorem ipsum"


async def test_did_parse_call_order():
    call_order = []

    class CustomParser(ObjectParser):
        async def did_parse(self, obj, from_string):
            call_order.append("parser")
            assert from_string == "foobar"
            return from_string[:-3]

    class CustomObject(Object):
        @classproperty
        def pattern(cls):
            return Pattern("**")

        async def did_parse(self, from_string):
            call_order.append("object")
            assert from_string == "foo"
            return from_string[:-1]

    parser = PatternParser()
    parser.register_parameter_type(CustomObject)
    result = await parser.parse_object(CustomObject, "foobar")
    assert call_order == ["parser", "object"]
    assert result.substring == "fo"


class Foo(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Foo from "{from_string}"')
        if "foo" not in from_string:
            raise ParseError(f'foo not found in "{from_string}"')
        self.value = "foo"
        return "foo"


class Bar(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Bar from "{from_string}"')
        if "bar" not in from_string:
            raise ParseError(f'bar not found in "{from_string}"')
        self.value = "bar"
        return "bar"


class Baz(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Baz from "{from_string}"')
        if "baz" not in from_string:
            raise ParseError(f'baz not found in "{from_string}"')
        self.value = "baz"
        return "baz"


class Greedy(Object):
    @classproperty
    def greedy(cls) -> bool:
        return True

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Greedy from "{from_string}"')
        self.value = from_string
        return from_string


pattern_parser = PatternParser()
pattern_parser.register_parameter_type(Foo)
pattern_parser.register_parameter_type(Bar)
pattern_parser.register_parameter_type(Baz)
pattern_parser.register_parameter_type(Greedy)


@pytest.mark.parametrize(
    "pattern_string,input_string,expected_params",
    [
        # wildcard regex params
        ("$f:Foo $b:Bar", "foo bar", {"f": "foo", "b": "bar"}),
        ("$f:Foo $b:Bar", "hey foo bar two", {"f": "foo", "b": "bar"}),
        # , 'hey foo one bar two' TODO: add support for just enum of param w/o exact pattern structure
        # optional params with wildcard regex
        ("$f:Foo? ?$b:Bar? ?$z:Baz?", "foo", {"f": "foo", "b": None, "z": None}),
        ("$f:Foo? ?$b:Bar? ?$z:Baz?", "foo bar", {"f": "foo", "b": "bar", "z": None}),
        (
            "$f:Foo? ?$b:Bar? ?$z:Baz?",
            "foo bar baz",
            {"f": "foo", "b": "bar", "z": "baz"},
        ),
        ("$f:Foo? ?$b:Bar? ?$z:Baz?", "bar baz", {"f": None, "b": "bar", "z": "baz"}),
        ("$f:Foo? ?$b:Bar? ?$z:Baz?", "foo baz", {"f": "foo", "b": None, "z": "baz"}),
        # greedy and trailing anchor
        (
            "command1 $g:Greedy end",
            "command1 a few words of greedy end",
            {"g": "a few words of greedy"},
        ),
        (
            "command1 $g:Greedy",
            "command1 a few words of greedy",
            {"g": "a few words of greedy"},
        ),
        # greedy with other params
        (
            "command1 $g:Greedy $f:Foo",
            "command1 a few words of greedy foo",
            {"g": "a few words of greedy", "f": "foo"},
        ),
        (
            "command1 $g:Greedy $ag:Greedy",
            "command1 a few words of greedy another greedy words",
            {"g": "a", "ag": "few words of greedy another greedy words"},
        ),  # TODO: review
        # greedy with optional params, note optional spaces
        (
            "$g:Greedy ?$f:Foo? ?$b:Bar?$",
            "one two three",
            {"g": "one two three", "f": None, "b": None},
        ),
        (
            "$g:Greedy ?$f:Foo? ?$b:Bar?$",
            "one two foo bar",
            {"g": "one two", "f": "foo", "b": "bar"},
        ),
    ],
)
async def test_complex_parsing__parametrized(pattern_string: str, input_string: str, expected_params: dict[str, str | None]):
    pattern = Pattern(pattern_string)
    matches = await pattern_parser.match(pattern, input_string)
    print(f'Pattern: {pattern_string} "{pattern_parser._compile_pattern(pattern)}", Input: {input_string}, Expected Params: {expected_params}')
    assert matches
    print(f"Match: {matches[0].substring}, Got Params: {matches[0].parameters}")
    assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected_params
