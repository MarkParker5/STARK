
import pytest

from stark.core import Pattern
from stark.core.patterns.pattern import ParseError
from stark.core.types import Object
from stark.general.classproperty import classproperty


class Lorem(Object):

    @classproperty
    def pattern(cls):
        return Pattern('* ipsum')

    async def did_parse(self, from_string: str) -> str:
        if 'lorem' not in from_string:
            raise ParseError('lorem not found')
        self.value = 'lorem'
        return 'lorem ipsum'

async def test_complex_parsing_failed():
    with pytest.raises(ParseError):
        await Lorem.parse('some lor ipsum')

async def test_complex_parsing():
    string = 'some lorem ipsum'
    match = await Lorem.parse(string)
    assert match
    assert match.obj
    assert match.obj.value == 'lorem'
    assert match.substring == 'lorem ipsum'
    assert (await Lorem.pattern.match(string))[0].substring == 'lorem ipsum'

class Foo(Object):

    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Foo from "{from_string}"')
        if 'foo' not in from_string:
            raise ParseError(f'foo not found in "{from_string}"')
        self.value = 'foo'
        return 'foo'

class Bar(Object):

    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Bar from "{from_string}"')
        if 'bar' not in from_string:
            raise ParseError(f'bar not found in "{from_string}"')
        self.value = 'bar'
        return 'bar'


class Baz(Object):

    @classproperty
    def greedy(cls) -> bool:
        return False

    @classproperty
    def pattern(cls):
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Baz from "{from_string}"')
        if 'baz' not in from_string:
            raise ParseError(f'baz not found in "{from_string}"')
        self.value = 'baz'
        return 'baz'

class Greedy(Object):

    @classproperty
    def greedy(cls) -> bool:
        return True

    @classproperty
    def pattern(cls):
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # print(f'Parsing Greedy from "{from_string}"')
        self.value = from_string
        return from_string

Pattern.add_parameter_type(Foo)
Pattern.add_parameter_type(Bar)
Pattern.add_parameter_type(Baz)
Pattern.add_parameter_type(Greedy)

@pytest.mark.parametrize('string', ['foo bar', 'hey foo bar two']) #, 'hey foo one bar two']) TODO: add support for just enum of param w/o exact pattern structure
async def test_complex_parsing__wildcard_params(string):
    print('Testing:', string)
    pattern = Pattern('$f:Foo $b:Bar')
    matches = await pattern.match(string)
    expected = {'f': 'foo', 'b': 'bar'}
    assert matches
    assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected

@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("foo", {"f": "foo", "b": None, "z": None}),
        ("foo bar", {"f": "foo", "b": "bar", "z": None}),
        ("foo bar baz", {"f": "foo", "b": "bar", "z": "baz"}),
        ("bar baz", {"f": None, "b": "bar", "z": "baz"}),
        ("foo baz", {"f": "foo", "b": None, "z": "baz"}),
    ]
)
async def test_complex_parsing__optional_wildcard(input_string: str, expected: dict[str, str | None]) -> None:
    print('Expected:', input_string, expected)
    pattern = Pattern('$f:Foo? ?$b:Bar? ?$z:Baz?') # TODO: better solution for optional space
    matches = await pattern.match(input_string)
    assert matches
    assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected

@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("one two three", {"g": "one two three", "f": None, "b": None}),
        ("one two foo bar", {"g": "one two", "f": "foo", "b": "bar"}),
    ]
)
async def test_complex_parsing__greedy_and_optional_wildcard(input_string: str, expected: dict[str, str | None]) -> None:
    print('Expected:', input_string, expected)
    matches = await Pattern('$g:Greedy ?$f:Foo? ?$b:Bar?$').match(input_string)
    assert matches
    assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected
