import itertools

import pytest

from stark.core import Pattern
from stark.core.patterns.rules import all_unordered, one_or_more_unordered
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty


class FullName(Object):
    first: Word
    second: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$first:Word $second:Word')

Pattern.add_parameter_type(FullName)

def permutations(pattern_str, words_space_separated: str, expected_tokens: set[str]) -> list[tuple[str, str, set[str]]]:
    return [(pattern_str, " ".join(p), expected_tokens) for p in itertools.permutations(words_space_separated.split(' '))]

@pytest.mark.asyncio
@pytest.mark.parametrize(
    'pattern_str,input_str,expected_tokens',
    [
        # --- Simple unordered patterns ---
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha beta', {'alpha', 'beta'}),
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha alpha', set()),
        *permutations(f'{all_unordered('alpha','beta')}', 'alpha gamma', set()),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo bar baz', {'foo', 'bar', 'baz'}),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo bar foo', set()),
        *permutations(f'{all_unordered('foo','bar','baz')}', 'foo baz', set()),

        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', 'apple banana cherry', {'apple', 'banana', 'cherry'}),
        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', 'banana', {'banana',}),
        *permutations(f'{one_or_more_unordered('apple','banana','cherry')}', '', set()),

        # --- Parameter cases ---
        # *permutations(f'{all_unordered('$f:FullName','$s:FullName')}', 'John Galt Alice Cooper', {'John','Galt','Alice','Cooper'}),
        # *permutations(f'{one_or_more_unordered('$f:FullName','$s:FullName','$t:FullName')}', 'John Galt Alice Cooper Bob Marley', {'John','Galt','Alice','Cooper', 'Bob', 'Marley'}),
    ]
)
async def test_unordered_patterns(pattern_str, input_str, expected_tokens):
    print(f'Pattern: "{pattern_str}", Input: "{input_str}", Expected Params: {expected_tokens}')
    p = Pattern(f"{pattern_str}")
    print(f'Compiled: "{p.compiled}"')
    matches = await p.match(input_str)

    if not expected_tokens:
        assert not matches, f'Unexpected match for "{pattern_str}" on "{input_str}"'
        return
    else:
        assert matches, f"No match for {pattern_str} on '{input_str}'"

    print(f'Match: {matches[0].substring}, Got Params: {matches[0].parameters}')

    # assert {name: obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected_tokens
    assert {obj.value if obj else None for name, obj in matches[0].parameters.items()} == expected_tokens
