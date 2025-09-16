import itertools

import pytest

from stark.core import Pattern
from stark.core.patterns.rules import all_unordered, one_or_more_unordered
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty


class Seconds(Object):
    value: str
    seconds: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$seconds:Word s')

    async def did_parse(self, from_string: str) -> str:
        self.value = self.seconds.value.split(' ')[0]
        return from_string

class Minutes(Object):
    value: str
    minutes: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$minutes:Word m')

    async def did_parse(self, from_string: str) -> str:
        self.value = self.minutes.value.split(' ')[0]
        return from_string

class Hours(Object):
    value: str
    hours: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$hours:Word h')

    async def did_parse(self, from_string: str) -> str:
        self.value = self.hours.value.split(' ')[0]
        return from_string

Pattern.add_parameter_type(Seconds)
Pattern.add_parameter_type(Minutes)
Pattern.add_parameter_type(Hours)

def permutations(pattern_str, words: str | list[str], match: bool, expected_tokens: dict[str, str] | None = None) -> list[tuple[str, str, bool, dict[str, str]]]:
    expected_tokens = expected_tokens or {}
    if isinstance(words, str):
        words = words.split(' ')
    return [(pattern_str, " ".join(p), match, expected_tokens) for p in itertools.permutations(words)]

@pytest.mark.parametrize(
    'pattern_str,input_str,is_match,expected_tokens',
    [
        # --- Simple unordered patterns ---
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha beta', True),
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha alpha', False),
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha gamma', False),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo bar baz', True),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo bar foo', False),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo baz', False),

        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', 'apple banana cherry', True),
        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', 'banana', True),
        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', '', False),

        # --- Parameter cases ---
        *permutations(f'{all_unordered('$h:Hours','$m:Minutes', '$s:Seconds')}', ['12 h', '30 m', '45 s'], True, {'h': '12', 'm': '30', 's': '45'}),
        *permutations(f'{all_unordered('$h:Hours','$m:Minutes', '$s:Seconds')}', ['12 h', '30 m'], False),
        *permutations(f'{one_or_more_unordered('$h:Hours','$m:Minutes', '$s:Seconds')}', ['12 h', '30 m', '45 s'], True, {'h': '12', 'm': '30', 's': '45'}),
        *permutations(f'{one_or_more_unordered('$h:Hours','$m:Minutes', '$s:Seconds')}', ['12 h', '30 m'], True, {'h': '12', 'm': '30'}),
        *permutations(f'{one_or_more_unordered('$h:Hours','$m:Minutes', '$s:Seconds')}', ['12 h'], True, {'h': '12'}),
    ]
)
@pytest.mark.asyncio
async def test_unordered_patterns(pattern_str, input_str, is_match, expected_tokens):
    print(f'Pattern: "{pattern_str}", Input: "{input_str}", Expected Params: {expected_tokens}')
    p = Pattern(f"{pattern_str}")
    print(f'Compiled: "{p.compiled}"')
    matches = await p.match(input_str)

    if not is_match:
        assert not matches, f'Unexpected match for "{pattern_str}" on "{input_str}"'
        return
    else:
        assert matches, f"No match for {pattern_str} on '{input_str}'"

    print(f'Match: {matches[0].substring}, Got Params: {matches[0].parameters}')

    assert {name: obj.value for name, obj in matches[0].parameters.items() if obj} == expected_tokens
