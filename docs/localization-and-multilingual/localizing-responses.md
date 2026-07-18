# Localizing Responses

Response localization allows your assistant to reply in the user's language. The key idea: store a translation key with format arguments, so the translated template is resolved first, then the arguments are injected into it.

```python
# Without localization — hardcoded language:
Response(f"Hello, {name}!")
# gives "Hello, Mark!"

# With localization — deferred:
Response(LocalizableString("greeting", "fr", name=str(name)))
# Localizer resolves "greeting" for "fr" → "Bonjour, {name}!"
# Then formats → "Bonjour, Mark!"
```

This matters because argument positions and surrounding text differ between languages, you can't just translate a pre-formatted string.

## `LocalizableString`

`LocalizableString` stores a key, a language code, and format arguments. At response time, `Localizer.localize()` looks up the key in `localizable.strings` for the given language, then calls `.format(**arguments)` on the resolved template.

```python
from stark.general.localisation import LocalizableString

LocalizableString("greeting", "it", name="Mark")
# .string = "greeting"         — the key
# .language_code = "it"        — which translation to use
# .arguments = {"name": "Mark"} — injected after translation

LocalizableString("greeting", "es", name="Mark")
# same key, different language — Localizer resolves "¡Hola, Mark!" instead
```

If the key is not found, `localize()` emits a `RuntimeWarning` and falls back to the raw key string.

## Using in Commands

`Response.text` and `Response.voice` accept both plain `str` and `LocalizableString`.

To know which language to respond in, annotate any parameter with `LanguageCode`, the framework injects the language of the matched substring automatically via dependency injection. The parameter name doesn't matter, only the type annotation:

```python
from stark.general.localisation.language_code import LanguageCode

@manager.new({
    "base": "hello $name:Word",
    "es": "hola $name:Word",
})
async def greet(name: Word, lang: LanguageCode) -> Response:
    return Response(LocalizableString("greeting_response", lang, name=str(name)))
```

When the user says "hola mundo", the pattern matches via the Spanish pattern, so `lang` is `"es"`. When they say "hello world", `lang` is `"en"`. For mixed-language input with `TranscriptionString`, the language is the majority language of the matched substring's words.

## Resolving at Response Time

The core framework stores `LocalizableString` as-is in the `Response` object. Resolution happens at the delegate level, where the `Localizer` is available. `VoiceAssistant` provided by STARK already does that automatically under the hood.

```python
# In your custom delegate / response handler:
if isinstance(response.text, LocalizableString):
    text = localizer.localize(response.text)
else:
    text = response.text
```

This keeps the core framework decoupled from any specific output target, the same `Response` can be rendered differently by a voice assistant (TTS), a chat UI, or a logging system.

## Fallback Behavior

If the key is not found in `localizable.strings` for the requested language, `localize()` falls back to:

1. The `base` language strings
2. The raw key string itself (with a `RuntimeWarning`)

## String Bundles

Response strings use the same `.strings` bundle format and directory structure as pattern localization. The `localizable.strings` files are the output counterpart to `recognizable.strings`:

```
strings/
  en/
    localizable.strings    ← response strings
    recognizable.strings   ← pattern strings
  cs/
    localizable.strings
    recognizable.strings
  pl/
    localizable.strings
    recognizable.strings
```

See [Localizing Parsing](localizing-parsing.md) for the full bundle format reference.

## Formatting Complex Values with PyICU

For formatting locale-sensitive values like numbers, dates, units, and currencies in responses, [PyICU](https://pypi.org/project/PyICU/) is a great companion library. It wraps the ICU C++ library (the same engine behind iOS/Swift's `Foundation` formatting) and provides ready-made locale-aware formatting for:

- **Numbers**: decimal, percent, currency, and spelled-out (e.g., `"five"`, `"п'ять"`, `"pięć"`)
- **Dates/Times**: locale-specific patterns, relative dates (`"yesterday"`, `"in 2 days"`)
- **Units**: `"5 kilometers"`, `"3 lbs"`, `"2 hours"` with localized names
- **Messages**: pluralization and gender rules (`"{num, plural, one {# item} other {# items}}"`)

PyICU is not a dependency of S.T.A.R.K, use it alongside when you need locale-aware value formatting in your responses. See [Command Response](../command-response.md#formatting-locale-sensitive-values-with-pyicu) for more examples of response building with formatted values.
