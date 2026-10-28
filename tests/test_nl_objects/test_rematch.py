"""
Results of the parameter re-match loop on edge cases.

Each parsed parameter's claim replaces its group in the pattern, and the pattern is re-matched.
Text that the claim leaves out must be taken by a pattern literal or by another parameter;
otherwise the claim does not fit at that position.
"""

import pytest

from stark.core import Pattern
from stark.core.parsing import ParseError, PatternParser
from stark.core.types import NLObject
from stark.general.classproperty import classproperty
from stark.general.feature_flags import FeatureFlag
from stark.general.localisation import LocaleString

NUMBERS = {"первого": 1, "пятого": 5, "один": 1, "два": 2, "пять": 5, "тринадцать": 13, "тридцать": 30}
MONTHS = {"января": 1, "сентября": 9}


class RmNumber(NLObject):
    # like a real number parser behind a `**` pattern: claims only the words it needs
    value: int

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    async def did_parse(self, from_string: LocaleString) -> str:
        for word in from_string.split():
            if word in NUMBERS:
                self.value = NUMBERS[word]
                return word
        raise ParseError(f"no number in '{from_string}'")


class RmGreedyNumber(RmNumber):
    @classproperty
    def greedy(cls) -> bool:
        return True


class RmGreedyText(NLObject):
    value: str

    @classproperty
    def greedy(cls) -> bool:
        return True

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    async def did_parse(self, from_string: LocaleString) -> str:
        self.value = str(from_string)
        return from_string


class RmDay(NLObject):
    value: int
    n: RmNumber

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$n:RmNumber( числ*)?")

    async def did_parse(self, from_string: LocaleString) -> str:
        if self.n is None:
            raise ParseError("no day")
        self.value = self.n.value
        return from_string


class RmMonth(NLObject):
    value: int

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(января|сентября)")

    async def did_parse(self, from_string: LocaleString) -> str:
        self.value = MONTHS[str(from_string)]
        return from_string


class RmYear(NLObject):
    value: int
    a: RmNumber
    b: RmNumber | None = None

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$a:RmNumber( $b:RmNumber)?")

    async def did_parse(self, from_string: LocaleString) -> str:
        if self.a is None:
            raise ParseError("no year")
        self.value = self.a.value * 100 + self.b.value if self.b else self.a.value
        return from_string


class RmDate(NLObject):
    value: tuple[int, int | None, int | None]
    day: RmDay
    month: RmMonth | None = None
    year: RmYear | None = None

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$day:RmDay( $month:RmMonth( $year:RmYear)?)?")

    async def did_parse(self, from_string: LocaleString) -> str:
        if self.day is None:
            raise ParseError("no day")
        self.value = (self.day.value, self.month and self.month.value, self.year and self.year.value)
        return from_string


class RmFlaggedDate(NLObject):
    value: tuple[int, int | None]
    day: RmDay
    month: RmMonth | None = None

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$day:RmDay( $month:RmMonth?)")

    async def did_parse(self, from_string: LocaleString) -> str:
        self.value = (self.day.value, self.month and self.month.value)
        return from_string


class RmLanguage(NLObject):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(c\\+\\+|python)")

    async def did_parse(self, from_string: LocaleString) -> str:
        self.value = str(from_string)
        return from_string


parser = PatternParser()
for _type in (RmDate, RmFlaggedDate, RmLanguage, RmGreedyNumber, RmGreedyText):
    parser.register_parameter_type(_type)


def values(parameters: dict[str, NLObject | None]) -> dict[str, object]:
    return {name: obj.value if obj is not None else None for name, obj in parameters.items()}


@pytest.fixture(autouse=True)
def stable_rematch(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(FeatureFlag.STABLE_REMATCH, "1")


@pytest.fixture(params=["0", "1"], ids=["flag off", "flag on"])
def either_mode(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(FeatureFlag.STABLE_REMATCH, request.param)


# Edge cases: fail without the STABLE_REMATCH flag


async def test_partial_claim_stays_placed_when_nothing_takes_the_cut():
    # year's group captured `в тринадцать тридцать` but claims only `тринадцать тридцать`; no slot takes `в`
    result = await parser.parse_object(RmDate, "пятого сентября в тринадцать тридцать")
    assert result.substring == "пятого сентября в тринадцать тридцать"
    assert result.obj.value == (5, 9, 1330)


async def test_partial_claim_of_required_param_keeps_match():
    matches = await parser.match(Pattern("$day:RmDay $month:RmMonth"), "пятого blah сентября")
    assert matches[0].substring == "пятого blah сентября"
    assert values(matches[0].parameters) == {"day": 5, "month": 9}


@pytest.mark.xfail(strict=True, reason="out of scope: a failed parameter is prefilled with an empty group that matches anywhere")
async def test_failed_required_param_rejects_match():
    matches = await parser.match(Pattern("$day:RmDay $month:RmMonth"), "blah сентября")
    assert matches == []


async def test_claim_with_regex_special_characters():
    matches = await parser.match(Pattern("пиши на $lang:RmLanguage"), "пиши на c++")
    assert matches[0].substring == "пиши на c++"
    assert values(matches[0].parameters) == {"lang": "c++"}


@pytest.mark.xfail(strict=True, reason="out of scope: a lazy greedy group with nothing after it captures one character")
async def test_greedy_param_at_end_of_optional_tail():
    matches = await parser.match(Pattern("$day:RmDay( $g:RmGreedyNumber)?"), "пятого тринадцать")
    assert matches[0].substring == "пятого тринадцать"
    assert values(matches[0].parameters) == {"day": 5, "g": 13}


@pytest.mark.xfail(strict=True, reason="out of scope: the required-parameters assert in parse_objects is inverted")
async def test_optional_flag_param_in_type_pattern():
    result = await parser.parse_object(RmFlaggedDate, "пятого сентября")
    assert result.obj.value == (5, 9)


# Regressions: already work, with the flag off and on


@pytest.mark.usefixtures("either_mode")
async def test_all_optional_params_present():
    result = await parser.parse_object(RmDate, "пятого сентября тринадцать тридцать")
    assert result.substring == "пятого сентября тринадцать тридцать"
    assert result.obj.value == (5, 9, 1330)


@pytest.mark.usefixtures("either_mode")
async def test_optional_tail_absent():
    result = await parser.parse_object(RmDate, "пятого сентября")
    assert result.substring == "пятого сентября"
    assert result.obj.value == (5, 9, None)


@pytest.mark.usefixtures("either_mode")
async def test_only_required_param():
    result = await parser.parse_object(RmDate, "пятого")
    assert result.substring == "пятого"
    assert result.obj.value == (5, None, None)


@pytest.mark.usefixtures("either_mode")
async def test_found_inside_longer_sentence():
    result = await parser.parse_object(RmDate, "напомни пятого сентября пожалуйста")
    assert result.substring == "пятого сентября"
    assert result.obj.value == (5, 9, None)


@pytest.mark.usefixtures("either_mode")
async def test_trailing_text_after_last_claim_is_trimmed():
    result = await parser.parse_object(RmDate, "пятого сентября тринадцать тридцать blah")
    assert result.substring == "пятого сентября тринадцать тридцать"
    assert result.obj.value == (5, 9, 1330)


@pytest.mark.usefixtures("either_mode")
async def test_child_pattern_literal_is_kept():
    result = await parser.parse_object(RmDate, "пятого числа сентября")
    assert result.substring == "пятого числа сентября"
    assert result.obj.value == (5, 9, None)


@pytest.mark.usefixtures("either_mode")
async def test_cut_text_goes_to_pattern_literal():
    matches = await parser.match(Pattern("$day:RmDay( в $year:RmYear)?"), "пятого в тринадцать тридцать")
    assert matches[0].substring == "пятого в тринадцать тридцать"
    assert values(matches[0].parameters) == {"day": 5, "year": 1330}


@pytest.mark.usefixtures("either_mode")
async def test_cut_text_goes_to_neighbour_param():
    matches = await parser.match(Pattern("$n:RmNumber $text:NLString"), "пять купить молоко")
    assert matches[0].substring == "пять купить молоко"
    assert values(matches[0].parameters) == {"n": 5, "text": "купить молоко"}


@pytest.mark.usefixtures("either_mode")
async def test_greedy_param_followed_by_literal():
    matches = await parser.match(Pattern("$day:RmDay( $g:RmGreedyNumber)? год"), "пятого тринадцать год")
    assert matches[0].substring == "пятого тринадцать год"
    assert values(matches[0].parameters) == {"day": 5, "g": 13}


@pytest.mark.usefixtures("either_mode")
async def test_greedy_text_ends_where_next_param_fits():
    matches = await parser.match(Pattern("$text:RmGreedyText в $n:RmNumber"), "купить молоко в магазине в пять")
    assert matches[0].substring == "купить молоко в магазине в пять"
    assert values(matches[0].parameters) == {"text": "купить молоко в магазине", "n": 5}
