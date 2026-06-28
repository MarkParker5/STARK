# Feature Flags

S.T.A.R.K uses environment variables to enable or disable experimental and optional features.

## Available Flags

| Flag | Default | Complexity overhead | Description |
|------|---------|-------------------|-------------|
| `STARK_ENABLE_VOICE_CLI` | `0` | None | Print voice input/output in terminal. See [Voice Assistant](../voice-assistant.md). |
| `STARK_ENABLE_MULTILANG_MATRIX` | `1` | O(T × C × P) — multiplies matching cost by T tracks | Match input against all alternative language tracks concurrently. See [Multilanguage Input](../localization-and-multilingual/multilanguage-input.md). |

## Setting Flags

Set via environment variables before running your app:

```bash
STARK_ENABLE_VOICE_CLI=1 python -m your_app
```
