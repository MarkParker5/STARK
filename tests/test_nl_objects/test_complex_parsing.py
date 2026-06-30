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
            assert from_string == "timing"
            return from_string[:-3]

    class CustomObject(Object):
        @classproperty
        def pattern(cls):
            return Pattern("**")

        async def did_parse(self, from_string):
            call_order.append("object")
            assert from_string == "tim"
            return from_string[:-1]

    parser = PatternParser()
    parser.register_parameter_type(CustomObject, CustomParser())
    result = await parser.parse_object(CustomObject, "timing")
    assert call_order == ["parser", "object"]
    assert result.substring == "ti"


class Size(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Size from "{from_string}"')
        if "small" not in from_string:
            raise ParseError(f'small not found in "{from_string}"')
        self.value = "small"
        return "small"


class Drink(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Drink from "{from_string}"')
        if "latte" not in from_string:
            raise ParseError(f'latte not found in "{from_string}"')
        self.value = "latte"
        return "latte"


class Extra(Object):
    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Extra from "{from_string}"')
        if "sugar" not in from_string:
            raise ParseError(f'sugar not found in "{from_string}"')
        self.value = "sugar"
        return "sugar"


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
pattern_parser.register_parameter_type(Size)
pattern_parser.register_parameter_type(Drink)
pattern_parser.register_parameter_type(Extra)
pattern_parser.register_parameter_type(Greedy)


@pytest.mark.parametrize(
    "pattern_string,input_string,expected_params",
    [
        # wildcard regex params
        ("$s:Size $d:Drink", "small latte", {"s": "small", "d": "latte"}),
        ("$s:Size $d:Drink", "hey small latte two", {"s": "small", "d": "latte"}),
        # , 'hey small one latte two' TODO: add support for just enum of param w/o exact pattern structure
        # optional params with wildcard regex
        ("$s:Size? ?$d:Drink? ?$e:Extra?", "small", {"s": "small", "d": None, "e": None}),
        ("$s:Size? ?$d:Drink? ?$e:Extra?", "small latte", {"s": "small", "d": "latte", "e": None}),
        (
            "$s:Size? ?$d:Drink? ?$e:Extra?",
            "small latte sugar",
            {"s": "small", "d": "latte", "e": "sugar"},
        ),
        ("$s:Size? ?$d:Drink? ?$e:Extra?", "latte sugar", {"s": None, "d": "latte", "e": "sugar"}),
        ("$s:Size? ?$d:Drink? ?$e:Extra?", "small sugar", {"s": "small", "d": None, "e": "sugar"}),
        # greedy and trailing anchor
        (
            "order $g:Greedy end",
            "order a few words of options end",
            {"g": "a few words of options"},
        ),
        (
            "order $g:Greedy",
            "order a few words of options",
            {"g": "a few words of options"},
        ),
        # greedy with other params
        (
            "order $g:Greedy $s:Size",
            "order a few words of options small",
            {"g": "a few words of options", "s": "small"},
        ),
        (
            "order $g:Greedy $ag:Greedy",
            "order a few words of options another options words",
            {"g": "a", "ag": "few words of options another options words"},
        ),  # TODO: review
        # greedy with optional params, note optional spaces
        (
            "$g:Greedy ?$s:Size? ?$d:Drink?$",
            "one two three",
            {"g": "one two three", "s": None, "d": None},
        ),
        (
            "$g:Greedy ?$s:Size? ?$d:Drink?$",
            "one two small latte",
            {"g": "one two", "s": "small", "d": "latte"},
        ),
    ],
)
async def test_complex_parsing__parametrized(
    pattern_string: str, input_string: str, expected_params: dict[str, str | None]
):
    pattern = Pattern(pattern_string)
    matches = await pattern_parser.match(pattern, input_string)
    print(
        f'Pattern: {pattern_string} "{pattern_parser._compile_pattern(pattern)}", Input: {input_string}, Expected Params: {expected_params}'
    )
    assert matches
    print(f"Match: {matches[0].substring}, Got Params: {matches[0].parameters}")
    assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected_params
