import pytest

from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import NLObject
from stark.general.classproperty import classproperty
from stark.general.feature_flags import FeatureFlag


class NoValue(NLObject):
    """Never sets `self.value` and doesn't call `super().did_parse`."""

    @classproperty
    def pattern(cls):
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        return from_string


class StaticValue(NLObject):
    """Sets a static value at declaration time; `did_parse` must not override it."""

    value = "static"

    @classproperty
    def pattern(cls):
        return Pattern("**")


async def test_default_did_parse_falls_back_to_substring():
    parser = PatternParser()
    parser.register_parameter_type(StaticValue)
    match = await parser.parse_object(StaticValue, "hello world")
    assert match.obj.value == "static"


async def test_static_value_is_not_overridden_by_default_did_parse():
    obj = StaticValue()
    substring = await obj.did_parse("hello world")
    assert obj.value == "static"
    assert substring == "hello world"


async def test_default_did_parse_sets_value_when_unset():
    class Plain(NLObject):
        @classproperty
        def pattern(cls):
            return Pattern("**")

    parser = PatternParser()
    parser.register_parameter_type(Plain)
    match = await parser.parse_object(Plain, "hello world")
    assert match.obj.value == "hello world"


async def test_missing_value_raises_by_default():
    parser = PatternParser()
    parser.register_parameter_type(NoValue)
    with pytest.raises(AssertionError):
        await parser.parse_object(NoValue, "hello world")


async def test_missing_value_allowed_with_feature_flag(monkeypatch):
    monkeypatch.setenv(FeatureFlag.TYPE_NO_REQUIRED_VALUE.value, "1")
    parser = PatternParser()
    parser.register_parameter_type(NoValue)
    match = await parser.parse_object(NoValue, "hello world")
    assert match.obj.value is None
