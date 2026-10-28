# Feature Flags

S.T.A.R.K uses environment variables to enable or disable experimental and optional features.

## Available Flags

| Flag | Default | Complexity overhead | Description |
|------|---------|-------------------|-------------|
| `STARK_ENABLE_VOICE_CLI` | `0` | None | Print voice input/output in terminal. See [Voice Assistant](../running/voice-assistant.md). |
| `STARK_ENABLE_MULTILANG_MATRIX` | `1` | O(T × C × P), multiplies matching cost by T tracks | Match input against all alternative language tracks concurrently. See [Multilanguage Input](../localization-and-multilingual/multilanguage-input.md). |
| `STARK_TYPE_NO_REQUIRED_VALUE` | `0` | None | Disable the assertion that an `NLObject`'s `value` must be set (non-`None`) by the time `did_parse` returns. Use for NLObject types where `value` has no meaning, e.g. all data lives in typed sub-parameters. See [`value` Property](../core-concepts/patterns.md#the-value-property). |
| `STARK_STABLE_REMATCH` | `0` | Up to 3 extra re-matches for a parameter whose claim can't be placed on its own | Experimental. When a parameter's `did_parse` claims only part of the text its pattern captured and no literal or other parameter can take the rest, keep that rest in the parameter's place in the match instead of dropping the parameter. The parameter's value and substring stay what `did_parse` returned. Also escapes regex characters in claimed text. See [Custom Parser Class Example](../core-concepts/patterns.md#custom-parser-class-example). |

## Setting Flags

Set via environment variables before running your app:

```bash
STARK_ENABLE_VOICE_CLI=1 python -m your_app
```
