import itertools

import pytest

from stark.core import Pattern
from stark.core.patterns.parsing import ParseError
from stark.core.patterns.rules import all_unordered, one_or_more_unordered
from stark.core.types import Object, Slots, Word
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

class StarObject(Object):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        # ** means greedy match for multiple words
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # param extraction imitation
        words = [w.strip() for w in from_string.split(' ') if w.strip() and not w.startswith('no')] #
        assert len(words) >= 2, ParseError(f"Expected at least two words without 'no' prefix, got '{from_string}'")
        self.value = " ".join(words[:2])
        # print(type(self), 'did_parse', self.value, words)
        return self.value

class GreedyObject(StarObject):
    @classproperty
    def greedy(cls) -> bool:
        return True

Pattern.add_parameter_type(StarObject)
Pattern.add_parameter_type(GreedyObject)

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

        # --- Check unordered doesn't affect wildcard and greedy ---
        (f"{all_unordered('$a:StarObject $b:StarObject $c:StarObject')}","one foo two bar three baz", True, {'a': 'one foo', 'b': 'two', 'c': 'bar three baz'}),
        (f"{all_unordered('$a:GreedyObject $b:GreedyObject $c:GreedyObject')}","one foo two bar three baz", True, {'a': 'one foo', 'b': 'two', 'c': 'bar three baz'}),
    ]
)
async def test_unordered_patterns(pattern_str, input_str, is_match, expected_tokens):

    if 'StarObject' in pattern_str or 'GreedyObject' in pattern_str:
        pytest.skip(reason='Wildcard (star) and greedy objects do not work correctly with unordered patterns. Use Slots instead')

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


class StarSlots(Slots):
    a: StarObject
    b: StarObject
    c: StarObject

class GreedySlots(Slots):
    a: GreedyObject
    b: GreedyObject
    c: GreedyObject

Pattern.add_parameter_type(StarSlots)
Pattern.add_parameter_type(GreedySlots)

@pytest.mark.parametrize('pattern_str, input_str, is_match, match_str, expected_tokens', [
        ("$slots:StarSlots","one foo two bar three baz", True, 'one foo two bar three baz', {'a': 'one foo', 'b': 'two bar', 'c': 'three baz'}),
        ("$slots:GreedySlots","one foo two bar three baz", True, 'one foo two bar three baz', {'a': 'one foo', 'b': 'two bar', 'c': 'three baz'}),
        ("$slots:StarSlots","noabc one foo two bar three baz noend", True, 'one foo two bar three baz', {'a': 'one foo', 'b': 'two bar', 'c': 'three baz'}),
        ("$slots:GreedySlots","nostart one foo two bar three baz noend", True, 'one foo two bar three baz', {'a': 'one foo', 'b': 'two bar', 'c': 'three baz'}),
    ]
)
async def test_slots(pattern_str, input_str, is_match, match_str, expected_tokens):
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

    got_values = {key: getattr(matches[0].parameters['slots'], key).value for key in expected_tokens.keys()}
    assert got_values == expected_tokens
    # assert matches[0].parameters['slots'].substring == match_str
