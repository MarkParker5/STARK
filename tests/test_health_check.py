import warnings

import pytest

from stark.core.command import Command
from stark.core.health_check import health_check
from stark.core.parsing import Pattern, PatternParser
from stark.core.types.object import Object
from stark.core.types.word import Word
from stark.general.classproperty import classproperty


class DummyType(Object):
    value: Word

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("dummy $value:Word")


class DummyWrapper(Object):
    dummy: DummyType

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("dummy $dummy:DummyType")


def dummy_runner(value: Word) -> None:
    pass


def dummy_runner_missing() -> None:
    pass


def dummy_runner_extra(value: Word, extra: Word) -> None:
    pass


def test_health_check_success():
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    command = Command("dummy", {"base": DummyType.pattern}, dummy_runner)
    health_check(parser, [command])  # Should not raise


def test_health_check_missing_param():
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    command = Command("dummy", {"base": DummyType.pattern}, dummy_runner_missing)
    with pytest.raises(AssertionError, match="function missing parameters"):
        health_check(parser, [command])


def test_health_check_unknown_param_type_in_command():
    parser = PatternParser()
    # forgot to register DummyType
    command = Command("dummy", {"base": Pattern("$dummy:DummyType")}, dummy_runner)
    with pytest.raises(AssertionError, match="Unknown parameter type"):
        health_check(parser, [command])


def test_health_check_unknown_param_type_in_type():
    # Auto-discovery scans _all_subclasses(Object) by name. A type referenced by
    # a name that has no matching Object subclass is silently skipped during
    # registration and caught by health_check.
    class TypeThatDoesNotExist(Object):
        pass

    class GhostWrapper(Object):
        x: TypeThatDoesNotExist  # gets auto discovered

        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("$x:TypeThatDoesNotExistTypo")  # typo here

    parser = PatternParser()
    parser.register_parameter_type(GhostWrapper)
    assert "TypeThatDoesNotExist" not in parser.parameter_types_by_name
    with pytest.raises(AssertionError, match="Unknown parameter type"):
        health_check(parser, [])


def test_health_check_duplicate_param_type():
    # register_parameter_type is idempotent — duplicate calls are silently ignored.
    parser = PatternParser()
    parser.register_parameter_type(DummyType)
    parser.register_parameter_type(DummyType)  # no-op, must not raise
    assert list(parser.parameter_types_by_name).count("DummyType") == 1
    health_check(parser, [])


def test_health_check_unused_type_warns():
    parser = PatternParser()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        health_check(parser, [])
        assert any("is not used in any pattern" in str(warn.message) for warn in w)
