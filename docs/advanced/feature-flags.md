# Feature Flags

S.T.A.R.K uses environment variables to enable or disable experimental and optional features.

## Available Flags

| Flag | Default | Complexity overhead | Description |
|------|---------|-------------------|-------------|
| `STARK_ENABLE_VOICE_CLI` | `0` | None | Print voice input/output in terminal. See [Voice Assistant](../running/voice-assistant.md). |
| `STARK_ENABLE_MULTILANG_MATRIX` | `1` | O(T × C × P), multiplies matching cost by T tracks | Match input against all alternative language tracks concurrently. See [Multilanguage Input](../localization-and-multilingual/multilanguage-input.md). |
| `STARK_TYPE_NO_REQUIRED_VALUE` | `0` | None | Disable the assertion that an `Object`'s `value` must be set (non-`None`) by the time `did_parse` returns. Use for object types where `value` has no meaning, e.g. all data lives in typed sub-parameters. See [`value` Property](../core-concepts/patterns.md#the-value-property). |

## Setting Flags

Set via environment variables before running your app:

```bash
STARK_ENABLE_VOICE_CLI=1 python -m your_app
```
