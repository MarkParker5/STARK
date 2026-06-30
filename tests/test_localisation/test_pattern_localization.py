from pathlib import Path

import pytest

from stark.core.parsing import ObjectParser, ParseError, PatternParser
from stark.core.patterns import Pattern
from stark.core.types import Object, Word
from stark.general.classproperty import classproperty
from stark.general.localisation import LocaleString, Localizer


def _create_strings_file(root: Path, lang: str, name: str, content: str):
    d = root / "strings" / lang
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.strings").write_text(content)


# --- Inline patterns dict ---


class GreetingLocalized(Object):
    value: str

    @classproperty
    def patterns(cls) -> dict[str, Pattern]:
        return {
            "base": Pattern("(hello|hi) $name:Word"),
            "en": Pattern("(hello|hi) $name:Word"),
            "ru": Pattern("(привет|здравствуй) $name:Word"),
        }


@pytest.fixture
def parser():
    p = PatternParser()
    p.register_parameter_type(GreetingLocalized)
    return p


async def test_inline_patterns_english(parser):
    result = await parser.parse_object(GreetingLocalized, LocaleString("hello world", "en"))
    assert result.obj.value == "hello world"


async def test_inline_patterns_russian(parser):
    result = await parser.parse_object(GreetingLocalized, LocaleString("привет мир", "ru"))
    assert result.obj.value == "привет мир"


async def test_inline_patterns_russian_no_match_english(parser):
    with pytest.raises(ParseError):
        await parser.parse_object(GreetingLocalized, LocaleString("привет мир", "en"))


async def test_inline_patterns_fallback_to_base(parser):
    result = await parser.parse_object(GreetingLocalized, LocaleString("hello world", "de"))
    assert result.obj.value == "hello world"


# --- @key syntax ---


@pytest.fixture
def localized_parser(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "recognizable", '"duration_units" = "hours|minutes|seconds";')
    _create_strings_file(tmp_path, "ru", "recognizable", '"duration_units" = "часов|минут|секунд";')
    _create_strings_file(tmp_path, "en", "localizable", '"duration_units" = "hours|minutes|seconds";')
    _create_strings_file(tmp_path, "ru", "localizable", '"duration_units" = "часов|минут|секунд";')

    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en", "ru"})
    localizer.load()

    p = PatternParser(localizer=localizer)

    class Duration(Object):
        value: str

        @classproperty
        def pattern(cls) -> Pattern:
            return Pattern("$n:Word (@duration_units)")

    p.register_parameter_type(Duration)
    return p, Duration


async def test_at_key_english(localized_parser):
    parser, Duration = localized_parser
    result = await parser.parse_object(Duration, LocaleString("5 hours", "en"))
    assert result.obj.value == "5 hours"


async def test_at_key_russian(localized_parser):
    parser, Duration = localized_parser
    result = await parser.parse_object(Duration, LocaleString("5 часов", "ru"))
    assert result.obj.value == "5 часов"


async def test_at_key_no_match_wrong_language(localized_parser):
    parser, Duration = localized_parser
    with pytest.raises(ParseError):
        await parser.parse_object(Duration, LocaleString("5 часов", "en"))


async def test_at_key_missing_localizer():
    with pytest.raises(ValueError, match="no Localizer"):
        parser = PatternParser()

        class BadType(Object):
            value: str

            @classproperty
            def pattern(cls) -> Pattern:
                return Pattern("@some_key")

        parser.register_parameter_type(BadType)


async def test_at_key_missing_key(tmp_path, monkeypatch):
    _create_strings_file(tmp_path, "en", "recognizable", '"other_key" = "value";')
    _create_strings_file(tmp_path, "en", "localizable", '"other_key" = "value";')
    monkeypatch.chdir(tmp_path)

    localizer = Localizer(languages={"en"})
    localizer.load()

    with pytest.warns(RuntimeWarning, match="nonexistent_key.*not found.*Added.*Translation needed"):
        parser = PatternParser(localizer=localizer)

        class BadType2(Object):
            value: str

            @classproperty
            def pattern(cls) -> Pattern:
                return Pattern("@nonexistent_key")

        parser.register_parameter_type(BadType2)


# --- did_parse receives language_code ---


class LangAwareType(Object):
    value: str
    received_language_code: str = ""

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    async def did_parse(self, from_string: str) -> str:
        self.received_language_code = from_string.language_code
        self.value = from_string
        return from_string


async def test_did_parse_receives_language_code():
    parser = PatternParser()
    parser.register_parameter_type(LangAwareType)

    result = await parser.parse_object(LangAwareType, LocaleString("test input", "ru"))
    assert result.obj.received_language_code == "ru"

    result2 = await parser.parse_object(LangAwareType, LocaleString("other input", "de"))
    assert result2.obj.received_language_code == "de"


# --- Command-level localized patterns ---


async def test_command_get_pattern():
    from stark.core.command import Command

    pattern_en = Pattern("hello $name:Word")
    pattern_ru = Pattern("привет $name:Word")

    cmd = Command(
        name="test",
        patterns={"base": pattern_en, "en": pattern_en, "ru": pattern_ru},
        runner=lambda: None,
    )

    assert cmd.get_pattern("en") is pattern_en
    assert cmd.get_pattern("ru") is pattern_ru
    assert cmd.get_pattern("de") is pattern_en  # fallback to base


async def test_commands_manager_localized_patterns():
    from stark.core.command import Response
    from stark.core.commands_manager import CommandsManager

    manager = CommandsManager()

    @manager.new({"en": "hello $name:Word", "ru": "привет $name:Word"})
    async def greet(name: Word) -> Response:
        return Response(f"Hello {name}!")

    assert greet.patterns is not None
    assert "en" in greet.patterns
    assert "ru" in greet.patterns
    assert "base" in greet.patterns
    assert greet.get_pattern("en")._origin == "hello $name:Word"
    assert greet.get_pattern("ru")._origin == "привет $name:Word"


# --- ObjectParser.get_patterns ---


class ProgrammaticType(Object):
    value: str


class ProgrammaticParser(ObjectParser):
    async def did_parse(self, obj: Object, from_string: str) -> str:
        obj.value = from_string
        return from_string

    @property
    def patterns(self):
        return {
            "base": Pattern("(hello|hi) **"),
            "ru": Pattern("(привет|здравствуй) **"),
        }


async def test_parser_get_patterns():
    parser = PatternParser()
    parser.register_parameter_type(ProgrammaticType, parser=ProgrammaticParser())

    result = await parser.parse_object(ProgrammaticType, LocaleString("hello world", "en"))
    assert result.obj.value == "hello world"

    result = await parser.parse_object(ProgrammaticType, LocaleString("привет мир", "ru"))
    assert result.obj.value == "привет мир"

    with pytest.raises(ParseError):
        await parser.parse_object(ProgrammaticType, LocaleString("привет мир", "en"))


async def test_commands_manager_single_pattern():
    from stark.core.command import Response
    from stark.core.commands_manager import CommandsManager

    manager = CommandsManager()

    @manager.new("hello $name:Word")
    async def greet(name: Word) -> Response:
        return Response(f"Hello {name}!")

    assert greet.patterns == {"base": greet.get_pattern("base")}
    assert greet.get_pattern("base")._origin == "hello $name:Word"
