# (WIP) Localizing Responses

Response localization allows your voice assistant to reply in the user's language. This page is reserved for the upcoming response localization feature.

## Foundation

The Localizer infrastructure is already in place. String bundles support two categories:

- **recognizable** — for input matching (patterns, parsing). See [Localizing Parsing](localizing-parsing.md).
- **localizable** — for output formatting (responses). This is the category that response localization will use.

You can already access localizable strings via the Localizer:

```python
localizer.get_localizable("greeting_response", language_code="ru")
# Returns the Russian greeting string from strings/ru/localizable.strings
```

## What's Coming

- Response objects will carry `language_code` for automatic string resolution
- Command runners will be able to access the Localizer via dependency injection
- Template formatting with `localizable.strings` keys

Stay tuned. In the meantime, you can manually use `localizer.get_localizable()` in your command runners to format responses in the correct language.
