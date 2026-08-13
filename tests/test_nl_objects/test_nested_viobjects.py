from stark.core import Pattern
from stark.core.parsing import PatternParser
from stark.core.types import NLObject, NLWord
from stark.general.classproperty import classproperty

pattern_parser = PatternParser()


class FullName(NLObject):
    first: NLWord
    second: NLWord

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$first:NLWord $second:NLWord")


class ExtraParameterInAnnotation(NLObject):
    word1: NLWord
    word2: NLWord
    word3: NLWord

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$word1:NLWord $word2:NLWord")


async def test_nested_objects():
    pattern_parser.register_parameter_type(FullName)

    p = Pattern("$name:FullName")
    assert p
    assert pattern_parser._compile_pattern(p)

    m = await pattern_parser.match(p, "John Galt")
    assert m
    assert set(m[0].parameters.keys()) == {"name"}
    assert m[0].parameters["name"].first == NLWord("John")
    assert m[0].parameters["name"].second == NLWord("Galt")


async def test_extra_parameter_in_annotation():
    pattern_parser.register_parameter_type(ExtraParameterInAnnotation)

    p = Pattern("$name:ExtraParameterInAnnotation")
    assert p
    assert pattern_parser._compile_pattern(p)

    m = await pattern_parser.match(p, "John Galt")
    assert m
    assert set(m[0].parameters.keys()) == {"name"}
    assert m[0].parameters["name"].word1 == NLWord("John")
    assert m[0].parameters["name"].word2 == NLWord("Galt")
    assert not hasattr(m[0].parameters["name"], "word3")
