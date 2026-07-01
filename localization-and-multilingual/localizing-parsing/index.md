# Localizing Parsing

S.T.A.R.K supports multi-language pattern matching and parsing out of the box. This page covers how to localize the input recognition side: patterns, parameter types, and `did_parse` logic. For response localization (output), see [Localizing Responses](https://stark.markparker.me/localization-and-multilingual/localizing-responses/index.md).

## Core Concepts

There are three places where localization applies to input processing:

1. **Command patterns**: how a command is triggered (e.g., `"set timer"` vs german `"stelle einen Timer"`)
1. **Object type patterns**: how a parameter type is recognized (e.g., `Duration` matching `"hours"` vs italian `"ore"`)
1. **`did_parse` logic**: programmatic parsing that may behave differently per language (e.g., parsing `"one"` vs spanish `"uno"` into a number)

Language metadata flows through the entire pipeline on the input string itself via `LocaleString`, a `str` subclass that carries a `language_code` attribute.

## `LocaleString`

`LocaleString` is a `str` subclass that carries language metadata. It behaves exactly like a regular string, equality, hashing, `in`, regex, `len`, iteration all work unchanged. All str methods that return a new string (`replace`, `strip`, slicing, `split`, etc.) are overridden to preserve the `language_code`. Note that third-party libraries and CPython C-level functions (e.g., `re.sub`, spacy) may reconstruct strings internally, bypassing Python-level overrides, in these cases metadata will be lost. Use `str(locale_string)` when passing to such APIs, and `locale_string._with(result)` to re-attach metadata to the output.

```python
from stark.general.localisation import LocaleString

s = LocaleString("hello world", "en")
s.language_code  # "en"
s[6:]            # LocaleString("world", "en") — metadata preserved
s.replace("hello", "hi")  # LocaleString("hi world", "en")
```

## Language Codes and `"base"`

The default language code is `"base"`. When no language is specified, all patterns and parsing use the `"base"` variant. This is the fallback for any language that doesn't have a dedicated pattern.

All language codes are typed as `LanguageCode`, a `Literal` union of `"base"` and ISO 639-1 codes (e.g., `"en"`, `"ru"`, `"de"`).

Your app provides the language code via `LocaleString`:

```python
from stark.general.localisation import LocaleString

await context.process_string(LocaleString("set timer for five minutes", "en"))
await context.process_string(LocaleString("ustaw minutnik na pięć minut", "pl"))

# Plain str works too — defaults to "base"
await context.process_string("set timer for five minutes")
```

Language identification is not part of S.T.A.R.K's core, it's the app's responsibility. In a voice assistant setup, the STT engine typically provides the language code alongside the recognized text.

## Localizing Patterns

### Inline `patterns` Dict

The simplest approach. Override the `patterns` classproperty on your Object type to return per-language Pattern instances:

```python
class Duration(Object):
    value: str

    @classproperty
    def patterns(cls) -> dict[str, Pattern]:
        return {
            "base": Pattern("$n:Word (hours|minutes|seconds)"),
            "de": Pattern("$n:Word (Stunden|Minuten|Sekunden)"),
            "it": Pattern("$n:Word (ore|minuti|secondi)"),
            "es": Pattern("$n:Word (horas|minutos|segundos)"),
            "fr": Pattern("$n:Word (heures|minutes|secondes)"),
        }
```

When matching with `language_code="pl"`, S.T.A.R.K uses the `"pl"` pattern; with `"it"` or `"es"`, the Italian or Spanish one. For any other language code, it falls back to `"base"`.

The single `pattern` classproperty still works, if you don't override `patterns`, it defaults to `{"base": cls.pattern}`. So existing types work unchanged.

> **Note on dict ordering:** If you provide a `dict[str, str]` to `@manager.new` without a `"base"` key, the first entry by iteration order is used as `"base"`. Python dicts preserve insertion order, but this is worth being explicit about, always include a `"base"` key to avoid ambiguity.

### `@key` Syntax with String Bundles

For production apps with many languages, embed localization keys in your pattern strings. The `PatternParser` resolves them at compile time from the `Localizer`:

```python
class Duration(Object):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("$n:Word (@duration_units)")
```

The `@duration_units` key is looked up in the Localizer's recognizable string files for the active language. This requires setting up a Localizer (see [String Bundles](#string-bundles) below).

Keys must start with a letter or underscore, followed by letters, digits, or underscores, standard identifier rules (e.g., `@duration_units`, `@_private_key`, `@greeting2`).

`@key` references are validated at type registration time and during health checks, if a key is missing from all loaded languages, you get an error at startup, not at runtime when a user triggers the command.

## Localizing Commands

Commands support the same per-language patterns. Pass a `dict[str, str]` instead of a single string to `@manager.new`:

```python
@manager.new({
    "base": "set timer for $t:Duration",
    "de": "stell einen Timer für $t:Duration",
    "fr": "mets un minuteur pour $t:Duration",
    "uk": "встанови таймер на $t:Duration",
})
async def set_timer(t: Duration) -> Response:
    ...
```

For a single-language command, just pass a string as before, it becomes the `"base"` pattern.

The `@key` syntax works for commands as well:

```python
@manager.new('@clock_timer_set_command')
async def set_timer(t: Duration) -> Response:
    ...
```

## Using ObjectParser for Localized Parsing

`ObjectParser` is the recommended approach for types that need localized `did_parse` logic, localized programmatic patterns, or both. Every `ObjectParser` instance automatically holds a reference to the `Localizer` (injected by `PatternParser` during type registration), no manual `__init__` wiring needed.

### Localized `did_parse`

The `from_string` parameter in `did_parse` is a `LocaleString`, same as the regular string, but provides `from_string.language_code: LanguageCode` for language-specific parsing logic.

With `ObjectParser`, use `self.localizer` for localized lookup tables:

```python
class NLNumberParser(ObjectParser):
    async def did_parse(self, obj: Object, from_string: LocaleString) -> str:
        words_one = self.localizer.get_recognizable("words_one", from_string.language_code)
        ...
```

For simple types that don't self.localizer or any other features of `ObjectParser`, you can still use `did_parse` directly on the Object:

```python
class NLNumber(Object):
    value: float

    async def did_parse(self, from_string: LocaleString) -> str:
        match from_string.language_code:
            case "pl":
                self.value = parse_polish_number(from_string)
            case "cs":
                self.value = parse_czech_number(from_string)
            case _:
                self.value = parse_english_number(from_string)
        return from_string
```

More details about parsing of custom types at [ObjectParser](https://stark.markparker.me/patterns/#defining-custom-object-types)

### Programmatic Patterns

For types that generate patterns at runtime (e.g., from a database or API), override the `patterns` property on your `ObjectParser`. It takes priority over the Object's `patterns` classproperty:

```python
class PlaylistParser(ObjectParser):
    _cache: dict[str, Pattern] | None = None

    @property
    def patterns(self) -> dict[str, Pattern] | None:
        if self._cache:
            return self._cache
        playlists = fetch_playlists()  # your data source
        play_word = self.localizer.get_recognizable("play", "base") or "play"
        self._cache = {"base": Pattern(f"({play_word}) ({"|".join(playlists)})")}
        return self._cache
```

Pattern resolution order: `parser.patterns[language_code]` > `object_type.patterns[language_code]` > fallback to `"base"` key.

Cache invalidation is the extension's responsibility, the Localizer provides stable strings, but dynamic data (like playlist names) may change.

## String Bundles

String bundles are files that store localized strings. S.T.A.R.K uses a simple key-value format (`.strings` files):

### File Format

```text
/* optional comment */
"key" = "value";

"greeting" = "hello|hi|hey";
"duration_units" = "hours|minutes|seconds";
```

### Directory Structure

```text
strings/
  base/
    localizable.strings
    recognizable.strings
  en/
    localizable.strings
    recognizable.strings
  de/
    localizable.strings
    recognizable.strings
  fr/
    localizable.strings
    recognizable.strings
  it/
    localizable.strings
    recognizable.strings
```

- **recognizable**: strings used for input matching (patterns, parsing)
- **localizable**: strings used for output formatting (responses), see [Localizing Responses](https://stark.markparker.me/localization-and-multilingual/localizing-responses/index.md)
- **base/**: fallback strings used when a key is missing for a specific language

### Setting Up the Localizer

```python
from stark.general.localisation import Localizer

localizer = Localizer(languages={"en", "de", "fr", "it"}, base_language="en")
localizer.load()  # discovers and reads .strings files
```

Only languages in the `languages` set are loaded, the rest are ignored even if files exist on disk. The `base` directory is always loaded.

`load()` automatically creates missing `strings/{lang}/` directories and empty `.strings` files for all configured languages. If a pattern uses an `@key` that doesn't exist in any loaded language, `health_check` automatically adds the key to the base `recognizable.strings` with its own name as the default value and a warning is emitted. This means you can start using `@key` syntax immediately, the files and entries are created for you, and you fill in translations later.

Pass the Localizer when creating `CommandsContext`:

```python
context = CommandsContext(
    task_group=main_task_group,
    commands_manager=manager,
    localizer=localizer,
)
```

The Localizer is automatically propagated to `PatternParser` and all `ObjectParser` instances registered on it.

For mixed-language input with per-word language metadata, see [Multilanguage Input](https://stark.markparker.me/localization-and-multilingual/multilanguage-input/index.md).
