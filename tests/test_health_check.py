import warnings

import pytest

from stark.core.command import Command
from stark.core.health_check import health_check
from stark.core.parsing import Pattern, PatternParser
from stark.core.types.object import Object
from stark.core.types.word import Word
from stark.general.classproperty import classproperty


class DummyType(Object):
    foo: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("dummy $foo:Word")


class DummyWrapper(Object):
    dummy: DummyType

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("dummy $dummy:DummyType")


def dummy_runner(foo: Word) -> None:
    pass


def dummy_runner_missing() -> None:
    pass


def dummy_runner_extra(foo: Word, bar: Word) -> None:
    pass


def test_health_check_success():
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    command = Command("dummy", DummyType.pattern, dummy_runner)
    health_check(parser, [command])  # Should not raise


def test_health_check_missing_param():
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    command = Command("dummy", DummyType.pattern, dummy_runner_missing)
    with pytest.raises(AssertionError, match="function missing parameters"):
        health_check(parser, [command])


def test_health_check_unknown_param_type_in_command():
    parser = PatternParser()
    # forgot to register DummyType
    command = Command("dummy", Pattern("$dummy:DummyType"), dummy_runner)
    with pytest.raises(AssertionError, match="Unknown parameter type"):
        health_check(parser, [command])


def test_health_check_unknown_param_type_in_type():
    parser = PatternParser()
    # forgot to register DummyType
    parser.register_parameter_type(DummyWrapper)
    with pytest.raises(AssertionError, match="Unknown parameter type"):
        health_check(parser, [])


def test_health_check_duplicate_param_type():
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    with pytest.raises(AssertionError, match="Duplicate parameter type"):
        parser.register_parameter_type(DummyType)
        health_check(parser, [])


def test_health_check_unused_type_warns():
    parser = PatternParser()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        health_check(parser, [])
        assert any("is not used in any pattern" in str(warn.message) for warn in w)
