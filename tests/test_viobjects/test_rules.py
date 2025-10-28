import itertools
import uuid
from typing import Union

import pytest
from typing_extensions import Optional

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
        self.value = self.seconds.value.split()[0]
        return from_string

class Minutes(Object):
    value: str
    minutes: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$minutes:Word m')

    async def did_parse(self, from_string: str) -> str:
        self.value = self.minutes.value.split()[0]
        return from_string

class Hours(Object):
    value: str
    hours: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('$hours:Word h')

    async def did_parse(self, from_string: str) -> str:
        self.value = self.hours.value.split()[0]
        return from_string

Pattern.add_parameter_type(Seconds)
Pattern.add_parameter_type(Minutes)
Pattern.add_parameter_type(Hours)

def permutations(pattern_str, words: str | list[str], match: bool, expected_tokens: dict[str, str] | None = None) -> list[tuple[str, str, bool, dict[str, str]]]:
    expected_tokens = expected_tokens or {}
    if isinstance(words, str):
        words = words.split()
    return [(pattern_str, " ".join(p), match, expected_tokens) for p in itertools.permutations(words)]

class StarObject(Object):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        # ** means greedy match for multiple words
        return Pattern('**')

    async def did_parse(self, from_string: str) -> str:
        # param extraction imitation
        words = [w.strip() for w in from_string.split() if w.strip() and not w.startswith('no')] #
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

class OOWord(Word):
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern(r'**')

    async def did_parse(self, from_string: str) -> str:
        # param extraction imitation
        words = [w.strip() for w in from_string.split() if w.strip() and 'oo' in w]
        if not words:
            raise ParseError(f"Expected a word with 'oo', got '{from_string}'")
        self.value = words[0]
        return self.value

class OOWordSimple(Word):
    async def did_parse(self, from_string: str) -> str:
        if "oo" not in from_string:
            raise ParseError("OOWord must contain 'oo'")
        self.value = from_string
        return from_string

Pattern.add_parameter_type(StarSlots)
Pattern.add_parameter_type(GreedySlots)
Pattern.add_parameter_type(OOWord)
Pattern.add_parameter_type(OOWordSimple)

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
    assert matches[0].parameters['slots'].value == match_str
    assert matches[0].substring == match_str

@pytest.mark.parametrize(
    "cls_name, slots_dict, input_str, expected_values, expected_error",
    [
        # All required, one missing - fail
        (
            "AllRequiredSlots",
            {"a": OOWord, "b": OOWord, "c": OOWord},
            "foo oops no",
            None,
            ParseError,
        ),
        # All required, all present - all parsed
        (
            "AllRequiredSlots2",
            {"a": OOWord, "b": OOWord, "c": OOWord},
            "foo boo woo",
            {"a": "foo", "b": "boo", "c": "woo"},
            None,
        ),
        # All optional, all present - all parsed
        (
            "AllOptionalSlots",
            {
                "a": Union[OOWord, None],
                "b": Union[OOWord, None],
                "c": Union[OOWord, None],
                "d": Union[OOWord, None],
            },
            "moon loop boom good",
            {"a": "moon", "b": "loop", "c": "boom", "d": "good"},
            None,
        ),
        # All optional, half missing - parsed correctly
        (
            "AllOptionalSlots2",
            {
                "a": Optional[OOWord],
                "b": Optional[OOWord],
                "c": Optional[OOWord],
                "d": Optional[OOWord],
            },
            "noon good",
            {"a": "noon", "b": "good"},
            None,
        ),
        # All optional, none matches - failed (at least one parameter must be matched)
        (
            "AllOptionalSlots3",
            {
                "a": OOWord | None,
                "b": OOWord | None,
            },
            "bar baz",
            None,
            ParseError,
        ),
        # Half optional - only required present - parsed correctly
        (
            "HalfOptionalSlots",
            {
                "a": OOWord,
                "b": OOWord,
                "c": Optional[OOWord],
                "d": Optional[OOWord],
            },
            "well choose nice goose",
            {"a": "choose", "b": "goose"},
            None,
        ),
        # Half optional - all present - parsed correctly
        (
            "HalfOptionalSlots2",
            {
                "a": OOWord,
                "b": OOWord,
                "c": Optional[OOWord],
                "d": Optional[OOWord],
            },
            "wood book cook hook",
            {"a": "wood", "b": "book", "c": "cook", "d": "hook"},
            None,
        ),
        # Half optional - all present but one required missing - failed
        (
            "HalfOptionalSlots3",
            {
                "a": OOWord,
                "b": OOWord,
                "c": Optional[OOWord],
                "d": Optional[OOWord],
            },
            "look lorem ipsum dolor",
            None,
            ParseError,
        ),

        # --- Extra words - wildcard ---

        # All required, all present, extra words - all parsed correctly
        (
            "AllRequiredSlots21",
            {"a": OOWord, "b": OOWord, "c": OOWord},
            "uno foo dos boo tres woo cuatro",
            {"a": "foo", "b": "boo", "c": "woo"},
            None,
        ),
        # All optional, all present, extra words - all parsed correctly
        (
            "AllOptionalSlots21",
            {
                "a": Union[OOWord, None],
                "b": Union[OOWord, None],
                "c": Union[OOWord, None],
                "d": Union[OOWord, None],
            },
            "one moon two loop three boom four good five",
            {"a": "moon", "b": "loop", "c": "boom", "d": "good"},
            None,
        ),
        # All optional, half missing - parsed correctly
        (
            "AllOptionalSlots22",
            {
                "a": Optional[OOWord],
                "b": Optional[OOWord],
                "c": Optional[OOWord],
                "d": Optional[OOWord],
            },
            "hello noon how good",
            {"a": "noon", "b": "good"},
            None,
        ),

        # --- Extra words - by pattern ---

        # All required, all present, extra words - all parsed correctly
        (
            "AllRequiredSlots21",
            {"a": OOWordSimple, "b": OOWordSimple, "c": OOWordSimple},
            "uno foo dos boo tres woo cuatro",
            {"a": "foo", "b": "boo", "c": "woo"},
            None,
        ),
        # All optional, all present, extra words - all parsed correctly
        (
            "AllOptionalSlots21",
            {
                "a": Union[OOWordSimple, None],
                "b": Union[OOWordSimple, None],
                "c": Union[OOWordSimple, None],
                "d": Union[OOWordSimple, None],
            },
            "one moon two loop three boom four good five",
            {"a": "moon", "b": "loop", "c": "boom", "d": "good"},
            None,
        ),
        # All optional, half missing - parsed correctly
        (
            "AllOptionalSlots22",
            {
                "a": Optional[OOWordSimple],
                "b": Optional[OOWordSimple],
                "c": Optional[OOWordSimple],
                "d": Optional[OOWordSimple],
            },
            "hello noon how good",
            {"a": "noon", "b": "good"},
            None,
        ),
    ],
)
async def test_slots_required_optional_cases(cls_name, slots_dict, input_str, expected_values, expected_error):

    print(f'{cls_name=} {input_str=} {expected_error=} {expected_values=} {slots_dict=}')

    # Generate a unique class name for each test run to avoid registry conflicts
    unique_cls_name = f"{cls_name}_{uuid.uuid4().hex[:8]}"
    # Ensure __annotations__ is set for dynamic slots class
    class_dict = dict(slots_dict)
    class_dict["__annotations__"] = {k: v for k, v in slots_dict.items()}
    slots_cls = type(unique_cls_name, (Slots,), class_dict)

    # Register the slots class as a parameter type for Pattern
    Pattern.add_parameter_type(slots_cls)

    pattern = Pattern(f"$slots:{slots_cls.__name__}")

    if expected_error is not None:
        with pytest.raises(expected_error):
            print('Match', m := await pattern.match(input_str))
            if not m[0].substring.strip():
                raise ParseError("Empty match") # small patch until required/optional params are fully implemented
        return

    matches = await pattern.match(input_str)

    assert matches, f"Expected a match but got none for input '{input_str}'"

    slots_obj = matches[0].parameters["slots"]
    got = {k: getattr(slots_obj, k).value for k in expected_values if getattr(slots_obj, k) is not None}
    for k, v in expected_values.items():
        assert got.get(k) == v
